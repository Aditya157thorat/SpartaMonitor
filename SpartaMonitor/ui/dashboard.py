import customtkinter as ctk
from PIL import Image
import psutil, threading, time

try:
    import GPUtil
    HAS_GPU = True
except ImportError:
    HAS_GPU = False


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # ✅ Background image stretched properly
        self.bg_image = ctk.CTkImage(
            light_image=Image.open("assets/bacg.png"),
            dark_image=Image.open("assets/bacg.png"),
            size=(1600, 900)  # cover large screens
        )
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bg_label.lower()  # background always behind

        # ✅ Dashboard title
        self.title_label = ctk.CTkLabel(
            self,
            text="📊 System Overview",
            font=("Segoe UI", 26, "bold"),
            text_color="white"
        )
        self.title_label.pack(pady=20)
        self.title_label.lift()

        # ✅ Cards container
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Info cards
        self.cpu_label = self.create_card("🖥 CPU", "Loading...", 0, 0)
        self.mem_label = self.create_card("💾 Memory", "Loading...", 0, 1)
        self.disk_label = self.create_card("💽 Disk", "Loading...", 0, 2)
        self.net_label = self.create_card("🌐 Network", "Loading...", 1, 0)
        self.gpu_label = self.create_card("🎮 GPU", "Loading...", 1, 1)
        self.temp_label = self.create_card("🌡 CPU Temp", "Loading...", 1, 2)

        # ✅ Start background thread for stats
        threading.Thread(target=self.update_stats, daemon=True).start()

    def create_card(self, title, value, row, col):
        """Reusable system info card with glassy effect"""
        frame = ctk.CTkFrame(
            self.cards_frame,
            corner_radius=15,
            fg_color="#1a1a1a"  # semi-dark glass illusion
        )
        frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color="lightgray"
        )
        title_label.pack(pady=(15, 5))

        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=("Segoe UI", 22),
            text_color="white"
        )
        value_label.pack(pady=(0, 15))

        frame.lift()
        return value_label

    def update_stats(self):
        old_sent = psutil.net_io_counters().bytes_sent
        old_recv = psutil.net_io_counters().bytes_recv

        while True:
            # CPU, RAM, Disk
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent

            # Network
            new_sent = psutil.net_io_counters().bytes_sent
            new_recv = psutil.net_io_counters().bytes_recv
            up_speed = (new_sent - old_sent) / 1024
            down_speed = (new_recv - old_recv) / 1024
            old_sent, old_recv = new_sent, new_recv

            # GPU
            gpu = 0
            if HAS_GPU:
                try:
                    gpus = GPUtil.getGPUs()
                    gpu = gpus[0].load * 100 if gpus else 0
                except Exception:
                    gpu = 0

            # CPU Temp
            temp = "N/A"
            try:
                temps = psutil.sensors_temperatures()
                if "coretemp" in temps:
                    temp = f"{temps['coretemp'][0].current:.1f}°C"
                elif temps:
                    first = list(temps.values())[0]
                    if first:
                        temp = f"{first[0].current:.1f}°C"
            except Exception:
                temp = "N/A"

            # Update UI
            self.cpu_label.configure(text=f"{cpu}%")
            self.mem_label.configure(text=f"{mem}%")
            self.disk_label.configure(text=f"{disk}%")
            self.net_label.configure(text=f"⬆ {up_speed:.1f} KB/s | ⬇ {down_speed:.1f} KB/s")
            self.gpu_label.configure(text=f"{gpu:.1f}%")
            self.temp_label.configure(text=temp)
