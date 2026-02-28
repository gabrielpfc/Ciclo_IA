import os
import traceback
from openai import OpenAI
from src.config import OLLAMA_URL, OLLAMA_KEY, MODEL_NAME
from src.services.telemetry import Profiler
from src.services.memory_manager import get_relevant_memory

client = OpenAI(base_url=OLLAMA_URL, api_key=OLLAMA_KEY)
profiler = Profiler()

def get_system_code_context():
    """Lê o código fonte do próprio sistema para dar auto-consciência ao LLM."""
    code_context = "\n--- AUTO-CONSCIÊNCIA DO MEU CÓDIGO FONTE ---\n"
    src_path = "src"
    try:
        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        code_context += f"\nFILE: {file}\n{f.read()}\n"
        return code_context
    except: return ""

def generate_title(messages):
    try:
        last_content = messages[-1]['content']
        text_content = last_content if isinstance(last_content, str) else "Multimodal"
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"Título curto (3 palavras) para: {text_content[:100]}"}],
            extra_body={"options": {"num_ctx": 4096, "num_gpu": -1, "num_predict": 20}}
        )
        return res.choices[0].message.content.strip().replace('"', '')
    except: return None

def get_response(messages, system_instruction, temperature=0.7, images_base64=None, predict_tokens=2048):
    # Injeta a auto-consciência
    system_instruction += get_system_code_context()
    
    # Memória de longo prazo
    last_msg = messages[-1]["content"]
    long_term = get_relevant_memory(str(last_msg))
    if long_term: system_instruction += f"\n\n{long_term}"

    profiler.start()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": system_instruction}] + messages,
            temperature=temperature,
            extra_body={
                "options": {
                    "num_ctx": 32768,        # 32k confortável para a 15B
                    "num_gpu": -1, 
                    "kv_cache_type": "q8_0", 
                    "f16_kv": False,
                    "num_predict": predict_tokens 
                }
            }
        )
        ai_msg = response.choices[0].message.content
        elapsed, log_file = profiler.stop_and_save("Prompt", ai_msg)
        return ai_msg, elapsed, log_file
    except Exception as e:
        return f"ERRO: {str(e)}", 0, ""
