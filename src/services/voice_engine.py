import os
import subprocess
import time
import threading

def play_audio_local(file_path):
    """Toca o áudio diretamente no Linux (Auto-Play) em background"""
    def _play():
        try:
            # Tenta paplay (PulseAudio - Melhor qualidade) ou aplay (ALSA - Padrão)
            subprocess.run(f"paplay {file_path} || aplay {file_path}", shell=True, check=False)
        except Exception as e:
            print(f"Erro ao tocar áudio: {e}")
            
    # Roda em thread separada para não travar a UI enquanto fala
    threading.Thread(target=_play).start()

def generate_speech(text, lang="en"):
    project_root = os.getcwd()
    piper_bin = os.path.join(project_root, "bin/piper/piper/piper")
    
    voices = {
        "en": "en_US-lessac-medium.onnx",
        "pt": "pt_PT-tugão-medium.onnx"
    }
    
    model_name = voices.get(lang, voices["en"])
    model_path = os.path.join(project_root, "models/tts", model_name)
    
    # Nome único para evitar cache de browser
    output_filename = f"speech_{int(time.time())}.wav"
    output_path = os.path.join(project_root, "static_audio", output_filename)
    
    # Garante que a pasta existe (Streamlit precisa de pasta estática às vezes, mas aqui usamos caminho absoluto)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    command = f'echo "{text}" | {piper_bin} --model {model_path} --output_file {output_path}'
    
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
        
        # --- AUTO PLAY IMEDIATO ---
        play_audio_local(output_path)
        
        return output_path
    except Exception as e:
        print(f"Erro TTS: {e}")
        return None
