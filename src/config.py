import os

# --- AMBIENTE ---
USER_HOST = "user"

# --- MODELO (Apriel nos 9GB do Fedora1) ---
MODEL_NAME = "ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M"
OLLAMA_URL = "http://localhost:11434/v1"
OLLAMA_KEY = "ollama"

# --- STORAGE (SSD Interno para Logs/Chats) ---
BASE_INTERNAL = "/home/user/Documentos/Repos/Ciclo_IA/storage"
os.makedirs(BASE_INTERNAL, exist_ok=True)
CHATS_DIR = os.path.join(BASE_INTERNAL, "conversas_salvas")
LOGS_DIR = os.path.join(BASE_INTERNAL, "logs")
DATASET_DIR = os.path.join(BASE_INTERNAL, "datasets")
MEMORY_FILE = os.path.join(BASE_INTERNAL, "global_memory.json")
VECTOR_DB_PATH = os.path.join(BASE_INTERNAL, "vector_db")
LOCAL_TODO_FILE = "/home/user/Documentos/Repos/Ciclo_IA/todo_list.json"

# --- BOT & BROWSER ---
BRAVE_PATH = "/usr/bin/brave-browser"
BRAVE_USER_DATA = f"/home/{USER_HOST}/.config/brave-browser"
SYSTEM_PASSWORD = "TuaSenhaForteAqui"
