import os
import subprocess
import time
import threading
import queue

audio_queue = queue.Queue()

def _audio_worker():
    while True:
        file_path = audio_queue.get()
        if file_path is None: break
        try:
            # Fedora usa PipeWire, paplay é mais robusto que aplay
            subprocess.run(f"paplay {file_path} || aplay {file_path}", shell=True, check=False)
        except Exception as e:
            print(f"Erro áudio: {e}")
        finally:
            audio_queue.task_done()

threading.Thread(target=_audio_worker, daemon=True).start()

def generate_speech(text, lang="en"):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    piper_bin = os.path.join(project_root, "bin/piper/piper/piper")
    
    voices = {
        "en": "en_US-lessac-medium.onnx",
        "pt": "pt_PT-tugão-medium.onnx"
    }
    
    model_path = os.path.join(project_root, "models/tts", voices.get(lang, voices["en"]))
    out_dir = os.path.join(project_root, "static_audio")
    os.makedirs(out_dir, exist_ok=True)
    
    output_wav = os.path.join(out_dir, f"speech_{int(time.time()*1000)}.wav")
    
    try:
        # Comando limpo usando pipe do python
        process = subprocess.Popen(
            [piper_bin, "--model", model_path, "--output_file", output_wav],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )
        process.communicate(input=text.encode("utf-8"))
        
        if os.path.exists(output_wav):
            audio_queue.put(output_wav)
            return output_wav
    except Exception as e:
        print(f"Falha Piper: {e}")
    return None
