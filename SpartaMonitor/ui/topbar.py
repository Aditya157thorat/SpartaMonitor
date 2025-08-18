import customtkinter as ctk
import psutil, time, threading, datetime

class TopBarFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#1a1a1a")  # dark glass effect

        # Title
        self.label = ctk.CTkLabel(self, text="⚔️ Sparta Monitor",
                                  font=("Segoe UI", 24, "bold"),
                                  fg_color="transparent", text_color="white")
        self.label.pack(side="left", padx=20, pady=10)

        # Right cluster (battery, clock, info)
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=10)

        self.battery_label = ctk.CTkLabel(right, text="", font=("Segoe UI", 16),
                                          fg_color="transparent", text_color="lightgray")
        self.battery_label.pack(side="right", padx=10)

        self.clock_label = ctk.CTkLabel(right, text="🕒 --:--", font=("Segoe UI", 16),
                                        fg_color="transparent", text_color="lightgray")
        self.clock_label.pack(side="right", padx=10)

        self.info_label = ctk.CTkLabel(right, text="Loading...", font=("Segoe UI", 16),
                                       fg_color="transparent", text_color="white")
        self.info_label.pack(side="right", padx=10)

        self.old_values = {"cpu": 0, "mem": 0}
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _flash_label(self, label: ctk.CTkLabel, color: str, ms: int = 300):
        orig = label.cget("text_color")
        label.configure(text_color=color)
        self.after(ms, lambda: label.configure(text_color=orig))

    def _update_loop(self):
        while True:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - psutil.boot_time()))
            self.info_label.configure(text=f"🖥️ {cpu}% | 💾 {mem}% | ⏱️ {uptime}")

            now = datetime.datetime.now().strftime("%H:%M:%S")
            self.clock_label.configure(text=f"🕒 {now}")

            try:
                battery = psutil.sensors_battery()
                if battery:
                    percent = battery.percent
                    plugged = " 🔌" if battery.power_plugged else ""
                    self.battery_label.configure(text=f"🔋 {percent:.0f}%{plugged}")
                    if percent < 20 and not battery.power_plugged:
                        self._flash_label(self.battery_label, "red")
                else:
                    self.battery_label.configure(text="")
            except Exception:
                self.battery_label.configure(text="")

            # Flash on spikes
            diffs = {"cpu": cpu - self.old_values["cpu"], "mem": mem - self.old_values["mem"]}
            for k, d in diffs.items():
                if abs(d) > 10:
                    self._flash_label(self.info_label, "red" if d > 0 else "green")
            self.old_values["cpu"], self.old_values["mem"] = cpu, mem
