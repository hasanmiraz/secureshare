import tkinter as tk
from tkinter import ttk
from ..widgets import Section, LabeledEntry, StatusBar, alert_error
from src.storage.cloud import list_files
from src.blockchain.local_chain import LocalChain
from src.services.sharing import create_access_request
from config.settings import KEYS_DIR
from src.core.keystore import ensure_user_keys

class RequestsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.requester_id = tk.StringVar(value="requester1")
        self.selected_file_id = tk.StringVar(value="")
        self.status = StatusBar(self)

        header = ttk.Label(self, text="Request Access to a File", style="Header.TLabel")
        header.pack(anchor="w", padx=8, pady=(10, 2))
        ttk.Label(self, text="Pick a file from the cloud list and create an access request.").pack(anchor="w", padx=8, pady=(0, 10))

        who = Section(self, "Requester")
        who.pack(fill="x", padx=8, pady=6)
        LabeledEntry(who, "Requester ID", self.requester_id, help_text="Your RSA keys live under this ID.").grid(sticky="we", padx=6, pady=6)

        list_sec = Section(self, "Cloud Files")
        list_sec.pack(fill="both", expand=True, padx=8, pady=6)

        # Treeview: file_id, filename, size
        cols = ("file_id", "filename", "size")
        self.tv = ttk.Treeview(list_sec, columns=cols, show="headings", height=8)
        for c, w in zip(cols, (44, 24, 8)):
            self.tv.heading(c, text=c)
            self.tv.column(c, width=w * 10, stretch=True)
        self.tv.pack(fill="both", expand=True, padx=6, pady=6)

        btn_row = ttk.Frame(list_sec)
        btn_row.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(btn_row, text="Refresh List", command=self._refresh).pack(side="left")
        ttk.Button(btn_row, text="Use Selected", command=self._use_selected).pack(side="left", padx=6)

        action = Section(self, "Create Request")
        action.pack(fill="x", padx=8, pady=6)
        ttk.Button(action, text="Create Access Request", command=self._request).pack(anchor="w", padx=6, pady=6)

        self.status.pack(fill="x")
        ensure_user_keys(KEYS_DIR, self.requester_id.get())
        self._refresh()

    def _refresh(self):
        self.tv.delete(*self.tv.get_children())
        for f in list_files():
            self.tv.insert("", "end", values=(f["file_id"], f["filename"], f["size"]))
        self.status.info("Cloud list refreshed.")

    def _use_selected(self):
        sel = self.tv.selection()
        if not sel:
            alert_error("Select a file row first.")
            return
        vals = self.tv.item(sel[0], "values")
        self.selected_file_id.set(vals[0])
        self.status.info(f"Selected file_id: {vals[0]}")

    def _request(self):
        fid = self.selected_file_id.get().strip()
        if not fid:
            alert_error("Pick a file from the list first.")
            return
        chain = LocalChain()
        create_access_request(chain, self.requester_id.get(), fid)
        self.status.info(f"Access request created for file {fid}.")
