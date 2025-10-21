import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import KEYS_DIR
from src.blockchain.local_chain import LocalChain
from src.core.keystore import ensure_user_keys
from src.storage.cloud import list_files
from src.services.sharing import create_access_request

class RequestsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.requester_id = tk.StringVar(value="requester1")
        self.file_id = tk.StringVar(value="")

        # Input fields
        top = ttk.Frame(self); top.pack(fill="x", pady=8)
        ttk.Label(top, text="Requester ID:").pack(side="left", padx=6)
        ttk.Entry(top, textvariable=self.requester_id, width=20).pack(side="left")

        mid = ttk.Frame(self); mid.pack(fill="x", pady=8)
        ttk.Label(mid, text="File ID:").pack(side="left", padx=6)
        ttk.Entry(mid, textvariable=self.file_id, width=40).pack(side="left")
        ttk.Button(mid, text="Pick from Cloud", command=self._pick_cloud).pack(side="left", padx=6)

        # Action button and output area
        ttk.Button(self, text="Create Access Request", command=self._request).pack(pady=8)
        self.out = tk.Text(self, height=8); self.out.pack(fill="both", expand=True, padx=6, pady=6)

        # Ensure requester keys exist
        ensure_user_keys(KEYS_DIR, self.requester_id.get())

    def _pick_cloud(self):
        # List available files in cloud storage
        files = list_files()
        if not files:
            messagebox.showinfo("Cloud", "No files uploaded yet.")
            return
        self.out.delete("1.0", "end")
        for f in files:
            self.out.insert("end", f"{f['file_id']}  {f['filename']}  ({f['size']} bytes)\n")

    def _request(self):
        # Create access request for a file
        fid = self.file_id.get().strip()
        if not fid:
            messagebox.showerror("Error", "Enter a File ID.")
            return
        chain = LocalChain()
        create_access_request(chain, self.requester_id.get(), fid)
        self.out.insert("end", f"ACCESS_REQUEST created for file {fid} by {self.requester_id.get()}\n")
