import psutil

def get_overview():
    percent = psutil.cpu_percent(interval=None)
    freq = psutil.cpu_freq()
    per_core = psutil.cpu_percent(interval=None, percpu=True) or []
    try:
        temps = psutil.sensors_temperatures()
        # pick first CPU-related sensor if available
        cpu_temps = next((v for k, v in temps.items() if "cpu" in k.lower() or "core" in k.lower()), [])
        temp_c = cpu_temps[0].current if cpu_temps else None
    except Exception:
        temp_c = None

    return {
        "percent": percent,
        "per_core": per_core,
        "cores_logical": psutil.cpu_count(),
        "cores_physical": psutil.cpu_count(logical=False) or psutil.cpu_count(),
        "freq_mhz": freq.current if freq else None,
        "temp_c": temp_c,
    }
