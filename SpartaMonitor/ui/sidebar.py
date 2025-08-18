import customtkinter as ctk
from PIL import Image

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        self.buttons = {}

        # ✅ Background image
        self.bg_image = ctk.CTkImage(
            light_image=Image.open("assets/bacg.png"),
            dark_image=Image.open("assets/bacg.png"),
            size=(300, 900)  # adjust sidebar size, not full 1600px
        )
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bg_label.lower()  # send behind widgets

        # ✅ Button style
        btn_style = {
            "font": ("Segoe UI", 18, "bold"),
            "height": 44,
            "corner_radius": 10,
            "fg_color": "#1a1a1a",   # dark glass effect
            "hover_color": ("#3B82F6", "#3B82F6"),
            "anchor": "w",
            "text_color": ("#EAEAEA", "#EAEAEA"),
        }

        items = [
            ("Dashboard", "📊 Dashboard"),
            ("CPU", "🖥️ CPU"),
            ("Memory", "💾 Memory"),
            ("Disk", "📀 Disk"),
            ("Network", "📶 Network"),
            ("GPU", "🎮 GPU"),
        ]

        for key, label in items:
            btn = ctk.CTkButton(
                self,
                text=label,
                command=lambda k=key: self.controller.show_frame(k),
                **btn_style
            )
            btn.pack(padx=12, pady=8, fill="x")
            btn.lift()  # ✅ force above background
            self.buttons[key] = btn

        # ✅ Footer
        self.footer = ctk.CTkLabel(
            self,
            text="Sparta ©",
            text_color="#8A8A8A",
            fg_color="transparent"
        )
        self.footer.pack(side="bottom", pady=12)
        self.footer.lift()  # ✅ keep above background

        self.active_key = None

    def set_active(self, key: str):
        if self.active_key and self.active_key in self.buttons:
            self.buttons[self.active_key].configure(fg_color="#1a1a1a")
        if key in self.buttons:
            self.buttons[key].configure(fg_color="#2563EB")  # active blue
            self.active_key = key
