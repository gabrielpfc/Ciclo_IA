import streamlit as st
import uuid
from src.services.data_handler import load_todos

# 1. Configuração da Página
st.set_page_config(
    layout="wide", 
    page_title="Ciclo IA - Workspace",
    page_icon="🧿",
    initial_sidebar_state="expanded"
)

# 2. Estado da Sessão
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Sessão Principal": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Sessão Principal"
if "todos" not in st.session_state:
    st.session_state.todos = load_todos()

# 3. Barra Lateral (Azure Style)
with st.sidebar:
    st.markdown("### 🧿 Workspace IA")
    st.caption("v1.0.0-beta | Cluster: Local (7900 XTX)")
    st.divider()
    
    # Navegação
    page = st.radio(
        "MÓDULOS",
        options=[
            "💬 Chat & Copilot", 
            "📋 Kanban & Sprints", 
            "📚 Knowledge Base (RAG)", 
            "⚙️ Model Configs",
            "📅 Calendário"
        ]
    )
    
    st.divider()
    
    st.markdown("#### 🗂️ Histórico de Chats")
    if st.button("➕ Nova Conversa", use_container_width=True):
        new_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_id] = []
        st.session_state.current_session = new_id
        st.rerun()
        
    for session_id in reversed(list(st.session_state.chat_sessions.keys())):
        active = (session_id == st.session_state.current_session)
        if st.button(session_id, key=f"btn_{session_id}", use_container_width=True, type="primary" if active else "secondary"):
            st.session_state.current_session = session_id
            st.rerun()

# 4. Roteamento
if page == "💬 Chat & Copilot":
    from src.ui.chat import render_chat
    render_chat()
else:
    st.title(page)
    st.info("Módulo em fase de integração de agentes.")
