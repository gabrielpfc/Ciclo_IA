import streamlit as st

def inject_chat_css():
    st.markdown("""
    <style>
        /* Fundo e Layout Principal */
        .stApp {
            background-color: #020617; /* Slate 950 */
            color: #f8fafc;
        }
        
        .block-container { 
            padding-top: 2rem; 
            padding-bottom: 120px; 
            max-width: 900px; 
        }
        
        /* Estilo das Mensagens (Glassmorphism) */
        .stChatMessage { 
            border-radius: 16px; 
            margin-bottom: 15px; 
            padding: 15px;
            background: rgba(30, 41, 59, 0.4); /* Slate 800 com opacidade */
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* Avatar do User e IA */
        .stChatMessage [data-testid="chatAvatarIcon-user"] { background-color: #4f46e5; }
        .stChatMessage [data-testid="chatAvatarIcon-assistant"] { background-color: #10b981; }
        
        /* Rodapé Fixo (Input) */
        .fixed-footer {
            position: fixed; 
            bottom: 0; 
            left: 0; 
            width: 100%;
            background: linear-gradient(0deg, #020617 70%, transparent 100%);
            padding: 20px; 
            padding-left: 22rem; /* Espaço para a sidebar */
            z-index: 999; 
        }
        
        @media (max-width: 768px) {
            .fixed-footer { padding-left: 20px; }
        }
        
        /* Estilo da Caixa de Texto */
        .stTextArea textarea {
            background-color: #0f172a !important; /* Slate 900 */
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            font-size: 15px !important;
            padding: 12px !important;
            transition: all 0.2s ease;
        }
        .stTextArea textarea:focus {
            border-color: #6366f1 !important; /* Indigo 500 */
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        }
        
        /* Botão de Enviar */
        .stButton button {
            border-radius: 12px !important;
            height: 100%;
            font-weight: bold;
            transition: all 0.2s ease;
        }
        .stButton button[kind="primary"] {
            background-color: #4f46e5 !important;
            border-color: #4f46e5 !important;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #4338ca !important;
            transform: translateY(-1px);
        }
    </style>
    """, unsafe_allow_html=True)