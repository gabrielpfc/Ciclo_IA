from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests, time, json, os, psutil, glob, uvicorn, asyncio, queue, threading

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STORAGE_PATH = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/storage")
os.makedirs(STORAGE_PATH, exist_ok=True)

CHATS_DB = os.path.join(STORAGE_PATH, "conversas.json")
HISTORY_DB = os.path.join(STORAGE_PATH, "job_history.json")
MINED_JOBS_DB = os.path.join(STORAGE_PATH, "mined_jobs.json")

MODEL_NAME = "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M"
OLLAMA_URL = "http://127.0.0.1:11434/api"

BOT_STATE = {"status": "stopped"}
MSG_STATE = {"status": "stopped"}

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f: 
            try: return json.load(f)
            except: return {} if "history" in path else[]
    return {} if "history" in path else[]

@app.get("/stats")
def get_stats(): return {"vram": 0.0, "gpu": 0, "ram": 0.0}

@app.get("/load_chats")
def load_chats(): return load_json(CHATS_DB)

@app.post("/save_chats")
async def save_chats(request: Request):
    data = await request.json()
    with open(CHATS_DB, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}

class ChatRequest(BaseModel):
    messages: list
    systemInstruction: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    def generate():
        payload = {"model": MODEL_NAME, "messages": [{"role": "system", "content": req.systemInstruction}] + [{"role": m["role"], "content": m["parts"][0]["text"]} for m in req.messages], "stream": True}
        try:
            with requests.post(f"{OLLAMA_URL}/chat", json=payload, stream=True, timeout=120) as r:
                for line in r.iter_lines():
                    if line: yield json.loads(line)["message"]["content"]
        except Exception as e: yield f"❌ Erro Ollama: {str(e)}"
    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/generate_title")
async def generate_title(request: Request):
    return {"title": "Conversa"}

@app.post("/tts")
async def tts_endpoint(request: Request):
    return {"status": "ok"}

@app.post("/stt")
async def stt_endpoint(request: Request):
    return {"text": "STT Offline"}

@app.get("/get_mined_jobs")
def get_mined_jobs(): return load_json(MINED_JOBS_DB)

@app.get("/get_history")
def get_history(): return load_json(HISTORY_DB)

@app.get("/clear_mined_jobs")
def clear_mined_jobs():
    with open(MINED_JOBS_DB, 'w') as f: json.dump([], f)
    return {"status": "ok"}

@app.post("/track_click")
async def track_click(request: Request):
    req = await request.json()
    link = req.get("link")
    history = load_json(HISTORY_DB)
    history[link] = history.get(link, 0) + 1
    with open(HISTORY_DB, 'w') as f: json.dump(history, f)
    return {"count": history[link]}

@app.get("/hunt")
async def hunt_endpoint(keyword: str, location: str, max_hours: int, enforce_location: bool = False):
    BOT_STATE["status"] = "running"
    q = queue.Queue()
    from src.logic.bot_logic import start_linkedin_bot
    def worker():
        current_jobs = load_json(MINED_JOBS_DB)
        if not isinstance(current_jobs, list): current_jobs = []
        seen = {j['link'] for j in current_jobs}
        for event in start_linkedin_bot(keyword, location, max_hours, enforce_location, BOT_STATE):
            if event.get("job"):
                if event["job"]["link"] not in seen:
                    current_jobs.insert(0, event["job"])
                    seen.add(event["job"]["link"])
                    with open(MINED_JOBS_DB, 'w') as f: json.dump(current_jobs[:150], f, indent=2)
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

@app.get("/scan_messages")
async def scan_messages_endpoint():
    MSG_STATE["status"] = "running"
    q = queue.Queue()
    from src.logic.bot_logic import scan_linkedin_messages
    def worker():
        for event in scan_linkedin_messages(MSG_STATE):
            q.put(event)
            if MSG_STATE["status"] == "stopped": break
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
def pause_bot(): BOT_STATE["status"] = "paused"; return {"status": "paused"}
@app.get("/resume")
def resume_bot(): BOT_STATE["status"] = "running"; return {"status": "running"}
@app.get("/stop")
def stop_hunt(): BOT_STATE["status"] = "stopped"; return {"status": "stopped"}
@app.get("/stop_messages")
def stop_messages(): MSG_STATE["status"] = "stopped"; return {"status": "stopped"}

if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8000)
