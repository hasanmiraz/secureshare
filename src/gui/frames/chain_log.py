import json
import tkinter as tk
from tkinter import ttk
from ..widgets import Section, StatusBar
from src.blockchain.local_chain import LocalChain
from src.util.time import pretty_ts

class ChainLogFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        header = ttk.Label(self, text="Blockchain Log", style="Header.TLabel")
        header.pack(anchor="w", padx=8, pady=(10, 2))
        ttk.Label(self, text="View recent events and verify the ledger integrity.").pack(anchor="w", padx=8, pady=(0, 10))

        controls = Section(self, "Controls")
        controls.pack(fill="x", padx=8, pady=6)

        row = ttk.Frame(controls); row.pack(fill="x", padx=6, pady=6)
        ttk.Label(row, text="Filter by type (optional):").pack(side="left")
        self.filter_var = tk.StringVar(value="")
        ttk.Entry(row, textvariable=self.filter_var, width=24).pack(side="left", padx=6)
        ttk.Button(row, text="Refresh", command=self._refresh).pack(side="left")

        view = Section(self, "Events")
        view.pack(fill="both", expand=True, padx=8, pady=6)
        self.text = tk.Text(view, height=18, wrap="word")
        self.text.pack(fill="both", expand=True, padx=6, pady=6)

        self.status = StatusBar(self)
        self.status.pack(fill="x")

        self._refresh()

    def _refresh(self):
        chain = LocalChain()
        ok = chain.verify_chain()
        evs = chain.get_events()
        f = self.filter_var.get().strip().upper()

        self.text.delete("1.0", "end")
        self.text.insert("end", f"Chain valid: {ok}\n\n")
        for b in evs:
            ev = b.get("event", {})
            if f and ev.get("type", "").upper() != f:
                continue
            ts = pretty_ts(b.get("ts", 0))
            self.text.insert("end", f"[{ts}] {ev.get('type', '?')}\n")
            pretty = json.dumps(ev, indent=2)
            self.text.insert("end", f"{pretty}\n\n")

        if ok:
            self.status.info("Ledger verified.")
        else:
            self.status.error("Ledger integrity check failed. One or more blocks were tampered.")
