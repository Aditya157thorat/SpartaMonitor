import sys
import time
import traceback
import tkinter as tk
from tkinter import ttk

# Optional: ttkbootstrap
try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import LEFT, RIGHT, TOP, BOTTOM, BOTH, X, Y
    BOOTSTRAP_OK = True
except Exception:
    BOOTSTRAP_OK = False
    LEFT, RIGHT, TOP, BOTTOM, BOTH, X, Y = "left", "right", "top", "bottom", "both", "x", "y"

from ui.topbar import TopBar
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from utils.theme import COLORS


class App:
    def __init__(self):
        if BOOTSTRAP_OK:
            self.root = tb.Window(title="SpartaMonitor", themename="darkly")
        else:
            self.root = tk.Tk()
            self.root.title("SpartaMonitor")

        self.root.geometry("1100x680")
        self.root.minsize(900, 560)
        try:
            self.root.configure(bg=COLORS["bg_dark"])
        except Exception:
            pass

        self._build_layout()

        # Default view
        self.sidebar.set_active("overview")
        self.dashboard.show("overview")

        # Start refresh loop
        self._running = True
        self._schedule_refresh()

        # Exit cleanly
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.topbar = TopBar(self.root, on_toggle_sidebar=self._toggle_sidebar)
        self.topbar.frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.sidebar = Sidebar(self.root, on_nav=self._on_nav)
        self.sidebar.frame.grid(row=1, column=0, sticky="nsew")

        self.dashboard = Dashboard(self.root, notify=self._notify)
        self.dashboard.frame.grid(row=1, column=1, sticky="nsew")

        self._sidebar_visible = True

    def _toggle_sidebar(self):
        if self._sidebar_visible:
            self.sidebar.frame.grid_remove()
        else:
            self.sidebar.frame.grid()
        self._sidebar_visible = not self._sidebar_visible

    def _on_nav(self, key: str):
        self.sidebar.set_active(key)
        self.dashboard.show(key)

    def _schedule_refresh(self):
        if not self._running:
            return
        try:
            metrics = self.dashboard.refresh()  # returns summary dict
            self.topbar.update_system(metrics.get("system", {}))
        except Exception:
            # Keep the app alive even if a panel had an issue
            traceback.print_exc(file=sys.stderr)
        finally:
            self.root.after(1000, self._schedule_refresh)

    def _notify(self, level: str, message: str):
        # forward to topbar to flash bell and show toast-like popup
        self.topbar.alert(level, message)

    def _on_close(self):
        self._running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
