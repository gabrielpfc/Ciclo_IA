import streamlit as st
from src.services.data_handler import save_todos

def render_sidebar():
    """Renderiza a barra lateral de tarefas."""
    with st.sidebar:
        st.header("🧠 Regras & Tarefas")
        st.caption("Memória de Curto Prazo")
        
        # Input de Nova Tarefa
        new_t = st.text_input("Nova entrada", key="new_task_input")
        if st.button("Adicionar", use_container_width=True) and new_t:
            st.session_state.todos.append({"task": new_t, "done": False})
            save_todos(st.session_state.todos)
            st.rerun()
        
        st.divider()
        
        # Listagem de Tarefas
        to_delete = []
        if not st.session_state.todos:
            st.info("Nenhuma regra ativa.")
            
        for i, t in enumerate(st.session_state.todos):
            c1, c2 = st.columns([0.85, 0.15])
            
            # Checkbox (Concluir)
            is_done = c1.checkbox(t["task"], value=t["done"], key=f"c_{i}")
            if is_done != t["done"]:
                st.session_state.todos[i]["done"] = is_done
                save_todos(st.session_state.todos)
                st.rerun() # Rerun para atualizar contexto imediatamente
            
            # Botão Delete
            if c2.button("X", key=f"d_{i}"):
                to_delete.append(i)
        
        # Processar Deleção
        if to_delete:
            for i in sorted(to_delete, reverse=True):
                del st.session_state.todos[i]
            save_todos(st.session_state.todos)
            st.rerun()
