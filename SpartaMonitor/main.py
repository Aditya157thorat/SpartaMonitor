import sys
import time
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

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
        # Create root
        if BOOTSTRAP_OK:
            # Start on a dark theme; we'll toggle later
            self.root = tb.Window(title="SpartaMonitor", themename="darkly")
        else:
            self.root = tk.Tk()
            self.root.title("SpartaMonitor")

        self.root.geometry("1100x680")
        self.root.minsize(900, 560)

        # Base background color (falls back behind image if image fails)
        try:
            self.root.configure(bg=COLORS.get("bg_dark", "#0f172a"))
        except Exception:
            pass

        # Background PNG (kept as attribute to avoid GC)
        self._load_background("assets/background.png")

        # Fonts and styles
        self._apply_fonts()
        self._apply_styles()

        # Layout
        self._build_layout()

        # Default view
        self.sidebar.set_active("overview")
        self.dashboard.show("overview")

        # Start refresh loop
        self._running = True
        self._schedule_refresh()

        # Exit cleanly
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------
    # Setup helpers
    # ------------------------
    def _load_background(self, path: str):
        """Load a PNG background and place it behind all widgets."""
        self._bg_image = None
        try:
            self._bg_image = tk.PhotoImage(file=path)
        except Exception:
            # If missing or invalid, silently skip
            return

        self._bg_label = tk.Label(self.root, image=self._bg_image, borderwidth=0)
        # Fill the window; note: PhotoImage does not scale — ensure your PNG is large enough
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self._bg_label.lower()  # make sure it's behind everything

    def _apply_fonts(self):
        """Apply a clean, modern font globally."""
        family = "Segoe UI"  # Native to Windows 11. Alternatives: "Inter", "Poppins" if installed.
        try:
            tkfont.nametofont("TkDefaultFont").configure(family=family, size=10)
            tkfont.nametofont("TkTextFont").configure(family=family, size=10)
            tkfont.nametofont("TkFixedFont").configure(family=family, size=10)
            tkfont.nametofont("TkHeadingFont").configure(family=family, size=12, weight="bold")
        except Exception:
            pass

    def _apply_styles(self):
        """Define styles for topbar, tool buttons, and accent buttons."""
        style = ttk.Style()

        # If ttkbootstrap is present, style maps into its theme; else use built-in 'clam' for consistency
        if not BOOTSTRAP_OK:
            try:
                style.theme_use("clam")
            except Exception:
                pass

        # Palette (tweak to taste or align with your COLORS)
        bg_topbar = COLORS.get("bg_dark", "#0f172a")
        text_light = COLORS.get("text_light", "#e2e8f0")
        accent = "#2563eb"
        accent_hover = "#1d4ed8"
        accent_active = "#1e40af"

        # Topbar containers and labels
        style.configure("Topbar.TFrame", background=bg_topbar)
        style.configure("Topbar.TLabel", background=bg_topbar, foreground=text_light)

        # Small icon-only buttons (for ☰ and 🌙/☀)
        style.configure(
            "Toolbutton.TButton",
            background=bg_topbar,
            foreground=text_light,
            borderwidth=0,
            padding=(8, 6)
        )
        style.map(
            "Toolbutton.TButton",
            background=[("active", bg_topbar)],
            foreground=[("disabled", "#94a3b8")]
        )

        # Primary action buttons
        style.configure(
            "Accent.TButton",
            background=accent,
            foreground="#ffffff",
            borderwidth=0,
            padding=(14, 8)
        )
        style.map(
            "Accent.TButton",
            background=[("active", accent_hover), ("pressed", accent_active)]
        )

        # Toast styles (used in _show_popup)
        glass_bg = COLORS.get("glass_bg", "#1f2937")
        style.configure("Toast.TFrame", background=glass_bg)
        style.configure("Toast.TLabel", background=glass_bg, foreground=text_light)

    # ------------------------
    # Layout and UI
    # ------------------------
    def _build_layout(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.topbar = TopBar(
            self.root,
            on_toggle_sidebar=self._toggle_sidebar,
            on_toggle_theme=self._toggle_theme
        )
        self.topbar.frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.sidebar = Sidebar(self.root, on_nav=self._on_nav)
        self.sidebar.frame.grid(row=1, column=0, sticky="nsew")

        self.dashboard = Dashboard(self.root, notify=self._notify)
        self.dashboard.frame.grid(row=1, column=1, sticky="nsew")

        # Ensure content sits above the background image
        try:
            self.topbar.frame.lift()
            self.sidebar.frame.lift()
            self.dashboard.frame.lift()
        except Exception:
            pass

        self._sidebar_visible = True

    # ------------------------
    # Actions / interactions
    # ------------------------
    def _toggle_sidebar(self):
        if self._sidebar_visible:
            self.sidebar.frame.grid_remove()
        else:
            self.sidebar.frame.grid()
        self._sidebar_visible = not self._sidebar_visible

    def _toggle_theme(self):
        """Toggle theme (supports ttkbootstrap) and show a small toast."""
        # ttkbootstrap-aware toggle
        if BOOTSTRAP_OK:
            try:
                current = self.root.style.theme_use()
                # flip between a dark and light theme
                new_mode = "flatly" if current in ("darkly", "cyborg", "superhero", "darkly") else "darkly"
                self.root.style.theme_use(new_mode)
                self._show_popup(f"Switched to {new_mode.capitalize()} Theme")
                return
            except Exception:
                pass

        # Fallback: no theme engine — just show a toast
        self._show_popup("Theme toggled")

    def _show_popup(self, message: str):
        """Small toast near the bottom-right corner of the window."""
        try:
            # position relative to the main window
            rx, ry = self.root.winfo_rootx(), self.root.winfo_rooty()
            rw, rh = self.root.winfo_width(), self.root.winfo_height()
            # ensure geometry info is ready
            self.root.update_idletasks()
            x = rx + rw - 320
            y = ry + rh - 140
        except Exception:
            x, y = 800, 600

        top = tk.Toplevel(self.root)
        top.overrideredirect(True)
        top.attributes("-topmost", True)
        top.geometry(f"300x100+{x}+{y}")

        frm = ttk.Frame(top, style="Toast.TFrame")
        frm.pack(fill="both", expand=True)

        lbl = ttk.Label(frm, text=message, style="Toast.TLabel")
        lbl.pack(anchor="w", padx=12, pady=(12, 8))

        btn = ttk.Button(frm, text="Dismiss", style="Accent.TButton", command=top.destroy)
        btn.pack(anchor="e", padx=12, pady=(0, 12))

        # auto-dismiss
        top.after(3000, lambda: (top.winfo_exists() and top.destroy()))

    # ------------------------
    # App plumbing
    # ------------------------
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
