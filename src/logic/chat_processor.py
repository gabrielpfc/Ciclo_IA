import streamlit as st
import time
import os
import re
import json
from src.services.llm_engine import get_response_stream
from src.services.voice_engine import generate_speech
from src.services.stt_engine import transcribe_audio
from src.services.data_handler import save_chat_session

KANBAN_DATA_PATH = "/home/user/Documentos/Repos/Ciclo_IA/storage/kanban_state.json"

def resolve_mentions(text):
    """Substitui menções #[TASK:id] ou #[SPRINT:id] por contexto real para o LLM."""
    if not os.path.exists(KANBAN_DATA_PATH): return text
    try:
        with open(KANBAN_DATA_PATH, "r") as f: data = json.load(f)
        
        # Encontra padrões #[TIPO:ID]
        mentions = re.findall(r'#\[(TASK|SPRINT):(.*?)\]', text)
        enriched_text = text
        
        for m_type, m_id in mentions:
            if m_type == "TASK":
                task = next((t for t in data.get('tasks', []) if t['id'] == m_id), None)
                if task:
                    detail = f"\n[CONTEXTO TAREFA: {task['title']} | Status: {task.get('status')} | Desc: {task.get('description','')}]\n"
                    enriched_text = enriched_text.replace(f"#[TASK:{m_id}]", detail)
            elif m_type == "SPRINT":
                sprint = next((s for s in data.get('sprints', []) if s['id'] == m_id), None)
                if sprint:
                    detail = f"\n[CONTEXTO SPRINT: {sprint['name']}]\n"
                    enriched_text = enriched_text.replace(f"#[SPRINT:{m_id}]", detail)
        return enriched_text
    except: return text

def handle_input(session_id, messages, text_input=None, audio_input=None, ui_container=None):
    user_text = text_input
    user_audio_path = None
    is_voice_mode = False

    # 1. PROCESSAR ÁUDIO (STT)
    if audio_input:
        audio_bytes = audio_input.getvalue()
        try:
            user_audio_path = f"temp_rec_{int(time.time())}.wav"
            with open(user_audio_path, "wb") as f: f.write(audio_bytes)
            with st.spinner("🎧 A transcrever..."):
                user_text, lang = transcribe_audio(user_audio_path)
                is_voice_mode = True
        except Exception as e:
            st.error(f"Erro no STT: {e}")
            return False

    if not user_text or user_text.strip() == "": return False

    # 2. ENRIQUECER COM KANBAN (#)
    enriched_prompt = resolve_mentions(user_text)

    # Adicionar mensagem do utilizador à sessão
    msg_data = {"role": "user", "content": user_text}
    if user_audio_path: msg_data["audio_path"] = user_audio_path
    messages.append(msg_data)
    
    # 3. GERAR RESPOSTA DO LLM
    sys_inst = "ROLE: Neural OS. Responde em Português." if not is_voice_mode else "ROLE: English Tutor. Speak English."
    
    with ui_container:
        with st.chat_message("assistant"):
            # Enviamos o prompt ENRIQUECIDO, mas guardamos o original no histórico visual
            llm_messages = messages[:-1] + [{"role": "user", "content": enriched_prompt}]
            stream = get_response_stream(llm_messages, sys_inst)
            ai_msg = st.write_stream(stream)

    # 4. GERAR VOZ (TTS)
    ai_audio_path = None
    if is_voice_mode:
        with st.spinner("🗣️ A gerar voz..."):
            ai_audio_path = generate_speech(ai_msg, lang="en")

    # Guardar resposta da IA
    ai_data = {"role": "assistant", "content": ai_msg}
    if ai_audio_path: ai_data["audio_path"] = ai_audio_path
    messages.append(ai_data)

    st.session_state.chat_sessions[session_id]["messages"] = messages
    save_chat_session(session_id, st.session_state.chat_sessions[session_id]["title"], messages)
    return True
