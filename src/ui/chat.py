import streamlit as st
import os
from src.ui.styles import inject_chat_css
from src.logic.chat_processor import handle_input

def render_chat():
    inject_chat_css()
    
    session_id = st.session_state.current_session
    session_data = st.session_state.chat_sessions[session_id]
    messages = session_data["messages"]

    # --- CABEÇALHO ---
    c1, c2 = st.columns([0.9, 0.1])
    c1.subheader(f"🇬🇧 {session_data.get('title', 'English Tutor')}")
    if c2.button("🗑️", help="Limpar"):
        st.session_state.chat_sessions[session_id]["messages"] = []
        st.rerun()

    # --- HISTÓRICO ---
    chat_container = st.container(height=650)
    with chat_container:
        if not messages:
            st.info("🎙️ Press the microphone below to start speaking.")
            
        for msg in messages:
            with st.chat_message(msg["role"]):
                # Áudio primeiro
                if "audio_path" in msg and msg["audio_path"] and os.path.exists(msg["audio_path"]):
                    st.audio(msg["audio_path"], format="audio/wav")
                # Texto depois
                st.markdown(msg["content"])

    # --- BARRA DE COMANDO ---
    st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
    c_txt, c_mic, c_clip, c_send = st.columns([0.7, 0.1, 0.1, 0.1])

    with c_txt:
        # Hack para detetar Enter: usamos key dinâmico ou form
        text_val = st.text_input("Msg", placeholder="Type here...", label_visibility="collapsed", key="txt_input")
    
    with c_mic:
        audio_val = st.audio_input("Mic", label_visibility="collapsed")
        
    with c_clip:
        if st.button("📎"): st.toast("Arraste ficheiros para a barra lateral", icon="ℹ️")
        
    with c_send:
        send_clicked = st.button("➤", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- GATILHO DE LÓGICA ---
    # Se houver áudio ou texto+botão, chama o processador
    if audio_val or (send_clicked and text_val):
        success = handle_input(session_id, messages, text_input=text_val, audio_input=audio_val)
        if success:
            st.rerun()
