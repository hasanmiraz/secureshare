import tkinter as tk
from tkinter import ttk
from config.settings import APP_TITLE, APP_SIZE
from .frames.encrypt_upload import EncryptUploadFrame
from .frames.requests import RequestsFrame
from .frames.share_key import ShareKeyFrame
from .frames.downloads import DownloadsFrame
from .frames.chain_log import ChainLogFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)

        # Tabbed interface for different app functions
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True)
        nb.add(EncryptUploadFrame(nb), text="Encrypt & Upload (Owner)")
        nb.add(RequestsFrame(nb), text="Requests")
        nb.add(ShareKeyFrame(nb), text="Share Key (Owner)")
        nb.add(DownloadsFrame(nb), text="Downloads (Requester)")
        nb.add(ChainLogFrame(nb), text="Blockchain Log")
