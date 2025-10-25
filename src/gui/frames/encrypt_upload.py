import os
import tkinter as tk
from tkinter import ttk, filedialog
from src.blockchain.local_chain import LocalChain
from src.core.keystore import ensure_user_keys, load_user_keys
from src.services.uploader import encrypt_sign_upload
from config.settings import KEYS_DIR
from ..widgets import Section, LabeledEntry, StatusBar, alert_error

class EncryptUploadFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.owner_id  = tk.StringVar(value="owner1")
        self.file_path = tk.StringVar(value="")
        self.file_info = tk.StringVar(value="No file selected")

        header = ttk.Label(self, text="Encrypt and Upload a File", style="Header.TLabel")
        header.pack(anchor="w", padx=8, pady=(10, 2))
        ttk.Label(self, text="Choose a file, then the app will encrypt, sign, and upload it.").pack(anchor="w", padx=8, pady=(0, 10))

        who = Section(self, "Owner")
        who.pack(fill="x", padx=8, pady=6)
        LabeledEntry(who, "Owner ID", self.owner_id, help_text="Used to find your signing keys.").grid(sticky="we", padx=6, pady=6)

        file_sec = Section(self, "File")
        file_sec.pack(fill="x", padx=8, pady=6)

        frow = ttk.Frame(file_sec)
        frow.pack(fill="x", padx=6, pady=6)
        ttk.Entry(frow, textvariable=self.file_path, width=60).pack(side="left", fill="x", expand=True)
        ttk.Button(frow, text="Browse…", command=self._browse).pack(side="left", padx=6)
        ttk.Label(file_sec, textvariable=self.file_info, style="Help.TLabel").pack(anchor="w", padx=6)

        ttk.Button(self, text="Encrypt, Sign & Upload", command=self._do_upload).pack(padx=8, pady=8, anchor="w")

        out_sec = Section(self, "Result")
        out_sec.pack(fill="both", expand=True, padx=8, pady=6)

        self.out = tk.Text(out_sec, height=10, wrap="word")
        self.out.pack(fill="both", expand=True, padx=6, pady=6)

        self.status = StatusBar(self)
        self.status.pack(fill="x")

    def _browse(self):
        p = filedialog.askopenfilename()
        if p:
            self.file_path.set(p)
            try:
                size = os.path.getsize(p)
                self.file_info.set(f"Selected: {os.path.basename(p)} ({size} bytes)")
            except Exception:
                self.file_info.set(f"Selected: {os.path.basename(p)}")

    def _do_upload(self):
        path = self.file_path.get().strip()
        if not path or not os.path.exists(path):
            alert_error("Choose a valid file first.")
            return

        # Ensure owner keys
        kp = ensure_user_keys(KEYS_DIR, self.owner_id.get())
        ecdsa_priv, _, _, _ = load_user_keys(kp)

        chain = LocalChain()
        result = encrypt_sign_upload(ecdsa_priv, self.owner_id.get(), path, chain=chain)

        self.out.delete("1.0", "end")
        self.out.insert("end", f"Upload complete.\n\n")
        self.out.insert("end", f"File ID: {result['file_id']}\n")
        self.out.insert("end", f"AES key (hex): {result['aes_key'].hex()}\n")
        self.out.insert("end", f"Nonce (hex): {result['nonce'].hex()}\n")
        self.out.insert("end", f"Signature (hex): {result['signature'].hex()}\n")
        self.out.insert("end", f"Ciphertext size: {result['size']} bytes\n")

        self.status.info("Encrypted, signed, and uploaded. Next: share the AES key to the requester.")
