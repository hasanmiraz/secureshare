import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from ..widgets import Section, LabeledEntry, StatusBar, alert_error
from src.blockchain.local_chain import LocalChain
from src.core.keystore import ensure_user_keys, load_user_keys
from src.services.verifier import requester_download_and_verify
from src.storage.cloud import get_meta

class DownloadsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.requester_id = tk.StringVar(value="requester1")
        self.owner_id = tk.StringVar(value="owner1")
        self.file_id = tk.StringVar(value="")
        self.status = StatusBar(self)

        header = ttk.Label(self, text="Download, Decrypt, and Verify", style="Header.TLabel")
        header.pack(anchor="w", padx=8, pady=(10, 2))
        ttk.Label(self, text="Pick a shared file or enter a file ID, then decrypt and verify signature.").pack(anchor="w", padx=8, pady=(0, 10))

        who = Section(self, "Participants")
        who.pack(fill="x", padx=8, pady=6)
        LabeledEntry(who, "Requester ID", self.requester_id).grid(sticky="we", padx=6, pady=6)
        LabeledEntry(who, "Owner ID", self.owner_id).grid(sticky="we", padx=6, pady=6)

        pick = Section(self, "Shared Files for Requester")
        pick.pack(fill="both", expand=True, padx=8, pady=6)

        cols = ("file_id", "filename", "owner")
        self.tv = ttk.Treeview(pick, columns=cols, show="headings", height=7)
        for c, w in zip(cols, (44, 24, 18)):
            self.tv.heading(c, text=c)
            self.tv.column(c, width=w * 10, stretch=True)
        self.tv.pack(fill="both", expand=True, padx=6, pady=6)

        btn_row = ttk.Frame(pick); btn_row.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(btn_row, text="Scan Eligible Shares", command=self._scan_shares).pack(side="left")
        ttk.Button(btn_row, text="Use Selected", command=self._use_selected).pack(side="left", padx=6)

        manual = Section(self, "Manual")
        manual.pack(fill="x", padx=8, pady=6)
        LabeledEntry(manual, "File ID", self.file_id, width=56).grid(sticky="we", padx=6, pady=6)

        ttk.Button(self, text="Download, Decrypt & Verify", command=self._download).pack(anchor="w", padx=8, pady=8)
        self.status.pack(fill="x")

        # Ensure keys exist
        ensure_user_keys(Path("data/keys"), self.requester_id.get())
        ensure_user_keys(Path("data/keys"), self.owner_id.get())

    def _scan_shares(self):
        """List file_ids that have a KEY_SHARE addressed to this requester."""
        self.tv.delete(*self.tv.get_children())
        chain = LocalChain()
        evs = chain.get_events()
        r = self.requester_id.get().strip()
        shares = [e["event"] for e in evs if e["event"].get("type") == "KEY_SHARE" and e["event"].get("requester_id") == r]
        # Show distinct last shares by file_id (latest wins)
        seen = {}
        for ev in shares:
            seen[ev["file_id"]] = ev
        for fid, ev in seen.items():
            meta = get_meta(fid) or {}
            self.tv.insert("", "end", values=(fid, meta.get("filename", "?"), ev.get("owner_id", "?")))
        self.status.info(f"Found {len(seen)} shared file(s) for requester {r}.")

    def _use_selected(self):
        sel = self.tv.selection()
        if not sel:
            alert_error("Select a file row first.")
            return
        vals = self.tv.item(sel[0], "values")
        self.file_id.set(vals[0])
        self.owner_id.set(vals[2] if vals[2] else self.owner_id.get())
        self.status.info(f"Selected file_id: {vals[0]}")

    def _download(self):
        fid = self.file_id.get().strip()
        if not fid:
            alert_error("Enter or select a file ID first.")
            return

        chain = LocalChain()
        req_id = self.requester_id.get().strip()
        own_id = self.owner_id.get().strip()

        # Load keys
        from config.settings import KEYS_DIR
        req_paths = ensure_user_keys(KEYS_DIR, req_id)
        own_paths = ensure_user_keys(KEYS_DIR, own_id)
        _, _, req_rsa_priv, _ = load_user_keys(req_paths)
        _, own_ecdsa_pub, _, _ = load_user_keys(own_paths)

        try:
            pt = requester_download_and_verify(
                chain=chain,
                requester_id=req_id,
                requester_rsa_priv=req_rsa_priv,
                owner_ecdsa_pub=own_ecdsa_pub,
                file_id=fid
            )
        except Exception as e:
            alert_error(str(e))
            return

        save_to = filedialog.asksaveasfilename(title="Save decrypted file as")
        if not save_to:
            self.status.warn("Save canceled.")
            return
        Path(save_to).write_bytes(pt)
        self.status.info(f"Decrypted and verified. Saved to: {save_to}")
