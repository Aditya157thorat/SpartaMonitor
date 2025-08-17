import tkinter as tk
from tkinter import ttk

from utils.theme import COLORS

NAV_ITEMS = [
    ("overview", "Overview"),
    ("cpu", "CPU"),
    ("memory", "Memory"),
    ("disk", "Disk"),
    ("network", "Network"),
    ("gpu", "GPU"),
]


class Sidebar:
    def __init__(self, root, on_nav):
        self.root = root
        self.on_nav = on_nav
        self.frame = ttk.Frame(root)
        self.buttons = {}

        self._build()

    def _build(self):
        style = ttk.Style()
        try:
            style.configure("Sidebar.TFrame", background=COLORS["ink"])
            style.configure("Sidebar.TButton", background=COLORS["ink"], foreground="#ddd")
            style.map("Sidebar.TButton", background=[("active", "#1a1a1a")])
            self.frame.configure(style="Sidebar.TFrame")
        except Exception:
            pass

        for i, (key, label) in enumerate(NAV_ITEMS):
            btn = ttk.Button(self.frame, text=label, command=lambda k=key: self.on_nav(k))
            try:
                btn.configure(style="Sidebar.TButton")
            except Exception:
                pass
            btn.pack(fill="x", padx=6, pady=4)
            self.buttons[key] = btn

        self._active = None

    def set_active(self, key: str):
        if self._active and self._active in self.buttons:
            try:
                self.buttons[self._active].configure(state="normal")
            except Exception:
                pass
        self._active = key
        if key in self.buttons:
            try:
                self.buttons[key].configure(state="disabled")
            except Exception:
                pass
