import json
import os
from datetime import datetime
from src.config import CHATS_DIR, DATASET_DIR, LOCAL_TODO_FILE

def load_todos():
    if os.path.exists(LOCAL_TODO_FILE):
        with open(LOCAL_TODO_FILE, "r") as f: return json.load(f)
    return []

def save_todos(todos):
    with open(LOCAL_TODO_FILE, "w") as f: json.dump(todos, f, indent=2)

def save_chat_session(session_id, title, messages):
    os.makedirs(CHATS_DIR, exist_ok=True)
    file_path = os.path.join(CHATS_DIR, f"{session_id}.json")
    data = {"title": title, "messages": messages, "last_update": datetime.now().isoformat()}
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_all_chats():
    if not os.path.exists(CHATS_DIR): return {}
    sessions = {}
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(CHATS_DIR, filename), "r") as f:
                try:
                    sessions[filename.replace(".json", "")] = json.load(f)
                except: pass
    return sessions

def log_interaction_for_training(user, ai, context):
    os.makedirs(DATASET_DIR, exist_ok=True)
    entry = {"instruction": f"Contexto: {context}\nUser: {user}", "output": ai, "date": datetime.now().isoformat()}
    try:
        with open(os.path.join(DATASET_DIR, "treino_diario.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"ERRO AO SALVAR DATASET: {e}")
