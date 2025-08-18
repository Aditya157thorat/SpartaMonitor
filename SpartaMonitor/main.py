import customtkinter as ctk
from PIL import Image

# Existing UI
from ui.sidebar import Sidebar
from ui.topbar import TopBarFrame
from ui.dashboard import DashboardFrame

# NEW page UIs
from ui.cpu_page import CPUPage
from ui.memory_page import MemoryPage
from ui.disk_page import DiskPage
from ui.network_page import NetworkPage
from ui.gpu_page import GPUPage


class SpartaMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sparta Monitor ⚔️")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ✅ Background image (covers whole window)
        self.bg_image = ctk.CTkImage(
            light_image=Image.open("assets/bacg.png"),
            dark_image=Image.open("assets/bacg.png"),
            size=(1600, 900)  # make sure this is >= your window size
        )
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bg_label.lower()  # always behind everything

        # Layout config
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, controller=self, fg_color="transparent")
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsw")

        # Topbar
        self.topbar = TopBarFrame(self, fg_color="transparent")
        self.topbar.grid(row=0, column=1, sticky="new")

        # Container for pages
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=1, column=1, sticky="nsew")

        # Pages
        self.frames = {
            "Dashboard": DashboardFrame(self.container, fg_color="transparent"),
            "CPU": CPUPage(self.container, fg_color="transparent"),
            "Memory": MemoryPage(self.container, fg_color="transparent"),
            "Disk": DiskPage(self.container, fg_color="transparent"),
            "Network": NetworkPage(self.container, fg_color="transparent"),
            "GPU": GPUPage(self.container, fg_color="transparent"),
        }
        for f in self.frames.values():
            f.grid(row=0, column=0, sticky="nsew")

        # Show Dashboard by default
        self.show_frame("Dashboard")

    def show_frame(self, name: str):
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
            if hasattr(self.sidebar, "set_active"):
                self.sidebar.set_active(name)


if __name__ == "__main__":
    app = SpartaMonitorApp()
    app.mainloop()
