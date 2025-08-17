import time
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from alerts import Alerts
from monitor import cpu as cpu_mon
from monitor import memory as mem_mon
from monitor import disk as disk_mon
from monitor import network as net_mon
from monitor import gpu as gpu_mon
from monitor import system as sys_mon
from utils.formatting import human_bytes, human_rate, format_duration
from utils.theme import COLORS


# Optional Pillow for background image support
try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter
    PIL_OK = True
except Exception:
    PIL_OK = False


class Dashboard:
    def __init__(self, root, notify):
        self.root = root
        self.frame = tk.Frame(root, bg="black")  # Use tk.Frame for layering
        self.frame.grid(row=0, column=0, sticky="nsew")

        # --- Background ---
        self.bg_label = None
        if PIL_OK:
            bg_path = Path("assets/bacg.png")
            print(f"[Dashboard] Looking for background at: {bg_path.resolve()}")

            if bg_path.exists():
                try:
                    img = Image.open(bg_path)
                    self.bg_img = ImageTk.PhotoImage(img)
                    self.bg_label = tk.Label(self.frame, image=self.bg_img, borderwidth=0)
                    self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
                    self.frame.bind("<Configure>", self._resize_bg)
                    self._bg_path = bg_path
                except Exception as e:
                    print(f"[Dashboard] Could not load background: {e}")

        # --- Transparent Style ---
        style = ttk.Style()
        style.configure("Transparent.TFrame", background="")

        # --- Foreground container ---
        self.container = tk.Frame(
            self.frame,
            bg=COLORS["glass_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0
        )
        self.container.place(relx=0.05, rely=0.08, relwidth=0.9, relheight=0.85)

      #  self.container.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Panels
        self.panels = {
            "overview": OverviewPanel(self.container),
            "cpu": CPUPanel(self.container),
            "memory": MemoryPanel(self.container),
            "disk": DiskPanel(self.container),
            "network": NetworkPanel(self.container),
            "gpu": GPUPanel(self.container),
        }
        self.current_key = None
        self.alerts = Alerts(root, callback=notify)

    def _resize_bg(self, event):
        if not (PIL_OK and hasattr(self, "_bg_path")):
            return
        try:
            img = Image.open(self._bg_path)
            img = img.resize((event.width, event.height), Image.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(img)
            self.bg_label.configure(image=self.bg_img)
        except Exception as e:
            print(f"[Dashboard] Background resize failed: {e}")


    def show(self, key: str):
        if self.current_key == key:
            return
        for child in self.container.winfo_children():
            child.pack_forget()
        panel = self.panels.get(key)
        if panel:
            panel.frame.pack(fill="both", expand=True)
            self.current_key = key

    def refresh(self):
        if self.current_key:
            self.panels[self.current_key].refresh()

        snapshot = {
            "cpu": cpu_mon.get_overview(),
            "memory": mem_mon.get_overview(),
            "disks": disk_mon.get_disks(),
            "network": net_mon.get_overview(),
            "gpus": gpu_mon.get_gpus(),
            "system": sys_mon.get_overview(),
        }

        if "network" in self.panels:
            self.panels["network"].ingest_counters(snapshot["network"])

        self.panels["overview"].update_from(snapshot)
        self.alerts.check(snapshot)
        return snapshot


# ------------------------
# Panel Implementations
# ------------------------

class OverviewPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.cpu = ttk.Label(self.frame, text="CPU: —")
        self.mem = ttk.Label(self.frame, text="Memory: —")
        self.disk = ttk.Label(self.frame, text="Disk: —")
        self.net = ttk.Label(self.frame, text="Network: —")
        self.gpu = ttk.Label(self.frame, text="GPU: —")
        self.sys = ttk.Label(self.frame, text="Uptime: —")
        for w in (self.cpu, self.mem, self.disk, self.net, self.gpu, self.sys):
            w.pack(anchor="w", pady=4)

    def update_from(self, snap: dict):
        c = snap["cpu"]
        self.cpu.config(text=f"CPU: {c.get('percent', 0):.0f}% @ {c.get('freq_mhz', 0):.0f} MHz ({c.get('cores_logical', '?')} cores)")
        m = snap["memory"]
        self.mem.config(text=f"Memory: {m.get('percent', 0):.0f}% {human_bytes(m.get('used', 0))}/{human_bytes(m.get('total', 0))}")
        d = snap["disks"]
        if d:
            worst = max(d, key=lambda x: x.get("percent", 0))
            self.disk.config(text=f"Disk: {worst.get('mount')} {worst.get('percent', 0):.0f}% used ({human_bytes(worst.get('used', 0))}/{human_bytes(worst.get('total', 0))})")
        else:
            self.disk.config(text="Disk: —")
        n = snap["network"]
        self.net.config(text=f"Network: Up {human_rate(n.get('tx_rate_bps', 0))} | Down {human_rate(n.get('rx_rate_bps', 0))}")
        g_list = snap["gpus"]
        if g_list:
            g = max(g_list, key=lambda x: x.get("load_percent", 0))
            self.gpu.config(text=f"GPU: {g.get('name','GPU')} {g.get('load_percent',0):.0f}% Mem {g.get('mem_used_mb',0)}/{g.get('mem_total_mb',0)} MB")
        else:
            self.gpu.config(text="GPU: —")
        s = snap["system"]
        self.sys.config(text=f"Uptime: {format_duration(s.get('uptime_seconds', 0))}")

    def refresh(self):
        pass


class CPUPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="CPU Usage", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        self.overview = ttk.Label(self.frame, text="—")
        self.overview.pack(anchor="w", pady=(0, 10))
        self.core_frame = ttk.Frame(self.frame)
        self.core_frame.pack(fill="x")
        self.bars = []

    def refresh(self):
        data = cpu_mon.get_overview()
        self.overview.config(text=f"{data['percent']:.0f}% @ {data.get('freq_mhz',0):.0f} MHz | Temps: {data.get('temp_c','—')}°C")
        cores = data.get("per_core", [])
        if len(self.bars) != len(cores):
            for w in self.core_frame.winfo_children():
                w.destroy()
            self.bars = []
            for i, _ in enumerate(cores):
                row = ttk.Frame(self.core_frame)
                row.pack(fill="x", pady=2)
                ttk.Label(row, text=f"Core {i}").pack(side="left", padx=(0, 8))
                bar = ttk.Progressbar(row, length=400, maximum=100)
                bar.pack(side="left", fill="x", expand=True)
                val = ttk.Label(row, text="0%")
                val.pack(side="left", padx=8)
                self.bars.append((bar, val))
        for (bar, val), p in zip(self.bars, cores):
            bar["value"] = p
            val.config(text=f"{p:.0f}%")


class MemoryPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Memory", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        self.total = ttk.Label(self.frame, text="—")
        self.used = ttk.Label(self.frame, text="—")
        self.swap = ttk.Label(self.frame, text="—")
        self.total.pack(anchor="w", pady=4)
        self.used.pack(anchor="w", pady=4)
        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", pady=8)
        ttk.Label(self.frame, text="Swap", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.swap.pack(anchor="w", pady=4)

    def refresh(self):
        m = mem_mon.get_overview()
        self.total.config(text=f"Total: {human_bytes(m['total'])}")
        self.used.config(text=f"Used: {human_bytes(m['used'])} ({m['percent']:.0f}%)")
        s = m.get("swap", {})
        self.swap.config(text=f"Swap: {human_bytes(s.get('used', 0))}/{human_bytes(s.get('total', 0))} ({s.get('percent', 0):.0f}%)")
class DiskPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Disks", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        cols = ("Mount", "FS", "Used", "Total", "Usage")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="w")
        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        disks = disk_mon.get_disks()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for d in disks:
            self.tree.insert("", "end", values=(
                d.get("mount"), d.get("fstype"),
                human_bytes(d.get("used", 0)),
                human_bytes(d.get("total", 0)),
                f"{d.get('percent', 0):.0f}%"
            ))
class NetworkPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Network", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        self.up = ttk.Label(self.frame, text="Up: —")
        self.down = ttk.Label(self.frame, text="Down: —")
        self.up.pack(anchor="w", pady=3)
        self.down.pack(anchor="w", pady=3)

        cols = ("Interface", "IPv4", "IPv6", "Sent", "Recv")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=(6, 0))

        self._last = None

    def ingest_counters(self, net_overview: dict):
        self._last = net_overview

    def refresh(self):
        now = net_mon.get_overview()
        up_bps = now.get("tx_rate_bps", 0)
        down_bps = now.get("rx_rate_bps", 0)
        self.up.config(text=f"Up: {human_rate(up_bps)}")
        self.down.config(text=f"Down: {human_rate(down_bps)}")

        info = net_mon.get_interfaces()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for name, data in info.items():
            self.tree.insert("", "end", values=(
                name,
                ", ".join(data.get("ipv4", [])) or "—",
                ", ".join(data.get("ipv6", [])) or "—",
                human_bytes(data.get("bytes_sent", 0)),
                human_bytes(data.get("bytes_recv", 0)),
            ))
class GPUPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="GPU", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        cols = ("Name", "Load", "Mem", "Temp")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=160, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.note = ttk.Label(self.frame, text="No GPU info available.")
        self.note.pack(anchor="w", pady=6)

    def refresh(self):
        gpus = gpu_mon.get_gpus()
        for i in self.tree.get_children():
            self.tree.delete(i)

        if not gpus:
            self.note.config(text="No GPU info available or GPUtil not installed.")
            return

        self.note.config(text="")
        for g in gpus:
            self.tree.insert("", "end", values=(
                g.get("name", "GPU"),
                f"{g.get('load_percent', 0):.0f}%",
                f"{g.get('mem_used_mb', 0)}/{g.get('mem_total_mb', 0)} MB",
                f"{g.get('temp_c', '—')}°C",
            ))
