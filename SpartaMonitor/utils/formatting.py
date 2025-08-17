def human_bytes(n: int) -> str:
    # base 1024
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    x = float(n)
    for u in units:
        if x < 1024.0 or u == units[-1]:
            return f"{x:.1f} {u}" if u != "B" else f"{int(x)} {u}"
        x /= 1024.0

def human_rate(bps: float) -> str:
    # bits per second to human readable
    units = ["bps", "Kbps", "Mbps", "Gbps", "Tbps"]
    x = float(bps)
    for u in units:
        if x < 1000.0 or u == units[-1]:
            return f"{x:.1f} {u}"
        x /= 1000.0

def format_duration(seconds: int) -> str:
    s = int(seconds)
    d, rem = divmod(s, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h or d: parts.append(f"{h}h")
    if m or h or d: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)
