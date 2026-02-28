import os
import subprocess
import time

def test_all_voices():
    project_root = os.getcwd()
    # Caminho exato para o binário que extraímos
    piper_bin = os.path.join(project_root, "bin/piper/piper/piper")
    
    voices = {
        "English": "en_US-lessac-medium.onnx",
        "Português PT": "pt_PT-tugão-medium.onnx",
        "Português BR": "pt_BR-cadu-medium.onnx"
    }

    test_phrases = {
        "English": "Hello Gabriel. Your AMD 7900 XTX is running perfectly. Let's study English now.",
        "Português PT": "Olá Gabriel. O sistema está operacional. Estás pronto para dominar o mercado?",
        "Português BR": "E aí Gabriel! Tudo pronto para começar os treinamentos noturnos."
    }

    for lang, model in voices.items():
        print(f"\n--- Testando Voz: {lang} ---")
        model_path = os.path.join(project_root, "models/tts", model)
        output_wav = f"test_{lang.replace(' ', '_')}.wav"
        
        # Comando para gerar o áudio
        gen_cmd = f'echo "{test_phrases[lang]}" | {piper_bin} --model {model_path} --output_file {output_wav}'
        
        start = time.time()
        subprocess.run(gen_cmd, shell=True, check=True)
        print(f"Áudio gerado em {round(time.time() - start, 3)}s")
        
        # Comando para tocar o áudio no Linux
        print(f"Reproduzindo...")
        subprocess.run(f"aplay {output_wav}", shell=True)

if __name__ == "__main__":
    test_all_voices()
