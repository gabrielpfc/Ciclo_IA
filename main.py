import streamlit as st
import uuid

from src.services.utils import cleanup_audio_files
# Limpa áudios velhos ao iniciar
cleanup_audio_files()
from src.services.data_handler import load_todos, load_all_chats
from src.services.telemetry import get_system_snapshot

st.set_page_config(layout="wide", page_title="Neural Center", page_icon="🧿")

# Inicialização
if "chat_sessions" not in st.session_state:
    saved = load_all_chats()
    st.session_state.chat_sessions = saved if saved else {"default": {"title": "Sessão Inicial", "messages":[]}}
if "current_session" not in st.session_state: st.session_state.current_session = "default"
if "todos" not in st.session_state: st.session_state.todos = load_todos()
if "last_error" not in st.session_state: st.session_state.last_error = ""

# --- HEALTH MONITOR (SNAPSHOT) ---
vram_gb, ram_gb, gpu_pct = get_system_snapshot()

# Estimativa de tokens do chat atual (Aprox. 4 chars por token)
current_msgs = st.session_state.chat_sessions[st.session_state.current_session]["messages"]
text_length = sum([len(m["content"]) for m in current_msgs if isinstance(m["content"], str)])
ctx_k = round((text_length / 4) / 1000, 1)
kv_vram_est = round(ctx_k * 0.1, 2) # ~100MB por cada 1k tokens em q8_0 15B

with st.sidebar:
    st.markdown("### 🧿 Workspace")
    
    # Dashboard de Métricas
    st.markdown(f"""
    <div style="font-size: 0.8em; padding: 10px; background-color: #1E1E1E; border-radius: 5px; margin-bottom: 15px;">
        <b>📡 HEALTH MONITOR</b><br>[ VRAM: {vram_gb}/24GB ]<br>
        [ RAM: {ram_gb}/32GB ]<br>[ GPU: {gpu_pct}% ]<br>[ Contexto: {ctx_k}k / 100k ]<br>
        <i>* Peso do KV Cache: ~{kv_vram_est} GB</i>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegação Principal
    page = st.radio("MÓDULOS", ["💬 Chat", "⚙️ Configurações"], label_visibility="collapsed")
    st.divider()

    # Expanders (Retrair/Expandir)
    with st.expander("🗂️ Conversas", expanded=True):
        if st.button("➕ Nova Conversa", use_container_width=True):
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {"title": "Conversa Vazia", "messages":[]}
            st.session_state.current_session = new_id
            st.rerun()
        
        for sid, data in reversed(list(st.session_state.chat_sessions.items())):
            is_active = (sid == st.session_state.current_session)
            if st.button(data.get("title", "Sem título"), key=f"btn_{sid}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.current_session = sid
                st.rerun()

    with st.expander("📋 Kanban (Sprints)", expanded=False):
        st.button("📌 Sprint 1: Jogo Godot", use_container_width=True)
        st.button("📌 Sprint 2: Web Agent", use_container_width=True)

    with st.expander("📎 Anexos (RAG/Vision)", expanded=False):
        st.file_uploader("Arraste os ficheiros aqui", accept_multiple_files=True, key="sidebar_uploader")
        if st.button("Ver Todos (Grade)", use_container_width=True):
            st.toast("Galeria visual será implementada no módulo Config.", icon="🖼️")

# Roteamento
if page == "💬 Chat":
    from src.ui.chat import render_chat
    render_chat()
else:
    st.title("⚙️ Configurações")
    st.info("Configurações do sistema e Galeria de Arquivos entrarão aqui.")
