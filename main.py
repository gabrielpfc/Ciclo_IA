import streamlit as st
import uuid, os
from src.services.data_handler import load_all_chats, delete_chat_session
from src.services.utils import cleanup_audio_files

cleanup_audio_files()
st.set_page_config(layout="wide", page_title="Neural OS", page_icon="🧿", initial_sidebar_state="expanded")

if "current_page" not in st.session_state: st.session_state.current_page = "Chat"
if "chat_sessions" not in st.session_state:
    saved = load_all_chats()
    st.session_state.chat_sessions = saved if saved else {"default": {"title": "Sessão Inicial", "messages": []}}
if "current_session" not in st.session_state: st.session_state.current_session = "default"

with st.sidebar:
    st.markdown("### 🧿 Neural OS")
    
    # Monitor de Sistema Moderno (Estilo Kanban/Tailwind)
    st.components.v1.html("""
    <div style="font-family: 'Inter', sans-serif; padding: 16px; background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; color: #94a3b8; box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1e293b; padding-bottom: 8px;">
            <b style="color: #6366f1; font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase;">📡 Live Monitor</b> 
            <span id="clock" style="color: #64748b; font-size: 12px; font-variant-numeric: tabular-nums;">--:--:--</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
            <div style="background: #1e293b; padding: 8px; border-radius: 8px;">
                <div style="font-size: 10px; color: #64748b; text-transform: uppercase; margin-bottom: 2px;">VRAM</div>
                <div style="color: #f8fafc; font-weight: 600;"><span id="vram">0.0</span><span style="font-size: 10px; color: #64748b; font-weight: normal;"> / 24GB</span></div>
            </div>
            <div style="background: #1e293b; padding: 8px; border-radius: 8px;">
                <div style="font-size: 10px; color: #64748b; text-transform: uppercase; margin-bottom: 2px;">GPU</div>
                <div style="color: #10b981; font-weight: 600;"><span id="gpu">0</span>%</div>
            </div>
            <div style="background: #1e293b; padding: 8px; border-radius: 8px; grid-column: span 2;">
                <div style="font-size: 10px; color: #64748b; text-transform: uppercase; margin-bottom: 2px;">RAM</div>
                <div style="color: #f8fafc; font-weight: 600;"><span id="ram">0.0</span><span style="font-size: 10px; color: #64748b; font-weight: normal;"> / 32GB</span></div>
            </div>
        </div>
    </div>
    <script>
        async function update() {
            try {
                const res = await fetch('http://127.0.0.1:8000/stats');
                const data = await res.json();
                document.getElementById('vram').innerText = data.vram.toFixed(1);
                document.getElementById('gpu').innerText = data.gpu;
                document.getElementById('ram').innerText = data.ram.toFixed(1);
                document.getElementById('clock').innerText = new Date().toLocaleTimeString();
            } catch(e) {}
        }
        setInterval(update, 1000);
        update();
    </script>
    """, height=160)

    st.divider()
    
    # Navegação
    if st.button("💬 Chat Inteligente", use_container_width=True, type="primary" if st.session_state.current_page == "Chat" else "secondary"): 
        st.session_state.current_page = "Chat"; st.rerun()
    if st.button("📋 Kanban Board", use_container_width=True, type="primary" if st.session_state.current_page == "Kanban" else "secondary"): 
        st.session_state.current_page = "Kanban"; st.rerun()
    
    st.divider()
    
    # Histórico de Conversas
    if st.session_state.current_page == "Chat":
        with st.expander("🗂️ Conversas", expanded=True):
            if st.button("➕ Nova Conversa", use_container_width=True):
                sid = str(uuid.uuid4()); st.session_state.chat_sessions[sid] = {"title": "Nova Conversa", "messages": []}
                st.session_state.current_session = sid; st.rerun()
            for sid, data in reversed(list(st.session_state.chat_sessions.items())):
                if st.button(data.get("title", "Sessão"), key=sid, use_container_width=True, type="primary" if sid == st.session_state.current_session else "secondary"):
                    st.session_state.current_session = sid; st.rerun()

if st.session_state.current_page == "Chat":
    from src.ui.chat import render_chat; render_chat()
elif st.session_state.current_page == "Kanban":
    from src.ui.kanban import render_kanban; render_kanban()