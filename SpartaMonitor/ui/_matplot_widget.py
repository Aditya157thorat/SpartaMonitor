from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def make_figure(width=6, height=2.2, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    fig.patch.set_facecolor("#0F1115")  # dark bg to match CTk
    return fig

def add_line_axes(fig, ylabel="%", ylim=(0, 100)):
    ax = fig.add_subplot(111)
    ax.set_facecolor("#0F1115")
    ax.tick_params(colors="#BFBFBF")
    for spine in ax.spines.values():
        spine.set_color("#444")
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel, color="#E0E0E0")
    ax.grid(True, alpha=0.15, color="#888", linestyle="--")
    return ax

def attach(fig, parent):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.configure(highlightthickness=0, bd=0, bg="#0F1115")
    widget.pack(fill="x", padx=10, pady=8)
    return canvas
