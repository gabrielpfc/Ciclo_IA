import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, urllib.parse, requests, os, threading, re
from datetime import datetime

# --- SISTEMA DE FILAS (LOCKS) ---
llm_lock = threading.Lock()
browser_lock = threading.RLock()

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.lock = threading.RLock()
        self.active_tasks = 0

    def get_driver(self):
        with self.lock:
            if self.driver is None:
                bot_profile = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/storage/bot_brave_profile")
                os.makedirs(bot_profile, exist_ok=True)
                options = uc.ChromeOptions()
                options.binary_location = "/usr/bin/brave-browser"
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument(f"--user-data-dir={bot_profile}")
                self.driver = uc.Chrome(options=options, headless=False, version_main=146)
            return self.driver

    def release(self):
        with self.lock:
            self.active_tasks -= 1
            if self.active_tasks <= 0 and self.driver:
                try: self.driver.quit()
                except: pass
                self.driver = None

bm = BrowserManager()

def sleep_stoppable(seconds, state_dict):
    """Pausa que pode ser interrompida imediatamente pelo botão STOP"""
    for _ in range(int(seconds * 10)):
        if state_dict.get("status") == "stopped": break
        time.sleep(0.1)

def is_within_30_days(date_text):
    date_text = date_text.lower().strip()
    if any(x in date_text for x in[":", "ontem", "yesterday", "seg", "ter", "qua", "qui", "sex", "sáb", "sab", "dom", "mon", "tue", "wed", "thu", "fri", "sat", "sun", "agora", "now", "min", "h"]):
        return True
    months = {"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12, "feb":2, "apr":4, "may":5, "aug":8, "sep":9, "oct":10, "dec":12}
    now = datetime.now()
    year_match = re.search(r'\b(20\d{2})\b', date_text)
    year_num = int(year_match.group(1)) if year_match else now.year
    month_num = next((v for k, v in months.items() if k in date_text), None)
    if not month_num: return True
    day_match = re.search(r'\b(\d{1,2})\b', date_text)
    if not day_match: return True
    try:
        msg_date = datetime(year_num, month_num, int(day_match.group(1)))
        if msg_date > now and not year_match:
            msg_date = datetime(now.year - 1, month_num, int(day_match.group(1)))
        return (now - msg_date).days <= 30
    except: return True

def ask_agent_if_match(title, company, loc, user_query, target_loc, enforce):
    # 1. Guilhotina Rápida
    title_l = title.lower()
    if "java" in user_query.lower():
        lixo =[".net", "c#", "golang", "data engineer", "data scientist", "elixir", "ruby", "php", "ios", "android", "frontend", "react", "uipath", "cloud engineer", "security", "qa", "tester", "support"]
        if any(l in title_l for l in lixo) and "java" not in title_l:
            return False, "Stack Errada"
        gestao =["manager", "director", "head", "scrum master", "product owner", "agile coach", "chief"]
        if any(g in title_l for g in gestao):
            return False, "Cargo Gestão"
        junior =["junior", "júnior", "trainee", "intern", "estágio", "estagiário", "graduate"]
        if any(j in title_l for j in junior):
            return False, "Junior/Trainee"

    # 2. IA Agent
    loc_rule = f"\nREJEIÇÃO FATAL: O usuário exige viver em '{target_loc}'. Local da vaga: '{loc}'. Se for incompatível, responda NAO." if enforce else ""
    prompt = f"""
    Tech Recruiter ULTRA RIGOROSO.
    CANDIDATO: Senior Software Engineer (Java). NÃO aceita cargos de gestão. Senior ou Mid-Senior apenas.
    BUSCA: "{user_query}"
    VAGA: "{title}" na "{company}"

    REGRAS DE REJEIÇÃO:
    1. Se é Management (Manager, Director), responda NAO.
    2. Se é outra stack (Cloud Engineer, Frontend, DevOps, C#), responda NAO.
    3. Se é nivel Junior, responda NAO.{loc_rule}

    MATCH PERFEITO? Responda APENAS com a palavra SIM ou NAO.
    """
    try:
        with llm_lock:
            r = requests.post("http://127.0.0.1:11434/api/generate", json={"model": "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M", "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}, timeout=300)
            res = r.json().get("response", "").strip().upper()
            return "SIM" in res, "Aprovado pela IA" if "SIM" in res else "Rejeitado pela IA (Sem Fit)"
    except Exception: return False, "Erro IA (Timeout)"

def draft_reply_with_ai(recruiter_name, recruiter_message):
    first_name = recruiter_name.split()[0] if recruiter_name else "Recrutador"
    prompt = f"""
    És o Gabriel Castro, Senior Java Software Engineer. Foco: Java, Spring Boot e Azure.
    O NOME DO RECRUTADOR É: {first_name}. TU ÉS O GABRIEL, NUNCA CHAMES O RECRUTADOR DE GABRIEL.

    20 REGRAS: Tom Seco e direto. Proibido usar "simpatia", "prazer". Saudação OBRIGATÓRIA: "Olá {first_name}, tudo bem?". Pede detalhes da vaga e modelo de trabalho. Máx 3 frases. Responde na língua do contacto. Se pedir AWS diz que tens Azure.
    
    MENSAGEM RECEBIDA DO RECRUTADOR:
    "{recruiter_message}"
    
    GERA APENAS A TUA RESPOSTA FINAL:
    """
    try:
        with llm_lock:
            r = requests.post("http://127.0.0.1:11434/api/generate", json={"model": "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M", "prompt": prompt, "stream": False, "options": {"temperature": 0.1}}, timeout=120)
            return r.json().get("response", "").strip()
    except Exception: return "Erro ao gerar resposta com a IA."

def start_linkedin_bot(job_title, location, max_hours, enforce_location, state_dict):
    with bm.lock: bm.active_tasks += 1
    consultancies =["Alten", "Accenture", "Deloitte", "Novabase", "Aubay", "PrimeIT", "Inetum", "Capgemini", "CGI", "NTT Data", "KPMG", "PwC", "Critical TechWorks", "Gfi", "Th3ra", "Condoroo", "Zoi", "Katalist", "Get2C"]
    stats = {"analyzed": 0, "approved": 0}
    yield {"log": f"🚀 Hunter Iniciado para: {job_title}..."}

    try:
        page = 0
        while state_dict.get("status") != "stopped":
            if state_dict.get("status") == "paused":
                yield {"log": "⏸️ Em Pausa."}
                while state_dict.get("status") == "paused": sleep_stoppable(1, state_dict)
                if state_dict.get("status") == "stopped": break
            
            cards_data =[]

            # BLOQUEIO DO BROWSER: Só o Hunter usa o rato
            with browser_lock:
                driver = bm.get_driver()
                offset = page * 25
                url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(job_title)}&location={urllib.parse.quote(location)}&f_TPR=r{max_hours*3600}&f_WT=2%2C3&start={offset}"
                
                driver.get(url)
                sleep_stoppable(4, state_dict)

                if len(driver.find_elements(By.ID, "username")) > 0:
                    yield {"log": "🔑 LOGIN NECESSÁRIO! Faça login e retome o Hunter."}
                    state_dict["status"] = "paused"
                    continue

                if "No matching jobs found" in driver.page_source:
                    yield {"log": "🏁 Fim das vagas."}
                    break

                yield {"log": f"📄 Pág {page+1}: Fazendo scroll..."}
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "job-card-container")))
                    last_count = 0
                    for _ in range(12): 
                        if state_dict.get("status") != "running": break
                        cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
                        if not cards: break
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cards[-1])
                        sleep_stoppable(1.5, state_dict)
                        if len(driver.find_elements(By.CLASS_NAME, "job-card-container")) == last_count: break 
                        last_count = len(driver.find_elements(By.CLASS_NAME, "job-card-container"))
                except: pass

                # Extrai e solta o browser para o Scanner!
                for card in driver.find_elements(By.CLASS_NAME, "job-card-container"):
                    try:
                        t = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title, .artdeco-entity-lockup__title, .job-card-list__title").text
                        c = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle, .artdeco-entity-lockup__subtitle, .job-card-container__primary-description").text
                        l = card.find_element(By.TAG_NAME, "a").get_attribute("href").split('?')[0]
                        try: j_loc = card.find_element(By.CSS_SELECTOR, "ul.job-card-container__metadata-wrapper li").text
                        except: j_loc = "Desconhecido"
                        cards_data.append((t, c, j_loc, l))
                    except: pass
            
            # O LLM PROCESSA EM SEGUNDO PLANO
            for t, c, j_loc, l in cards_data:
                if state_dict.get("status") != "running": break
                stats["analyzed"] += 1
                if any(cons.lower() in c.lower() for cons in consultancies): continue

                is_fit, reason = ask_agent_if_match(t, c, j_loc, job_title, location, enforce_location)
                if is_fit:
                    stats["approved"] += 1
                    yield {"log": f"✅ APROVADA: {c}", "job": {"title": t, "company": c, "link": l, "location": j_loc}, "stats": stats}
                else: yield {"log": f"🗑️ REJEITADA [{reason}]: {t}", "stats": stats}
            
            page += 1
            if page >= 40: break 
        yield {"log": "🛑 Hunter Encerrado."}
    except Exception as e: yield {"log": f"❌ Falha Geral: {str(e)[:100]}"}
    finally: bm.release()

