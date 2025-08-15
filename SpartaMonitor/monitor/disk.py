def get_gpu_summary():
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if not gpus:
            return "GPU: N/A"
        g = gpus[0]
        name = getattr(g, "name", "GPU")
        load = getattr(g, "load", 0) * 100
        mem_used = getattr(g, "memoryUsed", 0)
        mem_total = getattr(g, "memoryTotal", 0)
        temp = getattr(g, "temperature", None)
        temp_str = f" | Temp {temp:.0f}°C" if temp is not None else ""
        return f"GPU: {name} | Load {load:.0f}% | Mem {mem_used:.0f}/{mem_total:.0f} MB{temp_str}"
    except Exception:
        # GPUtil not available or no GPU
        return "GPU: N/A"
