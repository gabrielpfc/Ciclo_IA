import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib.parse
import requests
import os

def ask_agent_if_match(found_title, found_company, user_search_query):
    """
    Usa o cérebro do Apriel 15b para validar a vaga baseando-se estritamente
    no que o usuário digitou na barra de pesquisa (Senior, Junior, Java, Python, etc).
    """
    prompt = f"""
    Você é um Tech Recruiter de Elite.
    Sua única tarefa é verificar se a VAGA ENCONTRADA condiz com a PESQUISA DO USUÁRIO.

    PESQUISA DO USUÁRIO: "{user_search_query}"
    VAGA ENCONTRADA: "{found_title}" na empresa "{found_company}"

    REGRAS DE AVALIAÇÃO:
    1. A vaga DEVE corresponder à tecnologia principal e ao nível de experiência (se especificado) na PESQUISA DO USUÁRIO.
    2. Se o usuário pesquisou apenas a linguagem (ex: "Java"), aceite qualquer nível (Junior, Pleno, Senior), desde que seja para essa linguagem.
    3. Se a vaga foca claramente em OUTRA stack diferente da pesquisada (ex: usuário buscou "Java" mas a vaga é "C#" ou "Data Engineer"), rejeite.
    4. Se o usuário especificar um nível na busca (ex: "Junior", "Senior", "Manager"), a vaga DEVE condizer com esse nível.

    Esta vaga é um MATCH adequado para a pesquisa "{user_search_query}"?
    Responda APENAS com a palavra SIM ou NAO. Nada mais.
    """
    try:
        r = requests.post("http://127.0.0.1:11434/api/generate", 
                         json={
                             "model": "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M", 
                             "prompt": prompt, 
                             "stream": False,
                             "options": {"temperature": 0.0}
                         }, timeout=300)
        resposta = r.json().get("response", "").strip().upper()
        return "SIM" in resposta
    except Exception as e:
        return False

def start_linkedin_bot(job_title, location, max_hours, state_dict):
    bot_profile = os.path.expanduser("~/Documentos/Repos/Ciclo_IA/storage/bot_brave_profile")
    os.makedirs(bot_profile, exist_ok=True)

    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/brave-browser"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={bot_profile}")
    
    # --- BLACKLIST COMPLETA DE CONSULTORIA E OUTSOURCING ---
    consultancies = [
        # Originais
        "Alten", "Accenture", "Deloitte", "Novabase", "Aubay", "PrimeIT", "Inetum", "GFI", 
        "Capgemini", "Altran", "CGI", "NTT Data", "Everis", "KPMG", "PwC", "Critical TechWorks", 
        "Gfi", "Th3ra", "Condoroo", "Zoi", "Katalist", "Get2C",
        # Gigantes Globais
        "Fujitsu", "Claranet", "TCS", "Tata Consultancy", "Infosys", "Wipro", "Cognizant",
        # Clássicas de Outsourcing
        "BOLD", "Devoteam", "Noesis", "Altia", "agap2IT", "KCS IT", "KWAN", "Celfocus",
        # Mercado Português e Especializadas
        "InnoTech", "Xpand IT", "Bee Engineering", "Integer Consulting", "Olisipo", "Syone", 
        "ITSector", "Timestamp", "Glintt", "Readiness IT", "Dellent Consulting", 
        "Crossjoin Solutions", "Rumos Professionals", "Keepler", "Talent", "Mindsource",
        "Emetra", "Aubay Portugal", "Matches", "Findmore"
    ]

    driver = None
    stats = {"analyzed": 0, "approved": 0}
    yield {"log": f"🚀 Iniciando Agente Adaptativo (Anti-Consultoria total)..."}

    try:
        driver = uc.Chrome(options=options, headless=False, version_main=146)
        page = 0
        
        while state_dict.get("status") != "stopped":
            if state_dict.get("status") == "paused":
                yield {"log": "⏸️ Bot em Pausa."}
                while state_dict.get("status") == "paused":
                    time.sleep(1)
                yield {"log": "▶️ Retomando..."}
            
            offset = page * 25
            url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(job_title)}&location={urllib.parse.quote(location)}&f_TPR=r{max_hours*3600}&f_WT=2%2C3&start={offset}"
            
            driver.get(url)
            time.sleep(4)

            # Check de Login
            if "checkpoint/lg/login" in driver.current_url or driver.find_elements(By.ID, "username"):
                yield {"log": "🔑 LOGIN NECESSÁRIO! Por favor, logue na janela do Brave aberta."}
                while "jobs/search" not in driver.current_url:
                    time.sleep(2)
                    if state_dict.get("status") == "stopped": break
                yield {"log": "✅ Login detectado!"}

            if "No matching jobs found" in driver.page_source:
                yield {"log": "🏁 LinkedIn não retornou mais resultados."}
                break

            # SCROLL HARDCORE NA SIDEBAR
            yield {"log": f"📄 Lendo Página {page+1}..."}
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "job-card-container")))
                last_count = 0
                for _ in range(12): 
                    if state_dict.get("status") != "running": break
                    cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
                    if len(cards) == 0: break
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cards[-1])
                    time.sleep(1.5) 
                    new_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
                    if len(new_cards) == last_count: break 
                    last_count = len(new_cards)
            except: pass

            # Processamento dos Cards
            cards_completos = driver.find_elements(By.CLASS_NAME, "job-card-container")
            for card in cards_completos:
                if state_dict.get("status") != "running": break
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title, .artdeco-entity-lockup__title, .job-card-list__title").text
                    company = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle, .artdeco-entity-lockup__subtitle, .job-card-container__primary-description").text
                    link = card.find_element(By.TAG_NAME, "a").get_attribute("href").split('?')[0]
                    
                    stats["analyzed"] += 1
                    
                    # 1. Guilhotina de Consultoras (Filtro Blacklist)
                    if any(c.lower() in company.lower() for c in consultancies):
                        # yield {"log": f"⏩ Blacklisted: {company}", "stats": stats}
                        continue

                    # 2. Decisão da IA baseada na tua barra de pesquisa
                    if ask_agent_if_match(title, company, job_title):
                        stats["approved"] += 1
                        yield {
                            "log": f"✅ APROVADA: {company} | {title}", 
                            "job": {"title": title, "company": company, "link": link},
                            "stats": stats
                        }
                    else:
                        yield {"log": f"🗑️ REJEITADA (Sem Fit): {title}", "stats": stats}
                        
                except: continue
            
            page += 1
            if page >= 40: break 
            
        yield {"log": "🛑 Robô Encerrado."}
    except Exception as e:
        yield {"log": f"❌ Falha: {str(e)}"}
    finally:
        if state_dict.get("status") == "stopped" and driver:
            driver.quit()
