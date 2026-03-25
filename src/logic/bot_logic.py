import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
from src.config import BRAVE_PATH, BRAVE_USER_DATA

def start_linkedin_bot(job_title):
    options = uc.ChromeOptions()
    options.binary_location = BRAVE_PATH
    options.add_argument(f"--user-data-dir={BRAVE_USER_DATA}")
    options.add_argument("--profile-directory=Default")
    
    # Lista de consultoras conhecidas para ignorar (Expande esta lista se quiseres)
    consultancies = [
        "Alten", "Accenture", "Deloitte", "Novabase", "Aubay", "Keepler", 
        "It's Sector", "Talent", "Recruitment", "Consultancy", "Outsourcing", 
        "Kpmg", "PwC", "Critical TechWorks", "PrimeIT", "Gfi", "Inetum"
    ]

    driver = uc.Chrome(options=options, headless=False)
    results = []

    try:
        # Pesquisa direta de vagas em Portugal
        url = f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}&location=Portugal&f_TPR=r604800"
        driver.get(url)
        time.sleep(5)

        # Scrapar os cards de vagas
        cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
        
        for card in cards:
            try:
                title = card.find_element(By.CLASS_NAME, "artdeco-entity-lockup__title").text
                company = card.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle").text
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")

                # FILTRO ANTI-CONSULTORA
                is_consultant = any(c.lower() in company.lower() for c in consultancies)
                
                if not is_consultant:
                    results.append({"title": title, "company": company, "link": link})
            except:
                continue
        
        return results
    except Exception as e:
        print(f"Erro no Bot: {e}")
        return []
    # Nota: Não fechamos o driver aqui para poderes ver o que ele encontrou
