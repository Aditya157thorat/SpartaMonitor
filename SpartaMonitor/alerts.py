import ttkbootstrap as ttk
from ttkbootstrap.constants import *

print("[debug] loading alerts.py")

class Notifier:
    """Lightweight in-app toast notifications (top-right)."""
    def __init__(self, root):
        self.root = root
        self.toasts = []

    def show(self, message: str, bootstyle=WARNING, duration=5000):
        toast = ttk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)

        try:
            self.root.update_idletasks()
        except Exception:
            pass

        x = self.root.winfo_x() + self.root.winfo_width() - 340
        y = self.root.winfo_y() + 64 + (len(self.toasts) * 70)
        toast.geometry(f"320x60+{x}+{y}")

        frame = ttk.Frame(toast, padding=10, bootstyle=bootstyle)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Notification", font=("-size", 10, "bold")).pack(anchor="w")
        ttk.Label(frame, text=message, wraplength=300).pack(anchor="w")

        self.toasts.append(toast)

        def dismiss():
            if toast in self.toasts:
                self.toasts.remove(toast)
            try:
                toast.destroy()
            except Exception:
                pass

        toast.after(duration, dismiss)

    # Convenience helpers
    def high_temp(self, value):
        self.show(f"Core temperature high: {value:.1f}°C", bootstyle=DANGER)

    def heavy_task(self, value):
        self.show(f"Sustained high CPU load: {value:.0f}%", bootstyle=WARNING)
