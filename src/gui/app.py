import tkinter as tk
from tkinter import ttk

try:
    import ttkbootstrap as tb  # optional, for modern UI
    HAS_BOOTSTRAP = True
except Exception:
    HAS_BOOTSTRAP = False

from .pages.home import HomePage
from .pages.owner import OwnerPage
from .pages.requester import RequesterPage

APP_TITLE = "SecureShare | CSIT953"
APP_SIZE = "1024x700"


def _init_theme(root: tk.Tk):
    # DPI scaling
    try:
        root.call("tk", "scaling", 1.25)
    except Exception:
        pass

    if HAS_BOOTSTRAP:
        # Prefer a modern theme (flatly; fallback to cerulean)
        style = tb.Style(theme="flatly")
        # base fonts
        style.configure(".", font=("Inter", 12))
        style.configure("TButton", padding=(12, 8), font=("Inter", 12))
        style.configure("TEntry", padding=(6, 6))
        style.configure("Header.TLabel", font=("Inter", 18, "bold"))
        style.configure("Help.TLabel", foreground="#6b7280")  # slate-500
        style.configure("CTA.TButton", font=("Inter", 13, "bold"), padding=(14, 10))
        root.option_add("*tearOff", False)
        return

    # ttk fallback (clam) with nicer defaults
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure(".", padding=6, font=("Helvetica", 12))
    style.configure("TButton", padding=(12, 8), font=("Helvetica", 12))
    style.configure("TEntry", padding=4, font=("Helvetica", 12))
    style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
    style.configure("Help.TLabel", foreground="#6b7280")
    style.configure("CTA.TButton", font=("Helvetica", 13, "bold"), padding=(14, 10))
    root.option_add("*tearOff", False)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(900, 620)
        _init_theme(self)

        # Router container
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.pages = {}
        for P in (HomePage, OwnerPage, RequesterPage):
            page = P(container, controller=self)
            self.pages[P.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show("HomePage")

    def show(self, name: str):
        self.pages[name].tkraise()


if __name__ == "__main__":
    App().mainloop()
