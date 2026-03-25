import os
import psutil
import glob

def get_system_snapshot():
    gpu_pct, vram_gb = 0, 0.0
    try:
        cards = glob.glob('/sys/class/drm/card*/device/gpu_busy_percent')
        for card in cards:
            with open(card, 'r') as f: pct = int(f.read().strip())
            v_path = card.replace('gpu_busy_percent', 'mem_info_vram_used')
            v_gb = 0.0
            if os.path.exists(v_path):
                with open(v_path, 'r') as f: v_gb = round(int(f.read().strip()) / (1024**3), 1)
            if v_gb > 0 or len(cards) == 1:
                gpu_pct, vram_gb = pct, v_gb
                break
    except: pass
    ram_gb = round(psutil.virtual_memory().used / (1024**3), 1)
    return vram_gb, ram_gb, gpu_pct

class Profiler:
    def __init__(self): pass
    def start(self): pass
    def stop_and_save(self, p, r): return 0.0, ""
