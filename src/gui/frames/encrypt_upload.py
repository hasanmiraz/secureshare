import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config.settings import KEYS_DIR
from src.blockchain.local_chain import LocalChain
from src.core.keystore import ensure_user_keys, load_user_keys
from src.services.uploader import encrypt_sign_upload

class EncryptUploadFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.owner_id = tk.StringVar(value="owner1")
        self.file_path = tk.StringVar(value="")

        # Owner input
        frm = ttk.Frame(self)
        frm.pack(fill="x", pady=8)
        ttk.Label(frm, text="Owner ID:").pack(side="left", padx=6)
        ttk.Entry(frm, textvariable=self.owner_id, width=20).pack(side="left")

        # File selection
        filefrm = ttk.Frame(self)
        filefrm.pack(fill="x", pady=8)
        ttk.Entry(filefrm, textvariable=self.file_path, width=70).pack(side="left", padx=6)
        ttk.Button(filefrm, text="Browse...", command=self._browse).pack(side="left")

        # Upload action
        ttk.Button(self, text="Encrypt, Sign & Upload", command=self._do_upload).pack(pady=8)

        # Output area
        self.result = tk.Text(self, height=8)
        self.result.pack(fill="both", expand=True, padx=6, pady=6)

    def _browse(self):
        # Open file chooser
        p = filedialog.askopenfilename()
        if p:
            self.file_path.set(p)

    def _do_upload(self):
        # Encrypt, sign, and upload selected file
        path = self.file_path.get().strip()
        if not path:
            messagebox.showerror("Error", "Choose a file first.")
            return

        kp = ensure_user_keys(KEYS_DIR, self.owner_id.get())
        ecdsa_priv, _, _, _ = load_user_keys(kp)

        chain = LocalChain()
        out = encrypt_sign_upload(ecdsa_priv, self.owner_id.get(), path, chain=chain)
        self.result.delete("1.0", "end")
        self.result.insert("end", f"Uploaded file_id: {out['file_id']}\n")
        self.result.insert("end", f"AES key (hex): {out['aes_key'].hex()}\n")
        self.result.insert("end", f"Nonce (hex): {out['nonce'].hex()}\n")
        self.result.insert("end", f"Signature (hex): {out['signature'].hex()}\n")
        self.result.insert("end", f"Ciphertext bytes: {out['size']}\n")
