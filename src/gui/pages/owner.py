import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from pathlib import Path

from src.core.keystore import ensure_user_keys, load_user_keys
from src.blockchain.local_chain import LocalChain
from src.services.uploader import encrypt_sign_upload
from src.services.sharing import approve_and_share_key
from src.storage.cloud import get_meta
from ..widgets import (
    Section, LabeledEntry, StatusBar, alert_error, ScrollableFrame, apply_treeview_style
)

# Use Path (not str) for KEYS_DIR
KEYS_DIR: Path = Path("data/keys")


# ---------- cache AES keys so sharing never needs pasting ----------
def _owner_aes_store(owner_id: str) -> Path:
    p = KEYS_DIR / owner_id / "_aes_keys.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("{}", encoding="utf-8")
    return p

def _load_owner_keys(oid: str) -> dict:
    try:
        return json.loads(_owner_aes_store(oid).read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_owner_key(oid: str, fid: str, key: bytes):
    data = _load_owner_keys(oid)
    data[fid] = key.hex()
    _owner_aes_store(oid).write_text(json.dumps(data, indent=2), encoding="utf-8")


class OwnerPage(ttk.Frame):
    """
    Full-screen Owner workflow:
      - Encrypt & Upload a file
      - View pending access requests for your files
      - Share key to a selected request (uses cached AES key; if missing, prompt once and cache)
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        apply_treeview_style(self)

        self.owner_id = tk.StringVar(value="owner1")
        self.file_path = tk.StringVar(value="")
        self.file_info = tk.StringVar(value="No file selected")

        # full-page scroll container
        sc = ScrollableFrame(self)
        sc.pack(fill="both", expand=True)
        root = sc.body

        # header
        head = ttk.Frame(root); head.pack(fill="x", pady=(16, 8))
        ttk.Button(head, text="← Back", command=lambda: controller.show("HomePage")).pack(side="left", padx=8)
        ttk.Label(head, text="Upload & Share (Owner)", style="Header.TLabel").pack(side="left", padx=8)

        sub = ttk.Label(
            root,
            text="Encrypt, sign, and upload a file; then approve requests and share the AES key securely.",
            style="Help.TLabel"
        )
        sub.configure(wraplength=860, justify="left")
        sub.pack(anchor="w", padx=12, pady=(0, 12))

        # owner
        who = Section(root, "Owner"); who.pack(fill="x", padx=12, pady=8)
        LabeledEntry(
            who, "Owner ID", self.owner_id,
            help_text="Your signing and RSA keys are stored under this ID."
        ).grid(sticky="we", padx=8, pady=8)

        # upload
        up = Section(root, "Encrypt & Upload"); up.pack(fill="x", padx=12, pady=8)
        row = ttk.Frame(up); row.pack(fill="x", padx=8, pady=8)
        ttk.Entry(row, textvariable=self.file_path).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=self._browse).pack(side="left", padx=8)
        ttk.Label(up, textvariable=self.file_info, style="Help.TLabel").pack(anchor="w", padx=8)

        ttk.Button(root, text="Encrypt, Sign & Upload", command=self._upload, style="CTA.TButton").pack(
            padx=12, pady=12, anchor="w"
        )

        # result
        out = Section(root, "Result (latest upload)"); out.pack(fill="both", expand=True, padx=12, pady=8)
        self.out = tk.Text(out, height=8, wrap="word")
        self.out.pack(fill="both", expand=True, padx=8, pady=8)

        # requests
        req = Section(root, "Pending Access Requests"); req.pack(fill="both", expand=True, padx=12, pady=8)
        wrap = ttk.Frame(req); wrap.pack(fill="both", expand=True, padx=8, pady=8)

        cols = ("file_id", "filename", "requester_id")
        self.tv = ttk.Treeview(wrap, columns=cols, show="headings", height=12, style="SS.Treeview")
        self.tv.heading("file_id", text="file_id")
        self.tv.heading("filename", text="filename")
        self.tv.heading("requester_id", text="requester_id")
        self.tv.column("file_id", width=420, stretch=True)
        self.tv.column("filename", width=280, stretch=True)
        self.tv.column("requester_id", width=200, stretch=True)

        vbar = ttk.Scrollbar(wrap, orient="vertical", command=self.tv.yview)
        hbar = ttk.Scrollbar(wrap, orient="horizontal", command=self.tv.xview)
        self.tv.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

        wrap.columnconfigure(0, weight=1)
        wrap.rowconfigure(0, weight=1)
        self.tv.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")

        btns = ttk.Frame(req); btns.pack(fill="x", padx=8, pady=(4, 8))
        ttk.Button(btns, text="Refresh Requests", command=self._refresh_requests).pack(side="left")
        ttk.Button(btns, text="Share Key with Selected Request", command=self._share_selected).pack(side="left", padx=8)

        self.status = StatusBar(root); self.status.pack(fill="x")

        # Ensure keys exist for this owner
        ensure_user_keys(KEYS_DIR, self.owner_id.get())
        self._refresh_requests()

    # actions
    def _browse(self):
        p = filedialog.askopenfilename()
        if p:
            self.file_path.set(p)
            try:
                size = os.path.getsize(p)
                self.file_info.set(f"Selected: {os.path.basename(p)} ({size} bytes)")
            except Exception:
                self.file_info.set(f"Selected: {os.path.basename(p)}")

    def _upload(self):
        path = self.file_path.get().strip()
        if not path or not os.path.exists(path):
            alert_error("Choose a valid file first.")
            return

        kp = ensure_user_keys(KEYS_DIR, self.owner_id.get())
        ecdsa_priv, _, _, _ = load_user_keys(kp)
        chain = LocalChain()
        result = encrypt_sign_upload(ecdsa_priv, self.owner_id.get(), path, chain=chain)

        # Cache AES key locally so future shares don't need manual entry
        _save_owner_key(self.owner_id.get(), result["file_id"], result["aes_key"])

        self.out.delete("1.0", "end")
        self.out.insert("end", "Upload complete.\n\n")
        self.out.insert("end", f"File ID: {result['file_id']}\n")
        self.out.insert("end", f"AES key (hex): {result['aes_key'].hex()}\n")
        self.out.insert("end", f"Nonce (hex): {result['nonce'].hex()}\n")
        self.out.insert("end", f"Signature (hex): {result['signature'].hex()}\n")
        self.out.insert("end", f"Ciphertext size: {result['size']} bytes\n")

        self.status.info("Encrypted, signed, and uploaded. When requests appear, select one and click Share Key.")

    def _refresh_requests(self):
        self.tv.delete(*self.tv.get_children())
        chain = LocalChain(); evs = chain.get_events()
        owner = self.owner_id.get().strip()

        uploads = {
            e["event"]["file_id"]: e["event"]
            for e in evs if e["event"].get("type") == "UPLOAD" and e["event"].get("owner_id") == owner
        }
        reqs = [
            e["event"] for e in evs
            if e["event"].get("type") == "ACCESS_REQUEST" and e["event"].get("file_id") in uploads
        ]
        for r in reqs:
            fid = r["file_id"]; meta = get_meta(fid) or {}
            self.tv.insert("", "end", values=(fid, meta.get("filename", "?"), r.get("requester_id")))
        self.status.info(f"Found {len(reqs)} request(s) for your files.")

    def _prompt_for_aes_key(self, file_id: str) -> bytes | None:
        """
        Ask the owner for the AES key (hex) if it isn't cached.
        Validate length (16/24/32 bytes) and cache it on success.
        """
        prompt = (
            "The AES key for this file isn't cached on this machine.\n"
            "Paste the AES key (hex) that was shown when you uploaded this file.\n\n"
            "Accepted lengths: 16, 24, or 32 bytes (32, 48, or 64 hex chars)."
        )
        key_hex = simpledialog.askstring("Enter AES key (hex)", prompt, parent=self)
        if not key_hex:
            return None
        key_hex = key_hex.strip()
        try:
            key = bytes.fromhex(key_hex)
        except Exception:
            alert_error("Invalid hex. Please paste the AES key exactly as shown during upload.")
            return None
        if len(key) not in (16, 24, 32):
            alert_error("AES key length must be 16, 24, or 32 bytes.")
            return None
        # Cache for future use
        _save_owner_key(self.owner_id.get(), file_id, key)
        return key

    def _share_selected(self):
        sel = self.tv.selection()
        if not sel:
            alert_error("Select a request row first.")
            return

        fid, _, requester_id = self.tv.item(sel[0], "values")

        # Load owner's cached AES key for this file (or prompt once if missing)
        store = _load_owner_keys(self.owner_id.get())
        key_hex = store.get(fid)
        if key_hex:
            aes_key = bytes.fromhex(key_hex)
        else:
            aes_key = self._prompt_for_aes_key(fid)
            if aes_key is None:
                self.status.warn("Share canceled.")
                return

        # Load requester's RSA public key (ensure they have keys)
        _, _, _, req_rsa_pub = load_user_keys(ensure_user_keys(KEYS_DIR, requester_id))

        chain = LocalChain()
        approve_and_share_key(chain, self.owner_id.get(), fid, requester_id, req_rsa_pub, aes_key)

        self.status.info(f"Shared key for file {fid} with requester {requester_id}.")
