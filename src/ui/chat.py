import streamlit as st
import json
from src.services.llm_engine import get_response
from src.services.data_handler import log_interaction_for_training

def render_chat():
    st.title("💻 Terminal Neural")
    st.caption(f"Sessão: {st.session_state.current_session} | Aceleração: RX 7900 XTX")

    current_chat = st.session_state.chat_sessions[st.session_state.current_session]

    # --- ZONA DE ARQUIVOS ---
    with st.sidebar:
        st.divider()
        st.markdown("### 📎 Contexto Externo")
        uploaded_files = st.file_uploader("Upload de PDF/Imagens (OCR)", accept_multiple_files=True)
        if uploaded_files:
            st.success(f"{len(uploaded_files)} arquivos anexados.")

    # --- SYSTEM PROMPT ---
    active_todos = [t['task'] for t in st.session_state.todos if not t['done']]
    system_instruction = f"""
Você é o Qwen, o Arquiteto Chefe deste sistema Linux (Fedora).
Hardware: AMD Radeon RX 7900 XTX (24GB VRAM) | Ryzen 9 5950X.

CONSCIÊNCIA DE UI:
- Você roda em uma interface Streamlit (Python).
- O botão 'Deploy' no canto superior é nativo da nuvem Streamlit, não do nosso core.
- O histórico de conversas está na barra lateral esquerda.

REGRAS:
1. Responda em Markdown. Use blocos de código (```) para comandos e scripts.
2. Tarefas Ativas no Sistema: {json.dumps(active_todos)}
3. Seja extremamente polido, rápido e técnico.
"""

    # Exibir Histórico
    for msg in current_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input (Shift+Enter quebra linha, Enter envia)
    if prompt := st.chat_input("Insira comando ou código..."):
        
        current_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Processando tensores..."):
            ai_msg = get_response(current_chat, system_instruction) 
            
        current_chat.append({"role": "assistant", "content": ai_msg})
        with st.chat_message("assistant"):
            st.markdown(ai_msg)
            
        st.session_state.chat_sessions[st.session_state.current_session] = current_chat
        log_interaction_for_training(prompt, ai_msg, str(active_todos))
