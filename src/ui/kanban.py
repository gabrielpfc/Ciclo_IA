import streamlit as st

def render_kanban():
    st.title("📋 Kanban & Sprints")
    st.info("Módulo em construção. Aqui ficará o quadro estilo Azure/Jira.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("To Do")
        st.write("Tarefas pendentes...")
    with col2:
        st.header("Doing")
    with col3:
        st.header("Done")
