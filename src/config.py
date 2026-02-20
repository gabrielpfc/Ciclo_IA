import os

# --- MODELO & PERFORMANCE ---
MODEL_NAME = "qwen2.5-coder:32b-instruct-q4_K_M"
OLLAMA_URL = "http://localhost:11434/v1"
OLLAMA_KEY = "ollama"

# LIMITADORES (Para não estourar a VRAM de 24GB)
MAX_CONTEXT = 8192  # 8k tokens garante que cabe na VRAM
TEMPERATURE = 0.6

# --- CAMINHOS ---
USER = os.environ.get('USER')
BASE_STORAGE = f"/run/media/{USER}/IA_Treinos"

# Banco Vetorial (Memória de Longo Prazo)
VECTOR_DB_PATH = os.path.join(BASE_STORAGE, "chromadb_store")

# Logs de Treino
DATASET_DIR = os.path.join(BASE_STORAGE, "datasets")
DATASET_FILE = os.path.join(DATASET_DIR, "treino_diario.jsonl")

# Arquivos locais do Sistema
LOCAL_TODO_FILE = "kanban_data.json" # Mudamos para formato Kanban
