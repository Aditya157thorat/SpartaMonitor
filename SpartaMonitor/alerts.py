import time
import tkinter as tk
from tkinter import ttk

# Simple alert manager with debouncing and auto-hide toasts
class Alerts:
    def __init__(self, root, callback=None):
        self.root = root
        self.callback = callback
        self.last_fire = {}
        self.cooldown = 20  # seconds between same-alert repeats

        # default thresholds (customize as you like)
        self.thresholds = {
            "cpu_percent": 90,     # percent
            "mem_percent": 90,
            "disk_percent": 95,    # highest mounted partition percent
            "gpu_percent": 95,
        }

    def check(self, snapshot: dict):
        now = time.time()
        fired = []

        # CPU
        cpu_p = snapshot.get("cpu", {}).get("percent")
        if cpu_p is not None and cpu_p >= self.thresholds["cpu_percent"]:
            fired.append(("warning", f"High CPU usage: {cpu_p:.0f}%"))

        # Memory
        mem_p = snapshot.get("memory", {}).get("percent")
        if mem_p is not None and mem_p >= self.thresholds["mem_percent"]:
            fired.append(("warning", f"High memory usage: {mem_p:.0f}%"))

        # Disk
        disk_list = snapshot.get("disks", [])
        if disk_list:
            worst = max(d.get("percent", 0) for d in disk_list)
            if worst >= self.thresholds["disk_percent"]:
                fired.append(("warning", f"Low disk space: {worst:.0f}% used"))

        # GPU
        gpu_list = snapshot.get("gpus", [])
        if gpu_list:
            worst_gpu = max(g.get("load_percent", 0) for g in gpu_list)
            if worst_gpu >= self.thresholds["gpu_percent"]:
                fired.append(("warning", f"High GPU load: {worst_gpu:.0f}%"))

        # Emit with cooldown
        for level, msg in fired:
            last = self.last_fire.get(msg, 0)
            if now - last >= self.cooldown:
                self.last_fire[msg] = now
                if self.callback:
                    self.callback(level, msg)
                else:
                    self._toast(level.upper(), msg)

    def _toast(self, title, msg):
        # minimal toast window
        win = tk.Toplevel(self.root)
        win.title(title)
        win.attributes("-topmost", True)
        win.resizable(False, False)
        win.geometry("+60+60")

        frm = ttk.Frame(win, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=title).pack(anchor="w")
        ttk.Label(frm, text=msg).pack(anchor="w", pady=(4, 8))
        ttk.Button(frm, text="Dismiss", command=win.destroy).pack(anchor="e")

        # auto-close after 5s
        win.after(5000, lambda: (win.winfo_exists() and win.destroy()))
