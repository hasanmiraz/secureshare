import tkinter as tk
from tkinter import ttk


class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Center content with generous whitespace
        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.38, anchor="center")  # visually centered higher for balance

        ttk.Label(wrapper, text="Welcome to SecureShare", style="Header.TLabel").pack(pady=(0, 6))
        sub = ttk.Label(wrapper, text="Choose what you want to do today.", style="Help.TLabel")
        sub.configure(wraplength=640, justify="center")
        sub.pack(pady=(0, 18))

        row = ttk.Frame(wrapper)
        row.pack()

        ttk.Button(
            row, text="Upload & Share (Owner)", style="CTA.TButton",
            command=lambda: controller.show("OwnerPage")
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            row, text="Request & Download (Requester)", style="CTA.TButton",
            command=lambda: controller.show("RequesterPage")
        ).grid(row=0, column=1, padx=10)
