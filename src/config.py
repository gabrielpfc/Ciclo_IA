import os

# --- MODELO ---
MODEL_NAME = "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M"
OLLAMA_URL = "http://localhost:11434/v1"
OLLAMA_KEY = "ollama"

# --- CAMINHOS ATUALIZADOS (Dados_Fedora) ---
USER = os.environ.get('USER', 'user')

# Caminho Base correto
BASE_STORAGE = f"/run/media/{USER}/Dados_Fedora/IA_Empire"

# Subpastas
DATASET_DIR = os.path.join(BASE_STORAGE, "datasets")
LOGS_DIR = os.path.join(BASE_STORAGE, "logs")
CHATS_DIR = os.path.join(BASE_STORAGE, "conversas_salvas")
OLLAMA_DIR = os.path.join(BASE_STORAGE, "ollama_models")

# Memória Global
MEMORY_FILE = os.path.join(BASE_STORAGE, "global_memory.json")

# Caminho local
LOCAL_TODO_FILE = "todo_list.json"
