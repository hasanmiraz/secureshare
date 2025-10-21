import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config.settings import KEYS_DIR
from src.core.keystore import ensure_user_keys, load_user_keys
from src.blockchain.local_chain import LocalChain
from src.services.verifier import requester_download_and_verify
from pathlib import Path

class DownloadsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.requester_id = tk.StringVar(value="requester1")
        self.owner_id = tk.StringVar(value="owner1")
        self.file_id = tk.StringVar(value="")

        # Input fields
        frm = ttk.Frame(self); frm.pack(fill="x", pady=8)
        ttk.Label(frm, text="Requester ID:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.requester_id, width=20).grid(row=0, column=1, sticky="w")
        ttk.Label(frm, text="Owner ID:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.owner_id, width=20).grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="File ID:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.file_id, width=50).grid(row=2, column=1, sticky="w")

        # Action button and output area
        ttk.Button(self, text="Download, Decrypt & Verify", command=self._download).pack(pady=8)
        self.out = tk.Text(self, height=8); self.out.pack(fill="both", expand=True, padx=6, pady=6)

        # Ensure requester & owner keys exist
        ensure_user_keys(KEYS_DIR, self.requester_id.get())
        ensure_user_keys(KEYS_DIR, self.owner_id.get())

    def _download(self):
        # Retrieve and verify a file, then save decrypted output
        chain = LocalChain()
        req_paths = ensure_user_keys(KEYS_DIR, self.requester_id.get())
        own_paths = ensure_user_keys(KEYS_DIR, self.owner_id.get())

        _, _, req_rsa_priv, _ = load_user_keys(req_paths)
        _, own_ecdsa_pub, _, _ = load_user_keys(own_paths)

        try:
            pt = requester_download_and_verify(
                chain=chain,
                requester_id=self.requester_id.get(),
                requester_rsa_priv=req_rsa_priv,
                owner_ecdsa_pub=own_ecdsa_pub,
                file_id=self.file_id.get().strip()
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        save_to = filedialog.asksaveasfilename(title="Save decrypted file as")
        if not save_to:
            return
        Path(save_to).write_bytes(pt)
        self.out.insert("end", f"Decrypted file saved: {save_to}\n(Signature verified)\n")
