import json
import os
from src.config import MEMORY_FILE, KANBAN_DATA_PATH

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def get_relevant_memory(prompt):
    memory = load_memory()
    context_str = "--- FATOS CONHECIDOS ---\n"
    for k, v in memory.items():
        context_str += f"- {k.upper()}: {v}\n"
    
    # Injeta resumo do Kanban estruturado
    if os.path.exists(KANBAN_DATA_PATH):
        try:
            with open(KANBAN_DATA_PATH, "r", encoding="utf-8") as f:
                kb = json.load(f)
                tasks = kb.get('tasks', [])
                context_str += f"\n--- ESTADO DO KANBAN (NEURAL OS) ---\n"
                context_str += f"Total de tarefas ativas: {len(tasks)}\n"
                
                # Agrupar por status para dar melhor contexto à IA
                status_map = {}
                for t in tasks:
                    st = t.get('status', 'unknown')
                    if st not in status_map: status_map[st] = []
                    status_map[st].append(t['title'])
                
                for st, t_list in status_map.items():
                    context_str += f"[{st.upper()}]: {', '.join(t_list)}\n"
                    
                context_str += "Usa esta informação para ajudar o utilizador a gerir o seu tempo e prioridades.\n"
        except Exception as e: 
            print(f"Erro ao ler Kanban: {e}")
        
    return context_str