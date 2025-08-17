import time
import tkinter as tk
from tkinter import ttk

from utils.formatting import format_duration
from utils.theme import COLORS


class TopBar:
    def __init__(self, root, on_toggle_sidebar, on_toggle_theme):
        self.root = root
        self.on_toggle_sidebar = on_toggle_sidebar
        self.on_toggle_theme = on_toggle_theme

        self.frame = ttk.Frame(root, padding=(10, 8))
        try:
            self.frame.configure(style="Topbar.TFrame")
        except Exception:
            pass

        self._build()

    def _build(self):
        self.frame.grid_columnconfigure(1, weight=1)

        # Sidebar toggle button
        self.toggle = ttk.Button(self.frame, text="☰", width=3, command=self.on_toggle_sidebar)
        self.toggle.grid(row=0, column=0, sticky="w")

        # App title
        self.title = ttk.Label(self.frame, text="SpartaMonitor", font=("Segoe UI", 12, "bold"))
        self.title.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # System info labels
        self.uptime_lbl = ttk.Label(self.frame, text="Uptime: —")
        self.uptime_lbl.grid(row=0, column=2, sticky="e", padx=(0, 10))

        self.battery_lbl = ttk.Label(self.frame, text="Battery: —")
        self.battery_lbl.grid(row=0, column=3, sticky="e", padx=(0, 10))

        # Notification bell
        self.bell = ttk.Label(self.frame, text="🔔", foreground="#888")
        self.bell.grid(row=0, column=4, sticky="e")

        self.theme_toggle = ttk.Button(self.frame, text="🌙", width=3, command=self.on_toggle_theme)
        self.theme_toggle.grid(row=0, column=5, sticky="e", padx=(10, 0))

        # Style configuration
        style = ttk.Style()
        try:
            style.configure("Topbar.TFrame", background=COLORS["bg_dark"])
            style.configure("Topbar.TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_light"])
            self.frame.configure(style="Topbar.TFrame")
            for w in (self.title, self.uptime_lbl, self.battery_lbl, self.bell):
                w.configure(style="Topbar.TLabel")
        except Exception:
            pass

    def update_system(self, system_data: dict):
        # Uptime
        uptime_s = system_data.get("uptime_seconds")
        if uptime_s is not None:
            self.uptime_lbl.config(text=f"Uptime: {format_duration(uptime_s)}")

        # Battery
        batt = system_data.get("battery")
        if batt and batt.get("percent") is not None:
            pct = int(batt["percent"])
            ac = "⚡" if batt.get("plugged") else ""
            self.battery_lbl.config(text=f"Battery: {pct}% {ac}")
        else:
            self.battery_lbl.config(text="Battery: —")

    def alert(self, level: str, message: str):
        # Flash bell and show toast
        self._flash_bell()
        self._toast(level.title(), message)

    def _flash_bell(self):
        def step(i=0):
            if i >= 6:
                self.bell.config(foreground="#888")
                return
            self.bell.config(foreground="#e03131" if i % 2 == 0 else "#f0c419")
            self.root.after(200, lambda: step(i + 1))

        step(0)

    def _toast(self, title, message):
        top = tk.Toplevel(self.root)
        top.title(title)
        top.attributes("-topmost", True)
        top.resizable(False, False)

        # Position near top-right of root window
        try:
            x = self.root.winfo_x() + self.root.winfo_width() - 320
            y = self.root.winfo_y() + 60
            top.geometry(f"300x120+{x}+{y}")
        except Exception:
            top.geometry("300x120+80+80")

        frm = ttk.Frame(top, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(frm, text=message, wraplength=260).pack(anchor="w", pady=(6, 10))
        ttk.Button(frm, text="Dismiss", command=top.destroy).pack(anchor="e")

        top.after(5000, lambda: (top.winfo_exists() and top.destroy()))
