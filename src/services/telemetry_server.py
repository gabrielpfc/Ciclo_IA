from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psutil, glob, os, json, uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

KANBAN_DATA_PATH = "/home/user/Documentos/Repos/Ciclo_IA/storage/kanban_state.json"

@app.get("/stats")
def get_stats():
    gpu_pct, vram_gb = 0, 0.0
    try:
        # Leitura direta AMD GPU
        cards = glob.glob('/sys/class/drm/card*/device/gpu_busy_percent')
        for card in cards:
            with open(card, 'r') as f: pct = int(f.read().strip())
            v_path = card.replace('gpu_busy_percent', 'mem_info_vram_used')
            if os.path.exists(v_path):
                with open(v_path, 'r') as f: v_gb = round(int(f.read().strip()) / (1024**3), 1)
            gpu_pct, vram_gb = pct, v_gb
            break
    except: pass
    return {"vram": vram_gb, "gpu": gpu_pct, "ram": round(psutil.virtual_memory().used / (1024**3), 1)}

@app.post("/sync_kanban")
async def sync_kanban(request: Request):
    data = await request.json()
    os.makedirs(os.path.dirname(KANBAN_DATA_PATH), exist_ok=True)
    with open(KANBAN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return {"status": "synced"}

@app.get("/mentions")
def get_mentions():
    if not os.path.exists(KANBAN_DATA_PATH): return []
    try:
        with open(KANBAN_DATA_PATH, "r") as f: data = json.load(f)
        mentions = []
        for s in data.get("sprints", []):
            mentions.append({"key": s['name'], "value": f"#[SPRINT:{s['id']}]", "display": f"📅 {s['name']}"})
        for t in data.get("tasks", []):
            code = t.get('code', t['id'][:4].upper())
            mentions.append({"key": t['title'], "value": f"#[TASK:{t['id']}]", "display": f"✅ {code}: {t['title']}"})
        return mentions
    except: return []

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
