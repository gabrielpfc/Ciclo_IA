import traceback
from openai import OpenAI
from src.config import OLLAMA_URL, OLLAMA_KEY, MODEL_NAME

client = OpenAI(base_url=OLLAMA_URL, api_key=OLLAMA_KEY)

def get_response(messages, system_instruction, temperature=0.3):
    full_messages = [{"role": "system", "content": system_instruction}] + messages
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=full_messages,
            temperature=temperature,
            extra_body={
                "options": {
                    "num_ctx": 65536,        # 64k de contexto
                    "num_gpu": -1,           # Força 100% na GPU
                    "f16_kv": True,          # Cache KV em alta velocidade
                    "num_thread": 16,        # Usa os núcleos do Ryzen 9 se precisar
                    "low_vram": False        # Não economiza, quer desempenho
                }
            }
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"\n[ERRO OLLAMA]: {traceback.format_exc()}")
        return f"ERRO DE INFERÊNCIA: {str(e)}"
