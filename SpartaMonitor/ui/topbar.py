import ttkbootstrap as ttk
from ttkbootstrap.constants import *

print("[debug] loading topbar.py")

def fmt_uptime(sec: int) -> str:
    d = sec // 86400
    h = (sec % 86400) // 3600
    m = (sec % 3600) // 60
    if d: return f"{d}d {h}h {m}m"
    if h: return f"{h}h {m}m"
    return f"{m}m"

class TopBar:
    def __init__(self, master):
        self.frame = ttk.Frame(master, bootstyle=SECONDARY)
        self.frame.configure(padding=(10, 6))

        # Left: sidebar toggle
        self.toggle_btn = ttk.Button(self.frame, text="☰", width=3, bootstyle=(DARK, OUTLINE))
        self.toggle_btn.pack(side="left")
        self.on_toggle_sidebar = None
        self.toggle_btn.configure(command=self._toggle_clicked)

        # Right: battery + uptime + alert icon
        self.battery_label = ttk.Label(self.frame, text="⚡ --%")
        self.uptime_label = ttk.Label(self.frame, text="⏳ --m")
        self.alert_label = ttk.Label(self.frame, text="")  # can show 🔔 on alerts

        self.alert_label.pack(side="right", padx=6)
        self.uptime_label.pack(side="right", padx=6)
        self.battery_label.pack(side="right", padx=6)

    def _toggle_clicked(self):
        if self.on_toggle_sidebar:
            self.on_toggle_sidebar()

    def update_battery(self, batt):
        if batt is None:
            self.battery_label.configure(text="⚡ N/A")
            return
        plug = "🔌" if getattr(batt, "power_plugged", False) else "🔋"
        pct = getattr(batt, "percent", None)
        pct_text = "--" if pct is None else int(pct)
        self.battery_label.configure(text=f"{plug} {pct_text}%")

    def update_uptime(self, secs: int):
        self.uptime_label.configure(text=f"⏳ {fmt_uptime(secs)}")

    def show_alert_icon(self, show: bool):
        self.alert_label.configure(text="🔔" if show else "")