def scan_linkedin_messages(state_dict):
    with bm.lock: bm.active_tasks += 1
    yield {"log": "🚀 Scanner de Mensagens Aguardando o navegador..."}
    messages_data =[]

    try:
        while state_dict.get("status") != "stopped":
            
            # BLOQUEIO DO BROWSER: O Scanner assume o rato!
            with browser_lock:
                if state_dict.get("status") == "stopped": break
                yield {"log": "🔍 Assumindo o controle do navegador..."}
                driver = bm.get_driver()
                
                # Se abriu o scanner 1º, a aba está vazia. Vai para o job search
                if "linkedin.com" not in driver.current_url:
                    driver.get("https://www.linkedin.com/jobs/search/")
                    sleep_stoppable(5, state_dict)

                if len(driver.find_elements(By.ID, "username")) > 0:
                    yield {"log": "🔑 LOGIN NECESSÁRIO! Pause o Scanner, logue e retome."}
                    state_dict["status"] = "paused"
                    while state_dict.get("status") == "paused": sleep_stoppable(1, state_dict)
                    if state_dict.get("status") == "stopped": break

                yield {"log": "📥 A extrair mensagens dos últimos 30 dias..."}
                
                # Abrir a Janela de Mensagens Inferior se minimizada
                try:
                    overlay = driver.find_element(By.CSS_SELECTOR, ".msg-overlay-list-bubble")
                    if "minimized" in overlay.get_attribute("class"):
                        header = overlay.find_element(By.CSS_SELECTOR, ".msg-overlay-bubble-header")
                        driver.execute_script("arguments[0].click();", header)
                        time.sleep(1.5)
                except: pass

                # Scroll no painel lateral de mensagens
                try:
                    scroll_area = driver.find_element(By.CSS_SELECTOR, ".msg-overlay-list-bubble__content")
                    last_count = 0
                    while state_dict.get("status") == "running":
                        convs = driver.find_elements(By.CSS_SELECTOR, ".msg-conversation-card")
                        if not convs: break
                        
                        try:
                            time_el = convs[-1].find_element(By.TAG_NAME, "time").text
                            if not is_within_30_days(time_el):
                                yield {"log": f"🛑 Limite de 30 dias atingido ({time_el})."}
                                break
                        except: pass
                        
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll_area)
                        sleep_stoppable(1.5, state_dict)
                        if len(driver.find_elements(By.CSS_SELECTOR, ".msg-conversation-card")) == last_count: break
                        last_count = len(driver.find_elements(By.CSS_SELECTOR, ".msg-conversation-card"))
                except: yield {"log": "⚠️ Erro ao descer lista de mensagens."}

                # Extrair conversas e fechar pop-ups
                convs = driver.find_elements(By.CSS_SELECTOR, ".msg-conversation-card")
                yield {"log": f"🔍 {len(convs)} conversas extraídas. A ler textos..."}
                
                for i in range(len(convs)):
                    if state_dict.get("status") != "running": break
                    try:
                        curr_convs = driver.find_elements(By.CSS_SELECTOR, ".msg-conversation-card")
                        if i >= len(curr_convs): break
                        
                        try:
                            t_text = curr_convs[i].find_element(By.TAG_NAME, "time").text
                            if not is_within_30_days(t_text): continue
                        except: pass

                        name = curr_convs[i].find_element(By.CSS_SELECTOR, ".msg-conversation-card__participant-names").text.strip()
                        
                        driver.execute_script("arguments[0].click();", curr_convs[i])
                        sleep_stoppable(1.5, state_dict)
                        
                        bubbles = driver.find_elements(By.CSS_SELECTOR, ".msg-s-event-listitem__message-bubble")
                        if bubbles:
                            last_msg = bubbles[-1].text.strip()
                            messages_data.append((name, last_msg))
                        
                        try:
                            close_btns = driver.find_elements(By.CSS_SELECTOR, ".msg-overlay-conversation-bubble .msg-overlay-bubble-header__control--close-btn")
                            for btn in close_btns: driver.execute_script("arguments[0].click();", btn)
                        except: pass
                    except: continue
            break # Scanner lê as msgs e sai do while

        # BROWSER LIBERADO. LLM TRABALHA AGORA.
        for name, last_msg in messages_data:
            if state_dict.get("status") != "running": break
            yield {"log": f"🧠 A gerar resposta para {name}..."}
            reply = draft_reply_with_ai(name, last_msg)
            yield {"type": "message_reply", "data": {"name": name, "message": last_msg, "reply": reply}}
            
        yield {"log": "✨ Scanner de mensagens concluído!"}
    except Exception as e: yield {"log": f"❌ Erro Scanner: {str(e)[:50]}"}
    finally: bm.release()
