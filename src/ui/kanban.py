import streamlit as st

def render_kanban():
    # CSS para remover margens do Streamlit e fazer o iframe ocupar 100% da tela
    st.markdown("""
        <style>
        .block-container { 
            padding: 0 !important; 
            max-width: 100% !important; 
        }
        header { visibility: hidden; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        
        /* Esconde o scrollbar do Streamlit para o Kanban rolar nativamente */
        body { overflow: hidden; }
        
        .kanban-wrapper {
            width: 100vw;
            height: 100vh;
            margin: 0;
            padding: 0;
            background-color: #020617; /* Slate 950 */
        }
        iframe { 
            width: 100%; 
            height: 100%; 
            border: none; 
        }
        </style>
    """, unsafe_allow_html=True)
    
    kanban_url = "http://127.0.0.1:5173" 
    
    st.markdown(f"""
        <div class="kanban-wrapper">
            <iframe src="{kanban_url}" allowfullscreen></iframe>
        </div>
    """, unsafe_allow_html=True)