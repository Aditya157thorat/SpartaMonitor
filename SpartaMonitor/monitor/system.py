import time
import platform
import psutil

def get_overview():
    boot = psutil.boot_time()
    uptime = max(0, int(time.time() - boot))
    batt = None
    try:
        b = psutil.sensors_battery()
        if b:
            batt = {"percent": int(b.percent), "plugged": bool(b.power_plugged)}
    except Exception:
        batt = None

    return {
        "uptime_seconds": uptime,
        "battery": batt,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        }
    }
