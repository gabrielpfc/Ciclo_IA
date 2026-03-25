import os
from openai import OpenAI
from src.config import OLLAMA_URL, OLLAMA_KEY, MODEL_NAME
from src.services.memory_manager import get_relevant_memory

client = OpenAI(base_url=OLLAMA_URL, api_key=OLLAMA_KEY)

def generate_title(messages):
    try:
        first_prompt = str(messages[0]['content'])[:200]
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"Resume este texto num título de 2 a 4 palavras no máximo. NÃO uses aspas. Apenas o título: {first_prompt}"}],
            temperature=0.1
        )
        title = res.choices[0].message.content.strip().replace('"', '')
        return title if title else "Sessão Ativa"
    except Exception as e:
        print(f"Erro no Titulo: {e}")
        return "Sessão Ativa"

def get_response_stream(messages, system_instruction, predict_tokens=4096):
    last_msg = messages[-1]["content"]
    long_term = get_relevant_memory(str(last_msg))
    if long_term: system_instruction += f"\n\n{long_term}"

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": system_instruction}] + messages,
            temperature=0.7,
            stream=True,
            max_tokens=predict_tokens
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        error_msg = f"❌ [ERRO OLLAMA]: {str(e)}"
        if "500" in error_msg:
            error_msg += "\n\nO modelo crashou ou não coube na VRAM. Verifica o terminal onde corre o Ollama."
        yield error_msg
