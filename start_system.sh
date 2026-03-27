#!/bin/bash
# Cores para o terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== NEURAL OS CORE: STARTUP ===${NC}"

# 1. LIMPEZA (Apenas portas e servidor Python)
# REMOVIDO: pkill brave (Para não fechar o teu navegador de trabalho)
fuser -k 3000/tcp 2>/dev/null
fuser -k 8000/tcp 2>/dev/null
pkill -9 -f "server.py" 2>/dev/null

# 2. VERIFICAR OLLAMA
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
    echo -e "${BLUE}[!] Iniciando Ollama...${NC}"
    export HSA_OVERRIDE_GFX_VERSION=11.0.0
    export OLLAMA_MODELS="/run/media/user/Dados_Fedora1/IA_Empire/ollama_models"
    ollama serve > /dev/null 2>&1 &
    sleep 5
fi

# 3. LANÇAR COMPONENTES
export PYTHONPATH=$PYTHONPATH:$(pwd)
source venv/bin/activate
python3 src/logic/server.py & 
npm run dev &

echo -e "======================================="
echo -e "${GREEN}✅ SISTEMA OPERACIONAL (MODO TRABALHO SEGURO)!${NC}"
echo -e "======================================="
tail -f ~/Documentos/Repos/Ciclo_IA/neural_os.log
