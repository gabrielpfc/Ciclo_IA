from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests, time, json, os, psutil, glob, uvicorn, asyncio, queue, threading

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- CONFIGURAÇÃO DE STORAGE (PROTEGIDO CONTRA GIT RESET) ---
STORAGE_PATH = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/storage")
os.makedirs(STORAGE_PATH, exist_ok=True)

CHATS_DB = os.path.join(STORAGE_PATH, "conversas.json")
HISTORY_DB = os.path.join(STORAGE_PATH, "job_history.json")
MINED_JOBS_DB = os.path.join(STORAGE_PATH, "mined_jobs.json")

MODEL_NAME = "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

# ESTADO DO BOT: "stopped", "running", "paused"
BOT_STATE = {"status": "stopped"}

class ChatRequest(BaseModel):
    messages: list
    systemInstruction: str

# --- ENDPOINTS DE TELEMETRIA ---
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
            break
    except: pass
    return {"vram": vram_gb, "gpu": gpu_pct, "ram": round(psutil.virtual_memory().used / (1024**3), 1)}

# --- ENDPOINTS DE CHAT (RESTAURADOS) ---
@app.get("/load_chats")
def load_chats():
    if os.path.exists(CHATS_DB):
        with open(CHATS_DB, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return []
    return []

@app.post("/save_chats")
async def save_chats(request: Request):
    data = await request.json()
    with open(CHATS_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}

@app.post("/generate_title")
async def generate_title(request: Request):
    req = await request.json()
    prompt = req.get('prompt', '')[:150]
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": f"Resume em 3 palavras sem aspas: {prompt}"}],
        "stream": False
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=10)
        title = r.json()['message']['content'].strip().replace('"', '')
        return {"title": title}
    except: return {"title": "Conversa"}

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    def generate():
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "system", "content": req.systemInstruction}] + [
                {"role": m["role"], "content": m["parts"][0]["text"]} for m in req.messages
            ],
            "stream": True
        }
        try:
            with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as r:
                for line in r.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        yield chunk["message"]["content"]
        except Exception as e:
            yield f"❌ Erro Ollama: {str(e)}"
    return StreamingResponse(generate(), media_type="text/plain")

# --- ENDPOINTS DE VOZ ---
@app.post("/tts")
async def tts_endpoint(request: Request):
    req = await request.json()
    try:
        from src.services.voice_engine import generate_speech
        generate_speech(req['text'], lang=req.get('lang', 'en'))
        return {"status": "ok"}
    except: return {"status": "error"}

@app.post("/stt")
async def stt_endpoint(request: Request):
    from src.services.stt_engine import transcribe_audio
    body = await request.body()
    temp_path = os.path.join(STORAGE_PATH, "temp_rec.wav")
    with open(temp_path, "wb") as f: f.write(body)
    text, lang = transcribe_audio(temp_path)
    return {"text": text}

# --- ENDPOINTS DO LINKEDIN HUNTER (UNIFICADOS) ---
@app.get("/get_mined_jobs")
def get_mined_jobs():
    if os.path.exists(MINED_JOBS_DB):
        with open(MINED_JOBS_DB, 'r') as f: return json.load(f)
    return []

@app.get("/get_history")
def get_history():
    if os.path.exists(HISTORY_DB):
        with open(HISTORY_DB, 'r') as f: return json.load(f)
    return {}

@app.post("/track_click")
async def track_click(request: Request):
    req = await request.json()
    link = req.get("link")
    history = {}
    if os.path.exists(HISTORY_DB):
        with open(HISTORY_DB, 'r') as f: history = json.load(f)
    history[link] = history.get(link, 0) + 1
    with open(HISTORY_DB, 'w') as f: json.dump(history, f)
    return {"count": history[link]}

@app.get("/hunt")
async def hunt_endpoint(keyword: str, location: str, max_hours: int):
    BOT_STATE["status"] = "running"
    q = queue.Queue()
    from src.logic.bot_logic import start_linkedin_bot
    
    def worker():
        # Carrega vagas já salvas para evitar duplicados
        mined = []
        if os.path.exists(MINED_JOBS_DB):
            with open(MINED_JOBS_DB, 'r') as f: mined = json.load(f)
        
        seen_links = {j['link'] for j in mined}

        for event in start_linkedin_bot(keyword, location, max_hours, BOT_STATE):
            if event.get("job"):
                if event["job"]["link"] not in seen_links:
                    mined.insert(0, event["job"])
                    seen_links.add(event["job"]["link"])
                    with open(MINED_JOBS_DB, 'w') as f: json.dump(mined[:100], f, indent=2)
            
            q.put(event)
            if BOT_STATE["status"] == "stopped": break
        q.put(None)

    threading.Thread(target=worker, daemon=True).start()

    async def stream():
        while True:
            try:
                ev = q.get_nowait()
                if ev is None: break
                yield f"data: {json.dumps(ev)}\n\n"
            except: await asyncio.sleep(0.5)
    return StreamingResponse(stream(), media_type="text/event-stream")

@app.get("/pause")
def pause_bot():
    BOT_STATE["status"] = "paused"
    return {"status": "paused"}

@app.get("/resume")
def resume_bot():
    BOT_STATE["status"] = "running"
    return {"status": "running"}

@app.get("/stop")
def stop_hunt():
    BOT_STATE["status"] = "stopped"
    return {"status": "stopped"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
