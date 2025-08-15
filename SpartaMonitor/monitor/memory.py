import psutil

def get_ram_usage():
    try:
        return psutil.virtual_memory().percent
    except Exception as e:
        print(f"[monitor.memory] get_ram_usage error: {e}")
        return 0.0

def get_memory_detail():
    try:
        vm = psutil.virtual_memory()
        used = _fmt_bytes(vm.used)
        total = _fmt_bytes(vm.total)
        return used, total
    except Exception as e:
        print(f"[monitor.memory] get_memory_detail error: {e}")
        return "0B", "0B"

def _fmt_bytes(n):
    try:
        n = float(n)
    except Exception:
        return "0B"
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"
