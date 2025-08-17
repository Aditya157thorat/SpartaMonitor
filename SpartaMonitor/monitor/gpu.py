def get_gpus():
    try:
        import GPUtil
    except Exception:
        return []

    try:
        gpus = GPUtil.getGPUs()
    except Exception:
        return []

    result = []
    for g in gpus:
        result.append({
            "id": g.id,
            "name": g.name,
            "load_percent": float(g.load) * 100.0 if g.load is not None else 0.0,
            "mem_total_mb": int(g.memoryTotal),
            "mem_used_mb": int(g.memoryUsed),
            "temp_c": getattr(g, "temperature", None),
        })
    return result
