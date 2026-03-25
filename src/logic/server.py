from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import requests
import time
import json
import os
import re
import urllib.parse
import psutil
import glob
import uvicorn
import logging

# --- 1. SISTEMA DE LOGS MASSIVO ---
LOG_FILE = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/neural_os.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler() # Imprime no terminal também
    ]
)
logger = logging.getLogger("NeuralOS")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BRAVE_PATH = "/usr/bin/brave-browser"
BRAVE_USER_DATA = os.path.expanduser("~/.config/brave-browser")
MODEL_NAME = "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M"
OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"
DB_FILE = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/vagas_vistas.json")
KANBAN_DB = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/kanban_state.json")

BOT_STATE = {"running": False}

logger.info("🟢 === NEURAL OS BACKEND INICIADO ===")

# --- 2. TELEMETRIA (MONITOR) ---
@app.get("/stats")
def get_stats():
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
    return {"vram": vram_gb, "gpu": gpu_pct, "ram": round(psutil.virtual_memory().used / (1024**3), 1)}

# --- 3. KANBAN (PERSISTÊNCIA DE DADOS) ---
@app.post("/sync_kanban")
async def sync_kanban(request: Request):
    try:
        data = await request.json()
        with open(KANBAN_DB, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"❌ Erro a salvar o Kanban: {e}")
        return {"error": str(e)}

# --- 4. CHAT IA (LIGAÇÃO AO OLLAMA) ---
class ChatRequest(BaseModel):
    messages: list
    systemInstruction: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    logger.info(f"💬 Pedido de Chat recebido! ({len(req.messages)} mensagens no contexto)")
    
    def generate():
        formatted_msgs =[{"role": "system", "content": req.systemInstruction}]
        for m in req.messages:
            formatted_msgs.append({"role": m["role"], "content": m["parts"][0]["text"]})
            
        payload = {"model": MODEL_NAME, "messages": formatted_msgs, "stream": True, "options": {"num_ctx": 4096}}
        logger.info(f"🧠 Enviando prompt para o Ollama ({OLLAMA_CHAT_URL})...")
        
        try:
            with requests.post(OLLAMA_CHAT_URL, json=payload, stream=True, timeout=10) as r:
                if r.status_code != 200:
                    logger.error(f"❌ Ollama recusou: HTTP {r.status_code} - {r.text}")
                    yield f"\n❌[ERRO BACKEND]: O Ollama recusou a conexão. Código: {r.status_code}"
                    return

                logger.info("✅ Resposta do Ollama iniciada. A fazer stream para a UI...")
                for line in r.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
                logger.info("🏁 Resposta do Chat concluída com sucesso.")
        
        except requests.exceptions.ConnectionError:
            logger.error("❌ FATAL: Ollama desligado ou porto 11434 inacessível.")
            yield "\n❌[ERRO OLLAMA DESLIGADO]: Não consegui falar com a tua 7900 XTX. O `ollama serve` está a rodar?"
        except Exception as e:
            logger.error(f"❌ ERRO DESCONHECIDO NO CHAT: {str(e)}")
            yield f"\n❌ [ERRO INTERNO PYTHON]: {str(e)}"
            
    return StreamingResponse(generate(), media_type="text/plain")

# --- 5. LINKEDIN HUNTER ---
def load_seen_jobs():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return set(json.load(f))
        except: return set()
    return set()

def save_seen_jobs(seen_set):
    with open(DB_FILE, 'w') as f: json.dump(list(seen_set), f)

@app.get("/stop")
def stop_bot():
    logger.info("🛑 Ordem de paragem recebida do Frontend.")
    BOT_STATE["running"] = False
    return {"status": "Parando..."}

