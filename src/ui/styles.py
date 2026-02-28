import streamlit as st

def inject_chat_css():
    st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 8rem; }
        [data-testid="stAppViewContainer"] { overflow-x: hidden; }
        .stChatMessage { background-color: transparent !important; border: none !important; }
        div[data-testid="stChatMessage"]:nth-child(odd) div[data-testid="stMarkdownContainer"] {
            background-color: #2b313e; border: 1px solid #3b415e; color: #e0e0e0;
            padding: 12px 18px; border-radius: 12px 12px 0px 12px;
            text-align: right; margin-left: auto; min-width: 20%; max-width: 85%;
        }
        div[data-testid="stChatMessage"]:nth-child(even) div[data-testid="stMarkdownContainer"] {
            background-color: #18181b; border: 1px solid #27272a; color: #e0e0e0;
            padding: 12px 18px; border-radius: 12px 12px 12px 0px;
            margin-right: auto; min-width: 20%; max-width: 85%;
        }
        .fixed-footer {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background-color: #0E1117; padding: 15px 10px 10px 10px;
            z-index: 9999; border-top: 1px solid #333;
        }
        div[data-testid="stChatInput"] { display: none; }
        .stChatMessage .stAvatar { display: none; }
    </style>
    """, unsafe_allow_html=True)
