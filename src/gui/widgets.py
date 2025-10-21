import tkinter as tk
from tkinter import ttk

class StatusBar(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Label bound to status text
        self.var = tk.StringVar(value="")
        self.lbl = ttk.Label(self, textvariable=self.var, anchor="w")
        self.lbl.pack(fill="x", padx=6, pady=4)

    def set(self, msg: str):
        # Update status text
        self.var.set(msg)
        self.update_idletasks()
