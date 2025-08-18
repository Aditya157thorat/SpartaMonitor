import customtkinter as ctk
import psutil, threading, time, collections, socket

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def _make_fig():
    fig = Figure(figsize=(6, 2.2), dpi=100)
    fig.patch.set_facecolor("#0F1115")
    return fig

def _add_axes(fig, ylabel="KB/s", ylim=(0, 10000)):
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

def _get_ip():
    ip = "-"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
    return ip


class NetworkPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        title = ctk.CTkLabel(self, text="📶 Network", font=("Segoe UI", 22, "bold"),
                             fg_color="transparent", text_color="white")
        title.pack(pady=(10, 4))

        self.summary = ctk.CTkLabel(self, text=f"IP: {_get_ip()} | ⬆ -- KB/s ⬇ -- KB/s",
                                    font=("Segoe UI", 16), fg_color="transparent", text_color="#E0E0E0")
        self.summary.pack(pady=4)

        self.hist_len = 120
        self.up_hist = collections.deque([0]*self.hist_len, maxlen=self.hist_len)
        self.down_hist = collections.deque([0]*self.hist_len, maxlen=self.hist_len)

        fig = _make_fig()
        self.ax = _add_axes(fig, ylabel="KB/s", ylim=(0, 100000))
        (self.up_line,) = self.ax.plot(range(self.hist_len), list(self.up_hist), label="up")
        (self.down_line,) = self.ax.plot(range(self.hist_len), list(self.down_hist), label="down")
        self.ax.legend(facecolor="#0F1115", edgecolor="#444", labelcolor="#E0E0E0")
        self.canvas = _attach(fig, self)

        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        old = psutil.net_io_counters()
        ip = _get_ip()
        while True:
            time.sleep(1)
            new = psutil.net_io_counters()
            up = (new.bytes_sent - old.bytes_sent) / 1024
            down = (new.bytes_recv - old.bytes_recv) / 1024
            old = new

            self.up_hist.append(up)
            self.down_hist.append(down)
            self.up_line.set_ydata(list(self.up_hist))
            self.down_line.set_ydata(list(self.down_hist))
            self.canvas.draw_idle()
            self.summary.configure(text=f"IP: {ip} | ⬆ {up:.1f} KB/s ⬇ {down:.1f} KB/s")
