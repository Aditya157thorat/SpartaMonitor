import customtkinter as ctk
import psutil, threading, time, collections

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def _make_fig():
    fig = Figure(figsize=(6, 2.2), dpi=100)
    fig.patch.set_facecolor("#0F1115")
    return fig

def _add_axes(fig, ylabel="%", ylim=(0, 100)):
    ax = fig.add_subplot(111)
    ax.set_facecolor("#0F1115")
    ax.tick_params(colors="#BFBFBF")
    for s in ax.spines.values():
        s.set_color("#444")
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel, color="#E0E0E0")
    ax.grid(True, alpha=0.15, color="#888", linestyle="--")
    return ax

def _attach(fig, parent):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    w = canvas.get_tk_widget()
    w.configure(highlightthickness=0, bd=0, bg="#0F1115")
    w.pack(fill="x", padx=10, pady=8)
    return canvas


class MemoryPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        title = ctk.CTkLabel(self, text="💾 Memory", font=("Segoe UI", 22, "bold"),
                             fg_color="transparent", text_color="white")
        title.pack(pady=(10, 4))

        self.summary = ctk.CTkLabel(self, text="Used: -- / --  ( --% )",
                                    font=("Segoe UI", 16), fg_color="transparent", text_color="#E0E0E0")
        self.summary.pack(pady=4)

        self.bar = ctk.CTkProgressBar(self, height=18)
        self.bar.set(0)
        self.bar.pack(fill="x", padx=12, pady=8)

        self.hist_len = 120
        self.mem_hist = collections.deque([0]*self.hist_len, maxlen=self.hist_len)
        fig = _make_fig()
        self.ax = _add_axes(fig, ylabel="RAM %", ylim=(0, 100))
        (self.line,) = self.ax.plot(range(self.hist_len), list(self.mem_hist))
        self.canvas = _attach(fig, self)

        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            v = psutil.virtual_memory()
            used_gb = (v.total - v.available) / (1024**3)
            total_gb = v.total / (1024**3)
            self.summary.configure(text=f"Used: {used_gb:.2f} / {total_gb:.2f} GB  ( {v.percent:.0f}% )")
            self.bar.set(v.percent / 100)

            self.mem_hist.append(v.percent)
            self.line.set_ydata(list(self.mem_hist))
            self.canvas.draw_idle()
            time.sleep(1)
