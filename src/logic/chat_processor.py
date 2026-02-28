import streamlit as st
import time
import os
from src.services.llm_engine import get_response, generate_title
from src.services.data_handler import log_interaction_for_training, save_chat_session
from src.services.voice_engine import generate_speech
from src.services.stt_engine import transcribe_audio

def handle_input(session_id, messages, text_input=None, audio_input=None):
    user_text = text_input
    user_audio_path = None

    # 1. PROCESSAMENTO DE ÁUDIO
    if audio_input:
        audio_bytes = audio_input.getvalue()
        audio_hash = hash(audio_bytes)
        
        if st.session_state.get("last_processed_audio_hash") == audio_hash:
            return False
        st.session_state.last_processed_audio_hash = audio_hash
        
        try:
            user_audio_path = f"temp_rec_{int(time.time())}.wav"
            with open(user_audio_path, "wb") as f:
                f.write(audio_bytes)
            
            with st.spinner("🎧 A ouvir (Inglês Forçado)..."):
                user_text, lang = transcribe_audio(user_audio_path)
                
            if not user_text:
                st.toast("Não entendi. Tente falar mais perto.", icon="⚠️")
                return False
        except Exception as e:
            st.toast(f"Erro Áudio: {str(e)}", icon="🚨")
            return False

    if not user_text or user_text.strip() == "": return False

    # 2. FLUXO
    try:
        msg_data = {"role": "user", "content": user_text}
        if user_audio_path: msg_data["audio_path"] = user_audio_path
        messages.append(msg_data)
        
        # Prompt de Professor Rigoroso
        system_instruction = """
        ROLE: English Tutor (Apriel).
        GOAL: Help the user improve their English.
        HARDWARE: AMD 7900 XTX.
        RULES:
        1. Speak ONLY in English.
        2. Keep it conversational (short sentences).
        3. If there is a grammar error, correct it explicitly before answering.
        """

        with st.spinner("🧠 A pensar..."):
            ai_msg, elapsed, log = get_response(messages, system_instruction, predict_tokens=200)

        # TTS (Gera o arquivo E toca automaticamente nas colunas)
        ai_audio_path = None
        with st.spinner("🗣️ A falar..."):
            ai_audio_path = generate_speech(ai_msg, lang="en")

        ai_data = {"role": "assistant", "content": ai_msg}
        if ai_audio_path: ai_data["audio_path"] = ai_audio_path
        messages.append(ai_data)

        # Salvar
        st.session_state.chat_sessions[session_id]["messages"] = messages
        if len(messages) <= 2:
            new_title = generate_title(messages)
            if new_title: st.session_state.chat_sessions[session_id]["title"] = new_title

        save_chat_session(session_id, st.session_state.chat_sessions[session_id]["title"], messages)
        log_interaction_for_training(user_text, ai_msg, "English Tutor")
        
        return True

    except Exception as e:
        st.toast(f"Erro: {str(e)}", icon="❌")
        return False
