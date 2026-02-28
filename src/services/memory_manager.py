import json
import os
from src.config import MEMORY_FILE

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_fact(key, value):
    memory = load_memory()
    memory[key] = value
    # Garante que a pasta existe
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)

def get_relevant_memory(prompt):
    memory = load_memory()
    relevant = []
    
    # Se a memória estiver vazia, retorna nada
    if not memory: return ""

    # Palavras-chave para ativar memórias específicas
    triggers = {
        "nome": ["nome", "chamo", "quem sou"],
        "hardware": ["gpu", "pc", "specs", "sistema"],
        "projeto": ["jogo", "godot", "tcg", "app"]
    }
    
    prompt_lower = prompt.lower()
    
    # Estratégia: Se o prompt for curto ou genérico, injeta TUDO (pois cabe no contexto de 100k)
    # Se for muito específico, filtra.
    # Dado que temos 100k, vamos injetar a memória PRINCIPAL sempre.
    
    context_str = "FATOS CONHECIDOS SOBRE O UTILIZADOR:\n"
    for k, v in memory.items():
        context_str += f"- {k.upper()}: {v}\n"
        
    return context_str
