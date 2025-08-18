import customtkinter as ctk
import threading, time, collections

try:
    import GPUtil
    HAS_GPU = True
except Exception:
    HAS_GPU = False

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def _make_fig():
    fig = Figure(figsize=(6, 2.2), dpi=100)
    fig.patch.set_facecolor("#0F1115")
    return fig

def _add_axes(fig, ylabel="GPU %", ylim=(0, 100)):
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


class GPUPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        title = ctk.CTkLabel(self, text="🎮 GPU", font=("Segoe UI", 22, "bold"),
                             fg_color="transparent", text_color="white")
        title.pack(pady=(10, 4))

        self.summary = ctk.CTkLabel(self, text="Load: --% | Mem: --%", font=("Segoe UI", 16),
                                    fg_color="transparent", text_color="#E0E0E0")
        self.summary.pack(pady=4)

        self.hist_len = 120
        self.load_hist = collections.deque([0]*self.hist_len, maxlen=self.hist_len)
        fig = _make_fig()
        self.ax = _add_axes(fig, ylabel="GPU %", ylim=(0, 100))
        (self.load_line,) = self.ax.plot(range(self.hist_len), list(self.load_hist))
        self.canvas = _attach(fig, self)

        if HAS_GPU:
            threading.Thread(target=self._loop, daemon=True).start()
        else:
            self.summary.configure(text="No GPU detected (GPUtil not available)")

    def _loop(self):
        while True:
            try:
                gpus = GPUtil.getGPUs()
                if not gpus:
                    raise RuntimeError("No GPUs")
                g = gpus[0]
                load = g.load * 100
                mem = 0
                try:
                    mem = (g.memoryUsed / g.memoryTotal) * 100 if g.memoryTotal else 0
                except Exception:
                    pass

                self.summary.configure(text=f"Load: {load:.0f}% | Mem: {mem:.0f}%")
                self.load_hist.append(load)
                self.load_line.set_ydata(list(self.load_hist))
                self.canvas.draw_idle()
            except Exception:
                self.summary.configure(text="GPU info unavailable")
            finally:
                time.sleep(1)
