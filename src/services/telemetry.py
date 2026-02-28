import threading
import time
import json
import os
import psutil
from datetime import datetime
from src.config import LOGS_DIR

def get_system_snapshot():
    """Tira uma 'fotografia' instantânea do hardware para a UI"""
    try:
        with open('/sys/class/drm/card0/device/gpu_busy_percent', 'r') as f:
            gpu_pct = int(f.read().strip())
        with open('/sys/class/drm/card0/device/mem_info_vram_used', 'r') as f:
            vram_used = int(f.read().strip())
        vram_gb = round(vram_used / (1024**3), 1)
    except:
        gpu_pct, vram_gb = 0, 0.0
        
    ram_gb = round(psutil.virtual_memory().used / (1024**3), 1)
    return vram_gb, ram_gb, gpu_pct

class Profiler:
    def __init__(self):
        self.log_dir = LOGS_DIR
        os.makedirs(self.log_dir, exist_ok=True)
        self.is_running = False
        self.stats_log =[]
        self.thread = None
        self.start_time = 0

    def start(self):
        self.is_running = True
        self.stats_log =[]
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.start()

    def _monitor_loop(self):
        while self.is_running:
            vram_gb, ram_gb, gpu_pct = get_system_snapshot()
            self.stats_log.append({
                "time_offset": round(time.time() - self.start_time, 1),
                "cpu_%": psutil.cpu_percent(),
                "gpu_%": gpu_pct,
                "vram_gb": vram_gb
            })
            time.sleep(1)

    def stop_and_save(self, prompt, response):
        self.is_running = False
        if self.thread: self.thread.join()
        elapsed = round(time.time() - self.start_time, 2)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_time_sec": elapsed,
            "input": prompt,
            "telemetry": self.stats_log
        }
        filepath = os.path.join(self.log_dir, f"prompt_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, indent=4, ensure_ascii=False)
        except: pass
        return elapsed, filepath
