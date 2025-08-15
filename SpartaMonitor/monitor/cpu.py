import psutil

def get_core_usage():
    """Return list of per-core CPU percentages (safe)."""
    try:
        return psutil.cpu_percent(percpu=True)
    except Exception as e:
        print(f"[monitor.cpu] get_core_usage error: {e}")
        try:
            return [0.0] * psutil.cpu_count(logical=True)
        except Exception:
            return [0.0]

def get_core_temperatures():
    """Return list of core temps if available, else None."""
    try:
        if not hasattr(psutil, "sensors_temperatures"):
            return None
        sensor_data = psutil.sensors_temperatures() or {}
        # common keys: coretemp, cpu-thermal, k10temp, acpitz etc.
        for key in ("coretemp", "cpu-thermal", "k10temp", "acpitz"):
            if key in sensor_data:
                try:
                    temps = [float(t.current) for t in sensor_data[key] if hasattr(t, "current")]
                    return temps if temps else None
                except Exception:
                    continue
        # try any available sensor list
        for _, v in sensor_data.items():
            try:
                temps = [float(t.current) for t in v if hasattr(t, "current")]
                if temps:
                    return temps
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"[monitor.cpu] get_core_temperatures error: {e}")
        return None
