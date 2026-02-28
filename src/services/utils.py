import os
import time
import glob

def cleanup_audio_files(folder_path=".", max_age_seconds=3600):
    """Apaga arquivos .wav mais velhos que 1 hora para poupar disco."""
    try:
        files = glob.glob(os.path.join(folder_path, "*.wav"))
        # Também limpa na pasta static_audio se existir
        files += glob.glob(os.path.join(folder_path, "static_audio", "*.wav"))
        
        deleted = 0
        current_time = time.time()
        
        for f in files:
            file_mod_time = os.path.getmtime(f)
            if (current_time - file_mod_time) > max_age_seconds:
                os.remove(f)
                deleted += 1
                
        if deleted > 0:
            print(f"[MANUTENÇÃO] Limpeza efetuada: {deleted} arquivos de áudio removidos.")
    except Exception as e:
        print(f"[MANUTENÇÃO] Erro ao limpar áudio: {e}")
