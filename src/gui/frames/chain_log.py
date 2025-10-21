import tkinter as tk
from tkinter import ttk
from src.blockchain.local_chain import LocalChain
from src.util.time import pretty_ts

class ChainLogFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Button to refresh the log display
        ttk.Button(self, text="Refresh", command=self._refresh).pack(pady=6)
        # Text area for showing blockchain events
        self.text = tk.Text(self, height=20)
        self.text.pack(fill="both", expand=True, padx=6, pady=6)
        self._refresh()

    def _refresh(self):
        # Load and verify the local chain, then display events
        chain = LocalChain()
        evs = chain.get_events()
        ok = chain.verify_chain()
        self.text.delete("1.0", "end")
        self.text.insert("end", f"Chain valid: {ok}\n\n")
        for b in evs:
            ts = pretty_ts(b["ts"])
            ev = b["event"]
            self.text.insert("end", f"[{ts}] {ev.get('type')}  {ev}\n")
