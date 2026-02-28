import threading
import time
import json
import os
import psutil
from datetime import datetime
from src.config import LOGS_DIR

class Profiler:
    def __init__(self):
        self.log_dir = LOGS_DIR
        # Garante que a pasta existe (se a permissão do disco estiver ok)
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.is_running = False
        self.stats_log = []
        self.thread = None
        self.start_time = 0

    def _get_amd_gpu_stats(self):
        """Lê os sensores da AMD diretamente do Kernel do Linux"""
        try:
            # Uso da GPU (0-100)
            with open('/sys/class/drm/card0/device/gpu_busy_percent', 'r') as f:
                gpu_pct = int(f.read().strip())
                
            # VRAM Usada e Total (em bytes)
            with open('/sys/class/drm/card0/device/mem_info_vram_used', 'r') as f:
                vram_used = int(f.read().strip())
            with open('/sys/class/drm/card0/device/mem_info_vram_total', 'r') as f:
                vram_total = int(f.read().strip())
                
            vram_pct = round((vram_used / vram_total) * 100, 1)
            vram_gb = round(vram_used / (1024**3), 2)
            
            return gpu_pct, vram_pct, vram_gb
        except:
            return 0, 0, 0.0

    def _monitor_loop(self):
        while self.is_running:
            gpu_pct, vram_pct, vram_gb = self._get_amd_gpu_stats()
            cpu_pct = psutil.cpu_percent()
            ram_pct = psutil.virtual_memory().percent
            
            self.stats_log.append({
                "time_offset": round(time.time() - self.start_time, 1),
                "cpu_%": cpu_pct,
                "ram_%": ram_pct,
                "gpu_%": gpu_pct,
                "vram_%": vram_pct,
                "vram_gb": vram_gb
            })
            time.sleep(1) # Amostra a cada 1 segundo para maior precisão

    def start(self):
        self.is_running = True
        self.stats_log = []
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.start()

    def stop_and_save(self, prompt, response):
        self.is_running = False
        if self.thread:
            self.thread.join()
            
        elapsed_time = round(time.time() - self.start_time, 2)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_time_sec": elapsed_time,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "input": prompt,
            "output": response,
            "telemetry": self.stats_log
        }
        
        filename = f"prompt_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"ERRO AO SALVAR LOG: {e}")
            
        return elapsed_time, filepath
