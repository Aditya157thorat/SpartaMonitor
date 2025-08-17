import psutil

def get_disks():
    disks = []
    seen = set()
    for p in psutil.disk_partitions(all=False):
        # skip duplicates and pseudo filesystems
        key = (p.device, p.mountpoint)
        if key in seen:
            continue
        seen.add(key)
        try:
            usage = psutil.disk_usage(p.mountpoint)
        except Exception:
            # some mounts might be inaccessible
            continue
        disks.append({
            "device": p.device,
            "mount": p.mountpoint,
            "fstype": p.fstype,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent,
        })
    return disks
    