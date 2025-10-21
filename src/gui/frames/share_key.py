import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import KEYS_DIR
from src.core.keystore import ensure_user_keys, load_user_keys
from src.blockchain.local_chain import LocalChain
from src.services.sharing import approve_and_share_key

class ShareKeyFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.owner_id = tk.StringVar(value="owner1")
        self.requester_id = tk.StringVar(value="requester1")
        self.file_id = tk.StringVar(value="")
        self.aes_key_hex = tk.StringVar(value="")  # AES key pasted from upload step

        # Input fields
        frm = ttk.Frame(self); frm.pack(fill="x", pady=8)
        ttk.Label(frm, text="Owner ID:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.owner_id, width=20).grid(row=0, column=1, sticky="w")

        ttk.Label(frm, text="Requester ID:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.requester_id, width=20).grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="File ID:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.file_id, width=45).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="AES Key (hex):").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.aes_key_hex, width=60).grid(row=3, column=1, sticky="w")

        # Action button and output area
        ttk.Button(self, text="Approve & Share Key", command=self._share).pack(pady=8)
        self.out = tk.Text(self, height=8); self.out.pack(fill="both", expand=True, padx=6, pady=6)

    def _share(self):
        # Approve access and share AES key with requester
        try:
            aes_key = bytes.fromhex(self.aes_key_hex.get().strip())
        except Exception:
            messagebox.showerror("Error", "Invalid AES key hex.")
            return
        if not self.file_id.get().strip():
            messagebox.showerror("Error", "Provide File ID.")
            return

        # Load requester RSA public key
        req_paths = ensure_user_keys(KEYS_DIR, self.requester_id.get())
        _, _, _, req_rsa_pub = load_user_keys(req_paths)

        chain = LocalChain()
        approve_and_share_key(
            chain=chain,
            owner_id=self.owner_id.get(),
            file_id=self.file_id.get().strip(),
            requester_id=self.requester_id.get(),
            requester_rsa_pub=req_rsa_pub,
            aes_key=aes_key
        )
        self.out.insert("end", "Key shared successfully (KEY_SHARE event appended)\n")
