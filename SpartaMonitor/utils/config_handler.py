import json
from pathlib import Path

DEFAULTS = {
    "theme": "darkly",
    "refresh_rate": 1000,
    "temp_threshold": 85,
    "heavy_cpu_threshold": 85,
    "heavy_cpu_ticks": 8,
    "window_size": "900x700",
    "sidebar_width": 220
}

def _cfg_path(path=None):
    if path:
        return Path(path)
    return Path(__file__).resolve().parents[1] / "config.json"

def load_config(path=None):
    path = _cfg_path(path)
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
    except Exception as e:
        print(f"[config_handler] Error reading config {path}: {e}")
        data = {}
    for k, v in DEFAULTS.items():
        data.setdefault(k, v)
    return data

def save_config(data, path=None):
    path = _cfg_path(path)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[config_handler] Saved config to {path}")
    except Exception as e:
        print(f"[config_handler] Error saving config {path}: {e}")
