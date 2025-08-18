import customtkinter as ctk
import psutil, threading, time, collections
from monitor.cpu import get_overview  # uses your existing backend

# Matplotlib embed helpers
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
    widget = canvas.get_tk_widget()
    widget.configure(highlightthickness=0, bd=0, bg="#0F1115")
    widget.pack(fill="x", padx=10, pady=8)
    return canvas


class CPUPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        title = ctk.CTkLabel(self, text="🖥️ CPU", font=("Segoe UI", 22, "bold"),
                             fg_color="transparent", text_color="white")
        title.pack(pady=(10, 4))

        self.summary = ctk.CTkLabel(self, text="Usage: --% | Freq: -- MHz | Temp: --°C",
                                    font=("Segoe UI", 16), fg_color="transparent", text_color="#E0E0E0")
        self.summary.pack(pady=(0, 8))

        # Per-core usage list
        self.core_list = ctk.CTkScrollableFrame(self, fg_color=("gray10", "gray15"), height=180)
        self.core_list.pack(fill="x", padx=10, pady=8)
        self.core_labels = []
        for i in range(psutil.cpu_count(logical=True)):
            lbl = ctk.CTkLabel(self.core_list, text=f"Core {i}: --%",
                               font=("Segoe UI", 14), fg_color="transparent", text_color="white")
            lbl.pack(anchor="w", padx=10, pady=2)
            self.core_labels.append(lbl)

        # Usage graph
        self.hist_len = 120
        self.cpu_hist = collections.deque([0]*self.hist_len, maxlen=self.hist_len)
        fig = _make_fig()
        self.ax = _add_axes(fig, ylabel="CPU %", ylim=(0, 100))
        (self.line,) = self.ax.plot(range(self.hist_len), list(self.cpu_hist))
        self.canvas = _attach(fig, self)

        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            info = get_overview()
            usage = info["percent"]
            freq = info["freq_mhz"] if info["freq_mhz"] is not None else 0
            temp = info["temp_c"]
            per_core = info["per_core"]

            self.summary.configure(
                text=f"Usage: {usage:.0f}% | Freq: {freq:.0f} MHz | Temp: {temp:.1f}°C" if temp is not None
                     else f"Usage: {usage:.0f}% | Freq: {freq:.0f} MHz | Temp: N/A"
            )

            for i, v in enumerate(per_core):
                if i < len(self.core_labels):
                    self.core_labels[i].configure(text=f"Core {i}: {v:.0f}%")

            self.cpu_hist.append(usage)
            self.line.set_ydata(list(self.cpu_hist))
            self.canvas.draw_idle()
            time.sleep(1)
