import time
import psutil

_last = {
    "t": None,
    "bytes_sent": 0,
    "bytes_recv": 0,
}

def get_overview():
    # global rates across all interfaces
    global _last
    now = time.time()
    io = psutil.net_io_counters()
    if _last["t"] is None:
        _last.update({"t": now, "bytes_sent": io.bytes_sent, "bytes_recv": io.bytes_recv})
        tx_rate = rx_rate = 0.0
    else:
        dt = max(1e-6, now - _last["t"])
        tx_rate = (io.bytes_sent - _last["bytes_sent"]) * 8.0 / dt  # bits per sec
        rx_rate = (io.bytes_recv - _last["bytes_recv"]) * 8.0 / dt
        _last.update({"t": now, "bytes_sent": io.bytes_sent, "bytes_recv": io.bytes_recv})

    return {
        "tx_rate_bps": tx_rate,
        "rx_rate_bps": rx_rate,
        "bytes_sent": io.bytes_sent,
        "bytes_recv": io.bytes_recv,
    }

def get_interfaces():
    addrs = psutil.net_if_addrs()
    ios = psutil.net_io_counters(pernic=True)
    info = {}
    for name, addr_list in addrs.items():
        ipv4 = [a.address for a in addr_list if a.family.name == "AF_INET"]
        ipv6 = [a.address for a in addr_list if a.family.name == "AF_INET6"]
        io = ios.get(name)
        info[name] = {
            "ipv4": ipv4,
            "ipv6": ipv6,
            "bytes_sent": io.bytes_sent if io else 0,
            "bytes_recv": io.bytes_recv if io else 0,
        }
    return info
