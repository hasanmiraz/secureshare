import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont


class Section(ttk.LabelFrame):
    """A labeled frame with consistent padding for grouping controls."""
    def __init__(self, master, text: str):
        super().__init__(master, text=text, padding=(16, 12))


class LabeledEntry(ttk.Frame):
    """Label + Entry with optional help text underneath."""
    def __init__(self, master, label: str, textvariable: tk.StringVar, width=36, help_text: str | None = None):
        super().__init__(master)
        ttk.Label(self, text=label).grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=textvariable, width=width).grid(row=1, column=0, sticky="we")
        if help_text:
            ttk.Label(self, text=help_text, style="Help.TLabel").grid(row=2, column=0, sticky="w")


class StatusBar(ttk.Frame):
    """Simple status bar for messages at the bottom of a screen."""
    def __init__(self, master):
        super().__init__(master)
        self.var = tk.StringVar(value="")
        self.lbl = ttk.Label(self, textvariable=self.var, anchor="w")
        self.lbl.pack(fill="x", padx=8, pady=8)

    def info(self, msg: str):  self._set(msg, "#111827")
    def warn(self, msg: str):  self._set(msg, "#b26b00")
    def error(self, msg: str): self._set(msg, "#a10000")

    def _set(self, msg: str, color: str):
        self.var.set(msg)
        self.lbl.configure(foreground=color)
        self.update_idletasks()


def confirm(title: str, message: str) -> bool:
    return messagebox.askyesno(title, message)


def alert_error(message: str, title: str = "Error"):
    messagebox.showerror(title, message)


class ScrollableFrame(ttk.Frame):
    """
    Full-page vertical scroll container with the scrollbar pinned to the far right.
    Put all content inside `self.body`.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        canvas = tk.Canvas(self, highlightthickness=0)
        vbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)

        self.body = ttk.Frame(canvas)
        self.body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window = canvas.create_window((0, 0), window=self.body, anchor="nw")

        def _resize_inner(event):
            canvas.itemconfigure(window, width=event.width)
        canvas.bind("<Configure>", _resize_inner)

        canvas.configure(yscrollcommand=vbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")

        # Natural mousewheel across platforms
        self.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.bind_all("<Button-4>",  lambda e: canvas.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>",  lambda e: canvas.yview_scroll( 1, "units"))


def apply_treeview_style(root_or_widget):
    """
    Make Treeview readable on all themes/platforms and avoid text clipping.
    """
    style = ttk.Style(root_or_widget)
    try:
        base_font = tkfont.nametofont("TkDefaultFont")
    except Exception:
        base_font = tkfont.Font(family="Helvetica", size=12)
    line_space = base_font.metrics("linespace")
    row_height = max(30, int(line_space + 12))

    style.configure("SS.Treeview", font=(base_font.actual("family"), base_font.actual("size")),
                    rowheight=row_height, fieldbackground="#ffffff")
    style.configure("SS.Treeview.Heading", font=(base_font.actual("family"), base_font.actual("size"), "bold"))
    style.map("SS.Treeview",
              background=[("selected", "#dce7ff")],
              foreground=[("selected", "#111111")])
