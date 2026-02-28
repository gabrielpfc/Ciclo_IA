import traceback
from openai import OpenAI
from src.config import OLLAMA_URL, OLLAMA_KEY, MODEL_NAME
from src.services.telemetry import Profiler
from src.services.memory_manager import get_relevant_memory, save_fact

client = OpenAI(base_url=OLLAMA_URL, api_key=OLLAMA_KEY)
profiler = Profiler()

def generate_title(messages):
    try:
        # Pega apenas texto
        last_content = messages[-1]['content']
        text_content = last_content if isinstance(last_content, str) else "Imagem"
        
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"Título curto (3 palavras) para: {text_content[:100]}"}],
            extra_body={"options": {"num_ctx": 4096, "num_gpu": -1, "num_predict": 20}}
        )
        return res.choices[0].message.content.strip().replace('"', '')
    except: return None

def get_response(messages, system_instruction, temperature=0.7, images_base64=None):
    last_user_msg_content = messages[-1]["content"]
    
    # Tratamento Multimodal
    if images_base64:
        content_payload = [{"type": "text", "text": last_user_msg_content}]
        for img_b64 in images_base64:
            content_payload.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })
        messages[-1]["content"] = content_payload
    
    # Injeção de Memória
    text_for_memory = last_user_msg_content if isinstance(last_user_msg_content, str) else "Multimodal"
    long_term_memory = get_relevant_memory(text_for_memory)
    if long_term_memory:
        system_instruction += f"\n\n{long_term_memory}"

    profiler.start()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": system_instruction}] + messages,
            temperature=temperature,
            extra_body={
                "options": {
                    "num_ctx": 100000,       # 100k Contexto
                    "num_gpu": -1,           # Força GPU
                    "kv_cache_type": "q8_0", # Cache Otimizado
                    "f16_kv": False,
                    "num_predict": -1        # -1 = Infinito (até o modelo parar ou encher o contexto)
                }
            }
        )
        ai_msg = response.choices[0].message.content
        
        # Lógica de Captura de Nome Melhorada
        if isinstance(last_user_msg_content, str):
            lower_msg = last_user_msg_content.lower()
            if "meu nome é" in lower_msg or "chamo-me" in lower_msg or "chamo me" in lower_msg:
                # Tenta extrair o nome de forma tosca mas eficaz
                parts = lower_msg.replace("meu nome é", "").replace("chamo-me", "").strip().split()
                if parts:
                    save_fact("nome", parts[0].capitalize())

        elapsed, log_file = profiler.stop_and_save(str(text_for_memory)[:50], ai_msg)
        return ai_msg, elapsed, log_file
    
    except Exception as e:
        profiler.stop_and_save("ERRO", f"ERRO: {str(e)}")
        return f"ERRO: {str(e)}", 0, ""
