import json
import os
from datetime import datetime
from src.config import LOCAL_TODO_FILE, DATASET_FILE

def load_todos():
    """Carrega a lista de tarefas do SSD."""
    if os.path.exists(LOCAL_TODO_FILE):
        try:
            with open(LOCAL_TODO_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_todos(todos):
    """Salva a lista de tarefas no SSD."""
    with open(LOCAL_TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

def log_interaction_for_training(user_text, ai_text, context_summary):
    """Salva o par Pergunta/Resposta no Disco Grande para treino noturno."""
    # Garante que a pasta existe (cria se não existir)
    os.makedirs(os.path.dirname(DATASET_FILE), exist_ok=True)
    
    entry = {
        "instruction": f"Contexto do Sistema:\n{context_summary}\n\nUsuário:\n{user_text}",
        "output": ai_text,
        "timestamp": datetime.now().isoformat()
    }
    
    # Append no arquivo JSONL
    with open(DATASET_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
