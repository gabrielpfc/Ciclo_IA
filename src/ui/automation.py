import streamlit as st
from src.logic.bot_logic import start_linkedin_bot

def render_automation():
    st.title("🤖 LinkedIn Job Hunter (Anti-Consultora)")
    st.info("O bot usa o teu Brave para pesquisar vagas ativamente e ignora empresas de outsourcing.")
    
    # O teu prompt detalhado injetado por defeito
    default_prompt = """🤖 USER PROFILE DATA (FOR JOB MATCHING)
[1. BASIC INFO & TARGET ROLES]
Current Title: Senior Software Engineer / Senior Java Developer
Total Experience: 6+ years (since 2018)
Target Job Titles: Senior Java Developer, Senior Software Engineer, Backend Engineer, Java Spring Boot Developer, Full Stack Developer (Java-heavy).
Seniority Level: Senior, Mid-Senior. (Do NOT apply for Junior or Trainee roles).
Management Level: Individual Contributor (Technical leadership/architecture is okay, but NO people management/HR leadership roles).

[2. LOCATION & WORK MODEL]
Base Location: Loures, Lisbon, Portugal.
Work Authorization: Authorized to work in Portugal.
Preferred Work Model: Remote (Portugal), Hybrid (Lisbon or Porto).
Acceptable On-site: Up to 3 days a week in Lisbon/Greater Lisbon area.[3. TECH STACK & CORE SKILLS]
Primary Backend (Must Haves): Java (8, 11, 17, 21+), Spring Boot, Spring Cloud, REST APIs, Microservices Architecture.
Databases: SQL Server, PostgreSQL, Oracle, MongoDB (NoSQL), JPA, Hibernate (Solving N+1, FetchType optimization).
Cloud & DevOps: Azure, Azure DevOps, CI/CD Pipelines, Docker, Git.
Testing & Quality: JUnit, Mockito, TDD, Clean Architecture, Hexagonal Architecture (Ports and Adapters), SOLID principles applied practically.
Secondary/Past Stack (Nice to Haves): C# .NET, Angular (Basic/Mid level for Full Stack roles), JavaScript, VB6 (Legacy migration experience).

[4. LANGUAGES]
Portuguese: Native.
English: Fluent (B2/C1) - Fully capable of working in international teams.[5. EXCLUSION CRITERIA (RED FLAGS - DO NOT APPLY)]
Geographic: Roles requiring permanent relocation outside of Portugal, or heavy international rotation.
Tech Stack: Roles strictly focused on legacy maintenance (e.g., 100% VB6). Roles where Java is NOT the main backend language.
Role Type: Scrum Master, Product Owner, Tech Lead (if strictly people management).

[6. MATCHING LOGIC (For the Bot)]
High Match (Score 90-100%): Mentions "Java", "Spring Boot", "Microservices", "Senior", and is Hybrid in Lisbon or Remote in PT.
Medium Match (Score 70-89%): Mentions "Full Stack", "Java", "Angular/React", "CI/CD".
Low/No Match (Score < 50%): Requires frontend heavy, relocation, or people management.
"""

    st.text_area("Contexto de Pesquisa e Filtro da IA", value=default_prompt, height=400)
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.caption("Aviso: O Brave Browser deve estar fechado para evitar conflito de Perfil.")
    with col2:
        if st.button("🚀 Iniciar Scanner", type="primary", use_container_width=True):
            with st.spinner("A varrer o LinkedIn em Portugal..."):
                # O bot pesquisa a keyword principal no LinkedIn
                vagas = start_linkedin_bot("Senior Java")
                
                if vagas:
                    st.success(f"Encontrei {len(vagas)} vagas potenciais (sem consultoras)!")
                    for v in vagas:
                        with st.container():
                            st.markdown(f"#### 💼 {v['title']}")
                            st.write(f"🏢 **Empresa:** {v['company']}")
                            st.link_button("Abrir Vaga", v['link'])
                            st.divider()
                else:
                    st.warning("Nada encontrado ou todas as vagas listadas eram consultoras (Accenture, Alten, etc).")
