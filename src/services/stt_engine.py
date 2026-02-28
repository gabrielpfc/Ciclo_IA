import os
from faster_whisper import WhisperModel

# Upgrade para MEDIUM (Ryzen 9 5950X aguenta bem e é muito mais preciso)
# Se achar lento (o que duvido), volte para "small"
MODEL_SIZE = "medium"
model = None

def get_model():
    global model
    if model is None:
        print(f"[STT] Carregando Whisper ({MODEL_SIZE}) na CPU...")
        model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return model

def transcribe_audio(audio_path):
    if not os.path.exists(audio_path): return "", ""

    model = get_model()
    
    try:
        # TRUQUE DO GENERAL:
        # 1. language="en": Forçamos inglês. Acaba o erro de detetar japonês.
        # 2. initial_prompt: Dá contexto ao modelo para ele entender sotaques e pausas.
        # 3. beam_size=5: Tenta mais variações para garantir precisão.
        
        segments, info = model.transcribe(
            audio_path, 
            beam_size=5, 
            language="en", 
            initial_prompt="This is a conversation with a student learning English. The speech might have an accent."
        )
        
        text = " ".join([segment.text for segment in segments]).strip()
        
        # Filtro de Alucinação (Se o texto for vazio ou lixo repetitivo)
        if not text or text.lower() in ["thank you.", "subtitles by", "you"]:
            return "", "en"
            
        print(f"[STT] Texto: {text}")
        return text, "en"
        
    except Exception as e:
        print(f"[STT] Erro: {e}")
        return "", ""