def bot_generator(keyword, location, max_hours):
    driver = None
    seen_jobs = load_seen_jobs()
    BOT_STATE["running"] = True
    BLACKLIST =["cgi", "deloitte", "kpmg", "pwc", "accenture", "kcs", "inetum", "aubay", "primeit", "bold", "capgemini", "talan", "novabase", "glintt", "outsystems", "mindera", "dellent"]
    
    try:
        yield "data: " + json.dumps({"log": f"🚀 Crawler Iniciado. Vagas memorizadas: {len(seen_jobs)}."}) + "\n\n"
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument(f"--user-data-dir={BRAVE_USER_DATA}")
        options.add_argument("--profile-directory=Default")
        driver = uc.Chrome(options=options, browser_executable_path=BRAVE_PATH, use_subprocess=True)
        
        start_page_index = 0
        approved_count = 0

        while BOT_STATE["running"]:
            url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(keyword)}&location={urllib.parse.quote(location)}&start={start_page_index}"
            yield "data: " + json.dumps({"log": f"📄 Carregando Página {int(start_page_index/25) + 1}..."}) + "\n\n"
            driver.get(url)
            time.sleep(5)

            for step in range(1, 11):
                if not BOT_STATE["running"]: break
                driver.execute_script(f"let p = document.querySelector('.jobs-search-results-list'); if(p) p.scrollTop = p.scrollHeight * ({step}/10);")
                time.sleep(0.8)

            cards = driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
            if not cards: break

            for card in cards:
                if not BOT_STATE["running"]: break
                try:
                    job_id = card.get_attribute("data-job-id")
                    if not job_id or job_id in seen_jobs: continue

                    seen_jobs.add(job_id)
                    save_seen_jobs(seen_jobs)

                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(0.5)

                    title = card.find_element(By.CSS_SELECTOR, ".job-card-list__title, .artdeco-entity-lockup__title").text.split('\n')[0].strip()
                    company = card.find_element(By.CSS_SELECTOR, ".job-card-container__primary-description").text.split('\n')[0].strip()
                    try: link = card.find_element(By.TAG_NAME, "a").get_attribute("href").split("?")[0]
                    except: link = f"https://www.linkedin.com/jobs/view/{job_id}/"

                    if any(b in company.lower() for b in BLACKLIST): continue

                    time_text = re.search(r'(\d+)\s*(min|hor|hour|h|dia|day|d|seman|week|w|mês|mes|month|m)\b', card.text.lower())
                    time_text = time_text.group() if time_text else "desconhecido"
                    
                    def parse_h(t):
                        if any(x in t for x in["agora", "now"]): return 0
                        m = re.search(r'\d+', t)
                        if not m: return 0
                        v = int(m.group())
                        if any(x in t for x in["hor","h"]): return v
                        if any(x in t for x in["dia","d"]): return v * 24
                        if any(x in t for x in["seman","w"]): return v * 24 * 7
                        return v
                    
                    if parse_h(time_text) > max_hours: continue

                    card.click()
                    time.sleep(2)
                    
                    try: right_panel = driver.find_element(By.CSS_SELECTOR, ".jobs-search__job-details--container").text.lower()
                    except: right_panel = ""
                    if "candidatou-se" in right_panel or "applied" in right_panel: continue

                    try: description = driver.find_element(By.CSS_SELECTOR, ".jobs-description__content").text.strip()
                    except: description = ""

                    yield "data: " + json.dumps({"log": f"🧐 Analisando: {company} ({time_text})..."}) + "\n\n"

                    prompt = f"Vaga: {title}\nEmpresa: {company}\nDescrição: {description[:1200]}\nO candidato é Developer. REJEITA se for Consultora, Outsourcing, Liderança (Team Lead/Manager), Suporte ou se exigir Inglês Nativo/Excelente. Se for Cliente Final para Developer com inglês normal, responde: APROVADO. Senão: REJEITADO -[Motivo]."
                    
                    res = requests.post("http://127.0.0.1:11434/api/generate", json={"model": MODEL_NAME, "prompt": prompt, "stream": False}, timeout=60)
                    decision = res.json().get("response", "").strip().upper()

                    if "APROVADO" in decision:
                        approved_count += 1
                        yield "data: " + json.dumps({"job": {"company": company, "title": title, "link": link}}) + "\n\n"
                        yield "data: " + json.dumps({"log": f"✅ APROVADO ({approved_count}): {company}"}) + "\n\n"
                    else:
                        yield "data: " + json.dumps({"log": f"❌ FILTRADO ({decision.replace('REJEITADO', '').strip(' -:')[:40]}): {company}"}) + "\n\n"
                        
                except Exception as e:
                    if "connection" in str(e).lower(): raise e
                    continue

            start_page_index += 25

        yield "data: " + json.dumps({"log": f"✨ Concluído. {approved_count} vagas mineradas."}) + "\n\n"
    except Exception as e:
        logger.error(f"Erro Fatal no Bot: {e}")
        yield "data: " + json.dumps({"log": f"⚠️ Erro ou paragem forçada."}) + "\n\n"
    finally:
        BOT_STATE["running"] = False
        if driver:
            try: driver.quit()
            except: pass

@app.get("/hunt")
def hunt(keyword: str = "Senior Java", location: str = "Grande Lisboa", max_hours: int = 72):
    logger.info("🤖 Recebido comando para iniciar mineração do LinkedIn.")
    return StreamingResponse(bot_generator(keyword, location, max_hours), media_type="text/event-stream")

if __name__ == "__main__":
    logger.info("🌐 Uvicorn preparado. Escutando no porto 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
