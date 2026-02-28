import streamlit as st
import json
import base64
import fitz
from src.services.llm_engine import get_response, generate_title
from src.services.data_handler import log_interaction_for_training, save_chat_session
from src.services.memory_manager import load_memory, save_fact

def process_uploaded_files(uploaded_files):
    images_b64 = []
    text_context = ""
    for file in uploaded_files:
        if file.type.startswith('image'):
            bytes_data = file.getvalue()
            b64 = base64.b64encode(bytes_data).decode('utf-8')
            images_b64.append(b64)
        elif file.type == "application/pdf":
            doc = fitz.open(stream=file.read(), filetype="pdf")
            for page in doc: text_context += page.get_text()
        else:
            text_context += file.getvalue().decode("utf-8")
    return images_b64, text_context

def render_chat():
    session_id = st.session_state.current_session
    session_data = st.session_state.chat_sessions[session_id]
    messages = session_data["messages"]

    # --- BARRA LATERAL EXTRA ---
    with st.sidebar:
        st.divider()
        st.markdown("### 🧠 Memória de Longo Prazo")
        memory_data = load_memory()
        
        # Visualizador de Memória
        if memory_data:
            st.json(memory_data, expanded=False)
        else:
            st.info("Ainda não sei nada sobre você.")
            
        # Injetor Manual de Fatos
        with st.popover("➕ Adicionar Fato"):
            new_key = st.text_input("Chave (ex: projeto)")
            new_val = st.text_input("Valor (ex: RPG Godot)")
            if st.button("Salvar Memória"):
                save_fact(new_key, new_val)
                st.success("Salvo!")
                st.rerun()

        st.divider()
        with st.expander("📎 Anexos (RAG/Vision)"):
            uploaded_files = st.file_uploader("Arquivos", accept_multiple_files=True)

    # --- CHAT PRINCIPAL ---
    col1, col2 = st.columns([0.8, 0.2])
    col1.title(f"💬 {session_data.get('title', 'Chat')}")
    if col2.button("Limpar"):
        st.session_state.chat_sessions[session_id]["messages"] = []
        st.rerun()

    # System Prompt Dinâmico
    system_instruction = """
Você é o Apriel-15B.
HARDWARE: AMD 7900 XTX (24GB).
OBJETIVO: Ser o melhor assistente de engenharia e criatividade.
ESTILO: Respostas completas e detalhadas. Se for pedido um texto longo (livro/artigo), escreva extensivamente.
"""

    for msg in messages:
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], list):
                st.markdown(msg["content"][0]["text"])
                st.caption("📷 [Imagem Analisada]")
            else:
                st.markdown(msg["content"])

    if prompt := st.chat_input("Comando..."):
        images_b64 = []
        doc_text = ""
        
        if uploaded_files:
            images_b64, doc_text = process_uploaded_files(uploaded_files)
            if doc_text: prompt += f"\n\n[CONTEXTO ARQUIVOS]:\n{doc_text}"

        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            if images_b64: st.image(uploaded_files[0], width=200)

        with st.spinner("Gerando (Max Tokens)..."):
            ai_msg, elapsed, log = get_response(messages, system_instruction, images_base64=images_b64)
            
        messages.append({"role": "assistant", "content": ai_msg})
        with st.chat_message("assistant"):
            st.markdown(ai_msg)
            if elapsed: st.caption(f"⏱️ {elapsed}s")

        # Gerar Título na primeira msg
        if len(messages) <= 2:
            new_title = generate_title(messages)
            if new_title: st.session_state.chat_sessions[session_id]["title"] = new_title

        save_chat_session(session_id, session_data.get("title", "Chat"), messages)
        log_interaction_for_training(prompt, ai_msg, "Multimodal")
        st.rerun()
