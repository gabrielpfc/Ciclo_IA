import streamlit as st
import os
from src.ui.styles import inject_chat_css
from src.logic.chat_processor import handle_input

def render_chat():
    inject_chat_css()
    session_id = st.session_state.current_session
    messages = st.session_state.chat_sessions[session_id]["messages"]

    chat_container = st.container(height=650)
    with chat_container:
        for msg in messages:
            with st.chat_message(msg["role"]):
                if "audio_path" in msg and os.path.exists(msg["audio_path"]): st.audio(msg["audio_path"])
                st.markdown(msg["content"])

    st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
    c_txt, c_mic, c_send = st.columns([0.7, 0.2, 0.1])
    
    with c_txt:
        user_text = st.text_area("Msg", key="input_text", placeholder="Ctrl+Enter para enviar | # para tarefas", label_visibility="collapsed", height=70)
    with c_mic:
        audio_val = st.audio_input("Mic", key="mic_input", label_visibility="collapsed")
    with c_send:
        send_btn = st.button("➤", type="primary", use_container_width=True, key="send_trigger")
    st.markdown('</div>', unsafe_allow_html=True)

    # JS ULTRA-RESILIENTE (Sem quebrar o estado do Streamlit)
    st.components.v1.html("""
    <script src="https://cdn.jsdelivr.net/npm/tributejs@5.1.3/dist/tribute.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tributejs@5.1.3/dist/tribute.css">
    <style>
        /* Estilo do menu de menções para combinar com o tema escuro */
        .tribute-container { background: #1e293b; border: 1px solid #334155; border-radius: 8px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); }
        .tribute-container ul { background: transparent; }
        .tribute-container li { color: #cbd5e1; padding: 8px 12px; border-bottom: 1px solid #334155; }
        .tribute-container li.highlight { background: #4f46e5; color: white; }
    </style>
    <script>
        const doc = window.parent.document;
        
        function applyNeuralLogic() {
            const textarea = doc.querySelector('textarea[aria-label="Msg"]');
            const sendButton = Array.from(doc.querySelectorAll('button')).find(b => b.innerText.includes('➤'));
            
            // Usamos um dataset flag em vez de clonar o nó (clonar quebra o React interno do Streamlit)
            if (textarea && sendButton && !textarea.dataset.neuralBound) {
                textarea.dataset.neuralBound = "true"; 
                
                // 1. MAPEAMENTO CTRL + ENTER
                textarea.addEventListener('keydown', (e) => {
                    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                        e.preventDefault();
                        sendButton.click();
                    }
                });

                // 2. MENTIONS #
                fetch('http://127.0.0.1:8000/mentions').then(r => r.json()).then(data => {
                    if (window.tributeInstance) {
                        window.tributeInstance.detach(textarea);
                    }
                    window.tributeInstance = new Tribute({
                        trigger: '#',
                        values: data,
                        selectTemplate: function (item) { return item.original.value; },
                        menuItemTemplate: function (item) { return item.original.display; }
                    });
                    window.tributeInstance.attach(textarea);
                }).catch(e => console.log('Mentions não disponíveis:', e));
            }
        }

        setInterval(applyNeuralLogic, 1000);
    </script>
    """, height=0)

    if send_btn or audio_val:
        if handle_input(session_id, messages, text_input=user_text, audio_input=audio_val, ui_container=chat_container):
            st.rerun()