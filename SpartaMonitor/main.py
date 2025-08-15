# main.py
import sys
import traceback
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

print("[debug] loading alerts.py")
from alerts import Alerts
from topbar import TopBar
from sidebar import Sidebar
from dashboard import Dashboard
from utils.config_handler import load_config
from utils.theme import COLORS

CONFIG_PATH = Path(__file__).parent / "config.json"


class SpartaMonitorApp:
    def __init__(self):
        print("Launching SpartaMonitor...")

        self.config = load_config(CONFIG_PATH)
        self.app = ttk.Window(themename=self.config["theme"])
        self.app.title("SpartaMonitor")
        self.app.geometry(self.config.get("window_size", "800x800"))
        self.app.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load background (optional)
        self._load_background()

        # UI Components
        print("[main] Starting SpartaMonitorApp init")
        self.topbar = TopBar(self.app)
        self.topbar.frame.pack(fill=X)
        print("[main] TopBar created")

        self.sidebar = Sidebar(self.app, width=self.config.get("sidebar_width", 220), on_nav=self._on_nav)
        self.sidebar.frame.pack(side=LEFT, fill=Y)
        print("[main] Sidebar created")

        self.dashboard = Dashboard(master=self.app, config=self.config, notifier=Alerts())
        print("[main] Dashboard created")

        # Start refresh loop
        self._schedule_refresh()

        print("[main] Init complete")

    def _load_background(self):
        bg_path = Path(__file__).parent / "assets" / "bg.png"
        if bg_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(bg_path)
                self.bg_image = ImageTk.PhotoImage(img)
                label = ttk.Label(self.app, image=self.bg_image)
                label.place(x=0, y=0, relwidth=1, relheight=1)
                print(f"[main] Loaded background: {bg_path}")
            except Exception as e:
                print(f"[main] bg.png load failed, using fallback: {e}")
        else:
            print("[main] bg.png not found, skipping background.")

    def _on_nav(self, key):
        if hasattr(self.dashboard, "show"):
            self.dashboard.show(key, animate=False)

    def _schedule_refresh(self):
        try:
            if hasattr(self.dashboard, "refresh"):
                self.dashboard.refresh()
        except Exception as e:
            print("[main] Dashboard refresh failed:")
            traceback.print_exc()

        # Schedule again
        self.app.after(self.config.get("refresh_rate", 1000), self._schedule_refresh)

    def run(self):
        print("[main] SpartaMonitorApp constructed, running mainloop...")
        self.app.mainloop()

    def on_close(self):
        print("[main] Closing SpartaMonitorApp...")
        self.app.destroy()
        sys.exit(0)


if __name__ == "__main__":
    SpartaMonitorApp().run()
