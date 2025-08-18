import customtkinter as ctk
import psutil, threading, time, collections

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def _make_fig():
    fig = Figure(figsize=(6, 2.2), dpi=100)
    fig.patch.set_facecolor("#0F1115")
    return fig

def _add_axes(fig, ylabel="KB/s", ylim=(0, 5000)):
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


class DiskPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        title = ctk.CTkLabel(self, text="📀 Disk", font=("Segoe UI", 22, "bold"),
                             fg_color="transparent", text_color="white")
        title.pack(pady=(10, 4))

        # Partitions list
        self.parts_frame = ctk.CTkScrollableFrame(self, fg_color=("gray10", "gray15"), height=220)
        self.parts_frame.pack(fill="x", padx=10, pady=8)
        self.part_widgets = []

        # IO graph
        self.hist_len = 120
        self.r_hist = collections.deque([0]*self.hist_len, maxlen=self.hist_len)
        self.w_hist = collections.deque([0]*self.hist_len, maxlen=self.hist_len)
        fig = _make_fig()
        self.ax = _add_axes(fig, ylabel="KB/s", ylim=(0, 50000))
        (self.r_line,) = self.ax.plot(range(self.hist_len), list(self.r_hist), label="read")
        (self.w_line,) = self.ax.plot(range(self.hist_len), list(self.w_hist), label="write")
        self.ax.legend(facecolor="#0F1115", edgecolor="#444", labelcolor="#E0E0E0")
        self.canvas = _attach(fig, self)

        threading.Thread(target=self._loop, daemon=True).start()

    def _refresh_partitions(self):
        for w in self.part_widgets:
            w.destroy()
        self.part_widgets.clear()

        for p in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(p.mountpoint)
            except Exception:
                continue
            row = ctk.CTkFrame(self.parts_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=6)

            name = ctk.CTkLabel(row, text=f"{p.device} ({p.mountpoint})", font=("Segoe UI", 14, "bold"),
                                fg_color="transparent", text_color="white")
            name.pack(side="left")

            percent = usage.percent / 100
            bar = ctk.CTkProgressBar(row, height=14); bar.set(percent)
            bar.pack(side="right", fill="x", expand=True, padx=10)
            val = ctk.CTkLabel(row, text=f"{usage.percent:.0f}%", fg_color="transparent", text_color="#D0D0D0")
            val.pack(side="right", padx=8)
            self.part_widgets += [row, name, bar, val]

    def _loop(self):
        self._refresh_partitions()
        old = psutil.disk_io_counters()
        while True:
            time.sleep(1)
            new = psutil.disk_io_counters()
            r = (new.read_bytes - old.read_bytes) / 1024
            w = (new.write_bytes - old.write_bytes) / 1024
            old = new

            self.r_hist.append(r)
            self.w_hist.append(w)
            self.r_line.set_ydata(list(self.r_hist))
            self.w_line.set_ydata(list(self.w_hist))
            self.canvas.draw_idle()
