import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.configure(fg_color="#111111")  # solid dark background instead of image
        self.buttons = {}

        # ✅ Button style
        btn_style = {
            "font": ("Segoe UI", 18, "bold"),
            "height": 44,
            "corner_radius": 10,
            "fg_color": "#1a1a1a",   # dark button look
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
            self.buttons[key] = btn

        # ✅ Footer
        self.footer = ctk.CTkLabel(
            self,
            text="Sparta ©",
            text_color="#8A8A8A",
            fg_color="transparent"
        )
        self.footer.pack(side="bottom", pady=12)

        self.active_key = None

    def set_active(self, key: str):
        if self.active_key and self.active_key in self.buttons:
            self.buttons[self.active_key].configure(fg_color="#1a1a1a")
        if key in self.buttons:
            self.buttons[key].configure(fg_color="#2563EB")  # active blue
            self.active_key = key
