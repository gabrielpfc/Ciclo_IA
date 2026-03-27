import streamlit as st
import time
import os
import re
import json
import threading
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
    
    # 3. GERAR RESPOSTA DO LLM (COM TTS SIMULTÂNEO)
    sys_inst = "ROLE: Neural OS. Responde em Português." if not is_voice_mode else "ROLE: English Tutor. Speak English."
    
    ai_msg = ""
    
    with ui_container:
        with st.chat_message("assistant"):
            llm_messages = messages[:-1] + [{"role": "user", "content": enriched_prompt}]
            stream = get_response_stream(llm_messages, sys_inst)
            
            # Criamos um placeholder vazio para atualizar o texto em tempo real
            message_placeholder = st.empty()
            last_processed_length = 0
            
            for chunk in stream:
                ai_msg += chunk
                # Atualiza a UI com o texto a ser gerado e um cursor visual
                message_placeholder.markdown(ai_msg + "▌")
                
                # Se estivermos em modo voz, processamos o TTS em pedaços (frases)
                if is_voice_mode:
                    unprocessed_text = ai_msg[last_processed_length:]
                    # Procura por frases completas terminadas em ponto, exclamação, interrogação ou quebra de linha
                    match = re.search(r'.*?[.!?\n]+', unprocessed_text)
                    if match:
                        sentence = match.group(0)
                        if sentence.strip():
                            # Dispara a geração e reprodução de áudio em uma Thread separada para não travar a UI
                            threading.Thread(target=generate_speech, args=(sentence.strip(), "en"), daemon=True).start()
                        last_processed_length += len(sentence)

            # Remove o cursor visual no final
            message_placeholder.markdown(ai_msg)
            
            # Processa qualquer resto de texto que não terminou em pontuação
            if is_voice_mode and last_processed_length < len(ai_msg):
                remaining_text = ai_msg[last_processed_length:].strip()
                if remaining_text:
                    threading.Thread(target=generate_speech, args=(remaining_text, "en"), daemon=True).start()

    # Guardar resposta da IA
    ai_data = {"role": "assistant", "content": ai_msg}
    messages.append(ai_data)

    # Atualizar estado e salvar
    st.session_state.chat_sessions[session_id]["messages"] = messages
    save_chat_session(session_id, st.session_state.chat_sessions[session_id]["title"], messages)
    
    return True