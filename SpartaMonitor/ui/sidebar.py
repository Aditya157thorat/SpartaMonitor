import ttkbootstrap as ttk
from ttkbootstrap.constants import *

print("[debug] loading sidebar.py")

SECTIONS = [
    ("cpu",  "⚔  Core Usage"),
    ("ram",  "🛡  RAM Usage"),
    ("temp", "🔥  Core Temp"),
    ("disk", "💽  Disk Usage"),
    ("gpu",  "🎮  GPU Stats"),
    ("settings", "⚙  Settings"),
]

class Sidebar:
    def __init__(self, master, width=220, on_nav=None):
        self.master = master
        self.width = width
        self.visible = True
        self.on_nav = on_nav

        self.frame = ttk.Frame(master, bootstyle=SECONDARY)
        self.frame.configure(padding=10)

        ttk.Label(self.frame, text="SpartaMonitor",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        self.buttons = {}
        for key, label in SECTIONS:
            btn = ttk.Button(self.frame, text=label, bootstyle=(DARK, OUTLINE),
                             command=lambda k=key: self._click(k))
            btn.pack(fill="x", pady=6)
            self.buttons[key] = btn

        self._highlight("cpu")

    def _click(self, key):
        self._highlight(key)
        if self.on_nav:
            self.on_nav(key)

    def _highlight(self, key):
        for k, btn in self.buttons.items():
            style = (DARK, OUTLINE) if k != key else (DANGER,)
            btn.configure(bootstyle=style)
