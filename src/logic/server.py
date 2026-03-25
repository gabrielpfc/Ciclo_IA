from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import requests, time, json, os, re, urllib.parse, psutil, glob, uvicorn, logging

# Logs Redundantes
LOG_FILE = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/neural_os.log")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger("NeuralOS")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BRAVE_PATH = "/usr/bin/brave-browser"
BRAVE_USER_DATA = os.path.expanduser("~/.config/brave-browser")
MODEL_NAME = "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M"
OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"
CHATS_DB = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/conversas.json")
KANBAN_DB = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/kanban_state.json")
VAGAS_DB = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/vagas_vistas.json")

BOT_STATE = {"running": False}

@app.get("/stats")
def get_stats():
    gpu_pct, vram_gb = 0, 0.0
    try:
        cards = glob.glob('/sys/class/drm/card*/device/gpu_busy_percent')
        for card in cards:
            with open(card, 'r') as f: pct = int(f.read().strip())
            v_path = card.replace('gpu_busy_percent', 'mem_info_vram_used')
            if os.path.exists(v_path):
                with open(v_path, 'r') as f: vram_gb = round(int(f.read().strip()) / (1024**3), 1)
            gpu_pct = pct
            if vram_gb > 0: break
    except: pass
    return {"vram": vram_gb, "gpu": gpu_pct, "ram": round(psutil.virtual_memory().used / (1024**3), 1)}

@app.get("/load_chats")
def load_chats():
    if os.path.exists(CHATS_DB):
        with open(CHATS_DB, 'r', encoding='utf-8') as f: return json.load(f)
    return []

@app.post("/save_chats")
async def save_chats(request: Request):
    data = await request.json()
    with open(CHATS_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}

@app.post("/sync_kanban")
async def sync_kanban(request: Request):
    data = await request.json()
    with open(KANBAN_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}

class ChatRequest(BaseModel):
    messages: list
    systemInstruction: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    def generate():
        payload = {"model": MODEL_NAME, "messages": [{"role": "system", "content": req.systemInstruction}] + [
            {"role": m["role"], "content": m["parts"][0]["text"]} for m in req.messages
        ], "stream": True}
        try:
            with requests.post(OLLAMA_CHAT_URL, json=payload, stream=True, timeout=120) as r:
                for line in r.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
        except Exception as e:
            yield f"❌ Erro Ollama: {str(e)}"
    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/tts")
def tts_endpoint(req: dict):
    try:
        from src.services.voice_engine import generate_speech
        generate_speech(req['text'], lang=req.get('lang', 'en'))
        return {"status": "ok"}
    except: return {"status": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
