import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import traceback
from typing import Optional
from pathlib import Path

print("[debug] loading dashboard.py")

class Dashboard:
    def __init__(self, master, config, notifier, theme_change_cb: Optional[callable]=None, config_path: Optional[Path]=None):
        self.master = master
        self.config = config
        self.notifier = notifier
        self.theme_change_cb = theme_change_cb
        self.config_path = config_path

        # Expose frame that main can pack
        self.frame = ttk.Frame(master)
        self.frame.pack_propagate(False)

        # Panels map (created lazily)
        self.panels = {}
        self.active_key = None
        self._high_cpu_ticks = 0

        # Caches for widgets
        self.cpu_labels, self.cpu_bars = [], []
        self.temp_labels, self.temp_bars = [], []
        self.disk_rows = []
        self.disk_container = None
        self.ram_label = None
        self.ram_bar = None
        self.ram_detail = None
        self.gpu_label = None

        # Settings vars
        self.settings_vars = {}

        print("[dashboard] init complete")

    # --- panel creators (lazy) ---
    def _create_cpu_panel(self):
        from monitor.cpu import get_core_usage
        f = ttk.Frame(self.frame)
        ttk.Label(f, text="CPU Usage per Core", font=("Segoe UI", 16, "bold")).pack(pady=6)
        self.cpu_labels, self.cpu_bars = [], []
        try:
            cores = len(get_core_usage()) or 4
        except Exception:
            cores = 4
        for i in range(cores):
            row = ttk.Frame(f); row.pack(pady=2, fill="x")
            lbl = ttk.Label(row, text=f"Core {i+1}: 0%"); lbl.pack(side="left")
            bar = ttk.Progressbar(row, length=340, mode="determinate", bootstyle=INFO); bar.pack(side="left", padx=6)
            self.cpu_labels.append(lbl); self.cpu_bars.append(bar)
        return f

    def _create_ram_panel(self):
        f = ttk.Frame(self.frame)
        ttk.Label(f, text="RAM Usage", font=("Segoe UI", 16, "bold")).pack(pady=6)
        self.ram_label = ttk.Label(f, text="0%"); self.ram_label.pack()
        self.ram_bar = ttk.Progressbar(f, length=420, mode="determinate", bootstyle=SUCCESS); self.ram_bar.pack(pady=2)
        self.ram_detail = ttk.Label(f, text=""); self.ram_detail.pack(pady=4)
        return f

    def _create_temp_panel(self):
        f = ttk.Frame(self.frame)
        ttk.Label(f, text="Core Temperatures", font=("Segoe UI", 16, "bold")).pack(pady=6)
        self.temp_labels, self.temp_bars = [], []
        # Start with 4 rows; will fill values when available
        for i in range(4):
            row = ttk.Frame(f); row.pack(pady=2)
            lbl = ttk.Label(row, text=f"Core {i+1}: N/A"); lbl.pack(side="left")
            bar = ttk.Progressbar(row, length=340, mode="determinate", bootstyle=DANGER); bar.pack(side="left", padx=6)
            self.temp_labels.append(lbl); self.temp_bars.append(bar)
        return f

    def _create_disk_panel(self):
        f = ttk.Frame(self.frame)
        ttk.Label(f, text="Disk Usage", font=("Segoe UI", 16, "bold")).pack(pady=6)
        self.disk_container = ttk.Frame(f)
        self.disk_container.pack(fill="x")
        self.disk_rows = []
        return f

    def _create_gpu_panel(self):
        f = ttk.Frame(self.frame)
        ttk.Label(f, text="GPU Stats", font=("Segoe UI", 16, "bold")).pack(pady=6)
        self.gpu_label = ttk.Label(f, text="N/A"); self.gpu_label.pack()
        return f

    def _create_settings_panel(self):
        from utils.config_handler import save_config
        f = ttk.Frame(self.frame)
        ttk.Label(f, text="Settings", font=("Segoe UI", 16, "bold")).pack(pady=6)

        themes = ["darkly", "superhero", "morph", "flatly", "journal", "lumen"]

        theme_var = tk.StringVar(value=self.config.get("theme"))
        rr_var = tk.IntVar(value=self.config.get("refresh_rate"))
        tthr_var = tk.IntVar(value=self.config.get("temp_threshold", 85))
        hcpu_var = tk.IntVar(value=self.config.get("heavy_cpu_threshold", 85))
        hticks_var = tk.IntVar(value=self.config.get("heavy_cpu_ticks", 8))
        self.settings_vars.update(theme=theme_var, refresh_rate=rr_var,
                                  temp_threshold=tthr_var, heavy_cpu_threshold=hcpu_var,
                                  heavy_cpu_ticks=hticks_var)

        ttk.Label(f, text="Theme").pack(anchor="w")
        theme_cb = ttk.Combobox(f, values=themes, textvariable=theme_var); theme_cb.pack(fill="x", pady=4)

        ttk.Label(f, text="Refresh Rate (ms)").pack(anchor="w")
        ttk.Entry(f, textvariable=rr_var).pack(fill="x", pady=4)

        ttk.Label(f, text="Temperature Threshold °C").pack(anchor="w")
        ttk.Entry(f, textvariable=tthr_var).pack(fill="x", pady=4)

        ttk.Label(f, text="Heavy CPU Threshold (%)").pack(anchor="w")
        ttk.Entry(f, textvariable=hcpu_var).pack(fill="x", pady=4)

        ttk.Label(f, text="Heavy CPU Ticks").pack(anchor="w")
        ttk.Entry(f, textvariable=hticks_var).pack(fill="x", pady=4)

        ttk.Button(f, text="Save Settings", bootstyle=SUCCESS,
                   command=lambda: self._save_settings(save_config)).pack(pady=10)
        return f

    def _save_settings(self, save_config_func):
        try:
            for k, var in self.settings_vars.items():
                self.config[k] = var.get()
            save_config_func(self.config, path=self.config_path)
            if self.theme_change_cb:
                try:
                    self.theme_change_cb(self.config["theme"])
                except Exception:
                    pass
            self.notifier.show("Settings saved. Theme applied.", bootstyle=INFO)
        except Exception:
            traceback.print_exc()

    # --- show / animation ---
    def show(self, key: str, animate=True):
        try:
            if key not in self.panels:
                creator = {
                    "cpu": self._create_cpu_panel,
                    "ram": self._create_ram_panel,
                    "temp": self._create_temp_panel,
                    "disk": self._create_disk_panel,
                    "gpu": self._create_gpu_panel,
                    "settings": self._create_settings_panel,
                }.get(key)
                if creator:
                    self.panels[key] = creator()
            # hide current
            if self.active_key and self.active_key in self.panels:
                try:
                    self.panels[self.active_key].pack_forget()
                except Exception:
                    pass
            pane = self.panels.get(key)
            if pane:
                pane.pack(fill="both", expand=True, padx=12, pady=12)

            # Simple fade (optional)
            if animate:
                try:
                    cover = tk.Canvas(self.frame, highlightthickness=0)
                    cover.place(relx=0, rely=0, relwidth=1, relheight=1)
                    supported_stipples = ["gray12", "gray25", "gray50", "gray75"]
                    steps = len(supported_stipples)
                    def step(i=steps-1):
                        cover.delete("rect")
                        if i < 0:
                            cover.destroy()
                            return
                        w = max(1, self.frame.winfo_width())
                        h = max(1, self.frame.winfo_height())
                        stip = supported_stipples[max(0, min(i, steps-1))]
                        try:
                            cover.create_rectangle(0, 0, w, h, fill="#000", stipple=stip, tags="rect")
                        except Exception:
                            cover.create_rectangle(0, 0, w, h, fill="#000", tags="rect")
                        cover.after(30, step, i-1)
                    step()
                except Exception:
                    traceback.print_exc()

            self.active_key = key
        except Exception:
            traceback.print_exc()

    # --- refresh loop ---
    def refresh(self):
        try:
            if self.active_key == "cpu" and "cpu" in self.panels:
                from monitor.cpu import get_core_usage
                core = get_core_usage() or []
                for i, v in enumerate(core):
                    if i >= len(self.cpu_labels): break
                    self.cpu_labels[i].configure(text=f"Core {i+1}: {v:.0f}%")
                    self.cpu_bars[i]["value"] = v
                if core:
                    avg = sum(core) / max(len(core), 1)
                    if avg >= self.config.get("heavy_cpu_threshold", 85):
                        self._high_cpu_ticks += 1
                    else:
                        self._high_cpu_ticks = 0
                    if self._high_cpu_ticks >= self.config.get("heavy_cpu_ticks", 8):
                        self.notifier.heavy_task(avg)
                        self._high_cpu_ticks = 0

            elif self.active_key == "ram" and "ram" in self.panels:
                from monitor.memory import get_ram_usage, get_memory_detail
                pct = get_ram_usage()
                used, total = get_memory_detail()
                if self.ram_label: self.ram_label.configure(text=f"{pct:.0f}%")
                if self.ram_bar: self.ram_bar["value"] = pct
                if self.ram_detail: self.ram_detail.configure(text=f"Used: {used} / Total: {total}")

            elif self.active_key == "temp" and "temp" in self.panels:
                from monitor.cpu import get_core_temperatures
                temps = get_core_temperatures() or []
                for i, t in enumerate(temps):
                    if i >= len(self.temp_labels): break
                    self.temp_labels[i].configure(text=f"Core {i+1}: {t:.1f}°C")
                    self.temp_bars[i]["value"] = min(max(t, 0), 100)
                    if t >= self.config.get("temp_threshold", 85):
                        self.notifier.high_temp(t)
                # Clear remaining rows if fewer temps than rows
                for j in range(len(temps), len(self.temp_labels)):
                    self.temp_labels[j].configure(text=f"Core {j+1}: N/A")
                    self.temp_bars[j]["value"] = 0

            elif self.active_key == "disk" and "disk" in self.panels:
                from monitor.disk import get_disks
                disks = get_disks()
                if self.disk_container is not None:
                    if (not self.disk_rows) or (len(self.disk_rows) != len(disks)):
                        # rebuild rows
                        for child in self.disk_container.winfo_children():
                            child.destroy()
                        self.disk_rows = []
                        for d in disks:
                            row = ttk.Frame(self.disk_container); row.pack(fill="x", pady=2)
                            ttk.Label(row, text=d["mount"]).pack(side="left", padx=4)
                            bar = ttk.Progressbar(row, length=320, mode="determinate", bootstyle=SECONDARY); bar.pack(side="left", padx=6)
                            lbl = ttk.Label(row, text=f'{d["used_gb"]} / {d["total_gb"]} GB'); lbl.pack(side="left")
                            self.disk_rows.append((bar, lbl))
                for (bar, lbl), d in zip(self.disk_rows, disks):
                    bar["value"] = d["percent"]
                    lbl.configure(text=f'{d["used_gb"]} / {d["total_gb"]} GB  ({d["percent"]:.0f}%)')

            elif self.active_key == "gpu" and "gpu" in self.panels:
                from monitor.gpu import get_gpu_summary
                info = get_gpu_summary() or "GPU: N/A"
                if self.gpu_label: self.gpu_label.configure(text=info)

            # settings panel has no periodic refresh
        except Exception:
            traceback.print_exc()
