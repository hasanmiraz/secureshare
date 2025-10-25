import tkinter as tk
from tkinter import ttk
from ..widgets import Section, LabeledEntry, StatusBar, alert_error
from src.core.keystore import ensure_user_keys, load_user_keys
from src.blockchain.local_chain import LocalChain
from src.services.sharing import approve_and_share_key
from config.settings import KEYS_DIR

_VALID_KEY_SIZES = {16, 24, 32}  # bytes

class ShareKeyFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.owner_id = tk.StringVar(value="owner1")
        self.requester_id = tk.StringVar(value="requester1")
        self.file_id = tk.StringVar(value="")
        self.aes_key_hex = tk.StringVar(value="")
        self.key_len = tk.StringVar(value="Key length: 0 bytes")

        header = ttk.Label(self, text="Approve Access and Share AES Key", style="Header.TLabel")
        header.pack(anchor="w", padx=8, pady=(10, 2))
        ttk.Label(self, text="Paste the AES key (hex) generated during upload, not the nonce.").pack(anchor="w", padx=8, pady=(0, 10))

        who = Section(self, "Participants")
        who.pack(fill="x", padx=8, pady=6)
        LabeledEntry(who, "Owner ID", self.owner_id).grid(sticky="we", padx=6, pady=6)
        LabeledEntry(who, "Requester ID", self.requester_id).grid(sticky="we", padx=6, pady=6)

        what = Section(self, "File and Key")
        what.pack(fill="x", padx=8, pady=6)
        LabeledEntry(what, "File ID", self.file_id, width=56, help_text="Use the file you approved access for.").grid(sticky="we", padx=6, pady=6)

        row = ttk.Frame(what); row.grid(sticky="we", padx=6, pady=6)
        ttk.Label(row, text="AES Key (hex)").grid(row=0, column=0, sticky="w")
        e = ttk.Entry(row, textvariable=self.aes_key_hex, width=60)
        e.grid(row=1, column=0, sticky="we")
        e.bind("<KeyRelease>", self._update_key_len)
        ttk.Label(row, textvariable=self.key_len, style="Help.TLabel").grid(row=2, column=0, sticky="w")

        ttk.Button(self, text="Approve & Share Key", command=self._share).pack(anchor="w", padx=8, pady=8)

        self.status = StatusBar(self)
        self.status.pack(fill="x")

    def _update_key_len(self, *_):
        try:
            b = bytes.fromhex(self.aes_key_hex.get().strip())
            self.key_len.set(f"Key length: {len(b)} bytes")
        except Exception:
            self.key_len.set("Key length: invalid hex")

    def _share(self):
        key_hex = self.aes_key_hex.get().strip()
        if not key_hex:
            alert_error("Paste the AES key (hex) from the upload output.")
            return
        try:
            aes_key = bytes.fromhex(key_hex)
        except Exception:
            alert_error("AES key must be valid hex (no spaces/newlines).")
            return
        if len(aes_key) not in _VALID_KEY_SIZES:
            alert_error("AES key length invalid. Acceptable sizes: 16, 24, or 32 bytes.")
            return
        fid = self.file_id.get().strip()
        if not fid:
            alert_error("Provide File ID.")
            return

        req_paths = ensure_user_keys(KEYS_DIR, self.requester_id.get())
        _, _, _, req_rsa_pub = load_user_keys(req_paths)

        chain = LocalChain()
        approve_and_share_key(
            chain=chain,
            owner_id=self.owner_id.get(),
            file_id=fid,
            requester_id=self.requester_id.get(),
            requester_rsa_pub=req_rsa_pub,
            aes_key=aes_key
        )
        self.status.info("Key shared. Requester can now download and verify.")
