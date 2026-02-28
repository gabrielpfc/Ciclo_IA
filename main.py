import streamlit as st
import uuid
from src.services.data_handler import load_todos, load_all_chats

st.set_page_config(layout="wide", page_title="Neural Center", page_icon="🧿")

if "chat_sessions" not in st.session_state:
    saved = load_all_chats()
    st.session_state.chat_sessions = saved if saved else {"default": {"title": "Sessão Inicial", "messages": []}}

if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

if "todos" not in st.session_state:
    st.session_state.todos = load_todos()

with st.sidebar:
    st.title("🧿 Workspace")
    page = st.radio("MENU", options=["💬 Chat", "📋 Kanban", "📚 RAG", "⚙️ Config"])
    st.divider()
    if st.button("➕ Nova Conversa", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chat_sessions[new_id] = {"title": "Conversa Vazia", "messages": []}
        st.session_state.current_session = new_id
        st.rerun()
    st.subheader("Histórico")
    for sid, data in reversed(list(st.session_state.chat_sessions.items())):
        is_active = (sid == st.session_state.current_session)
        if st.button(data.get("title", "Sem título"), key=f"btn_{sid}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.current_session = sid
            st.rerun()

if page == "💬 Chat":
    from src.ui.chat import render_chat
    render_chat()
else:
    st.title(page)
    st.info("Módulo em desenvolvimento.")
