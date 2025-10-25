import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from src.core.keystore import ensure_user_keys, load_user_keys
from src.blockchain.local_chain import LocalChain
from src.services.sharing import create_access_request
from src.services.verifier import requester_download_and_verify
from src.storage.cloud import list_files, get_meta
from ..widgets import (
    Section, LabeledEntry, StatusBar, alert_error, ScrollableFrame, apply_treeview_style
)

# Use Path (not str) for KEYS_DIR
KEYS_DIR: Path = Path("data/keys")


class RequesterPage(ttk.Frame):
    """
    Full-screen Requester workflow:
      - Browse cloud files and request access
      - See files shared to this requester and download/decrypt/verify
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        apply_treeview_style(self)

        self.requester_id = tk.StringVar(value="requester1")
        self.owner_id = tk.StringVar(value="owner1")

        sc = ScrollableFrame(self)
        sc.pack(fill="both", expand=True)
        root = sc.body

        head = ttk.Frame(root); head.pack(fill="x", pady=(16, 8))
        ttk.Button(head, text="← Back", command=lambda: controller.show("HomePage")).pack(side="left", padx=8)
        ttk.Label(head, text="Request & Download (Requester)", style="Header.TLabel").pack(side="left", padx=8)

        sub = ttk.Label(root, text="Request access to files and download them once the owner shares the key.",
                        style="Help.TLabel")
        sub.configure(wraplength=860, justify="left")
        sub.pack(anchor="w", padx=12, pady=(0, 12))

        who = Section(root, "Requester"); who.pack(fill="x", padx=12, pady=8)
        LabeledEntry(who, "Requester ID", self.requester_id,
                     help_text="Your RSA keys live under this ID."
                     ).grid(sticky="we", padx=8, pady=8)

        # Cloud list
        req = Section(root, "Request Access"); req.pack(fill="both", expand=True, padx=12, pady=8)
        cloud_wrap = ttk.Frame(req); cloud_wrap.pack(fill="both", expand=True, padx=8, pady=8)

        cols = ("file_id", "filename", "size")
        self.tv_cloud = ttk.Treeview(cloud_wrap, columns=cols, show="headings", height=10, style="SS.Treeview")
        self.tv_cloud.heading("file_id", text="file_id")
        self.tv_cloud.heading("filename", text="filename")
        self.tv_cloud.heading("size", text="size")
        self.tv_cloud.column("file_id", width=420, stretch=True)
        self.tv_cloud.column("filename", width=320, stretch=True)
        self.tv_cloud.column("size", width=160, stretch=True)

        vbar_c = ttk.Scrollbar(cloud_wrap, orient="vertical", command=self.tv_cloud.yview)
        hbar_c = ttk.Scrollbar(cloud_wrap, orient="horizontal", command=self.tv_cloud.xview)
        self.tv_cloud.configure(yscrollcommand=vbar_c.set, xscrollcommand=hbar_c.set)

        cloud_wrap.columnconfigure(0, weight=1)
        cloud_wrap.rowconfigure(0, weight=1)
        self.tv_cloud.grid(row=0, column=0, sticky="nsew")
        vbar_c.grid(row=0, column=1, sticky="ns")
        hbar_c.grid(row=1, column=0, sticky="ew")

        rbtns = ttk.Frame(req); rbtns.pack(fill="x", padx=8, pady=(4, 8))
        ttk.Button(rbtns, text="Refresh Cloud Files", command=self._refresh_cloud).pack(side="left")
        ttk.Button(rbtns, text="Request Access for Selected", command=self._request_selected).pack(side="left", padx=8)

        # Shared list
        dl = Section(root, "Download Shared Files"); dl.pack(fill="both", expand=True, padx=12, pady=8)
        shared_wrap = ttk.Frame(dl); shared_wrap.pack(fill="both", expand=True, padx=8, pady=8)

        cols2 = ("file_id", "filename", "owner_id")
        self.tv_shared = ttk.Treeview(shared_wrap, columns=cols2, show="headings", height=10, style="SS.Treeview")
        self.tv_shared.heading("file_id", text="file_id")
        self.tv_shared.heading("filename", text="filename")
        self.tv_shared.heading("owner_id", text="owner_id")
        self.tv_shared.column("file_id", width=420, stretch=True)
        self.tv_shared.column("filename", width=320, stretch=True)
        self.tv_shared.column("owner_id", width=200, stretch=True)

        vbar_s = ttk.Scrollbar(shared_wrap, orient="vertical", command=self.tv_shared.yview)
        hbar_s = ttk.Scrollbar(shared_wrap, orient="horizontal", command=self.tv_shared.xview)
        self.tv_shared.configure(yscrollcommand=vbar_s.set, xscrollcommand=hbar_s.set)

        shared_wrap.columnconfigure(0, weight=1)
        shared_wrap.rowconfigure(0, weight=1)
        self.tv_shared.grid(row=0, column=0, sticky="nsew")
        vbar_s.grid(row=0, column=1, sticky="ns")
        hbar_s.grid(row=1, column=0, sticky="ew")

        dbtns = ttk.Frame(dl); dbtns.pack(fill="x", padx=8, pady=(4, 8))
        ttk.Button(dbtns, text="Scan My Shares", command=self._scan_shares).pack(side="left")
        ttk.Button(dbtns, text="Download, Decrypt & Verify Selected", command=self._download_selected).pack(side="left", padx=8)

        self.status = StatusBar(root); self.status.pack(fill="x")

        ensure_user_keys(KEYS_DIR, self.requester_id.get())
        self._refresh_cloud()

    # actions
    def _refresh_cloud(self):
        self.tv_cloud.delete(*self.tv_cloud.get_children())
        for f in list_files():
            self.tv_cloud.insert("", "end", values=(f["file_id"], f["filename"], f["size"]))
        self.status.info("Cloud list refreshed. Select a file and click Request Access.")

    def _request_selected(self):
        sel = self.tv_cloud.selection()
        if not sel:
            alert_error("Select a file row first."); return
        fid, _, _ = self.tv_cloud.item(sel[0], "values")
        chain = LocalChain()
        create_access_request(chain, self.requester_id.get(), fid)
        self.status.info(f"Access request created for file {fid}.")

    def _scan_shares(self):
        self.tv_shared.delete(*self.tv_shared.get_children())
        chain = LocalChain(); evs = chain.get_events()
        r = self.requester_id.get().strip()
        shares = [e["event"] for e in evs if e["event"].get("type") == "KEY_SHARE" and e["event"].get("requester_id") == r]
        latest = {}
        for ev in shares:
            latest[ev["file_id"]] = ev
        for fid, ev in latest.items():
            meta = get_meta(fid) or {}
            self.tv_shared.insert("", "end", values=(fid, meta.get("filename", "?"), ev.get("owner_id", "?")))
        self.status.info(f"Found {len(latest)} shared file(s). Select one and click Download.")

    def _download_selected(self):
        sel = self.tv_shared.selection()
        if not sel:
            alert_error("Select a shared file row first."); return
        fid, _, owner = self.tv_shared.item(sel[0], "values")
        self.owner_id.set(owner or self.owner_id.get())

        req_paths = ensure_user_keys(KEYS_DIR, self.requester_id.get())
        own_paths = ensure_user_keys(KEYS_DIR, self.owner_id.get())
        _, _, req_rsa_priv, _ = load_user_keys(req_paths)
        _, own_ecdsa_pub, _, _ = load_user_keys(own_paths)

        chain = LocalChain()
        try:
            pt = requester_download_and_verify(
                chain=chain,
                requester_id=self.requester_id.get(),
                requester_rsa_priv=req_rsa_priv,
                owner_ecdsa_pub=own_ecdsa_pub,
                file_id=fid
            )
        except Exception as e:
            alert_error(str(e)); return

        save_to = filedialog.asksaveasfilename(title="Save decrypted file as")
        if not save_to:
            self.status.warn("Save canceled."); return
        Path(save_to).write_bytes(pt)
        self.status.info(f"Decrypted and verified. Saved to: {save_to}")
