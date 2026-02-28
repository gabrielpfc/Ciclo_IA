#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

if [ "$EUID" -eq 0 ]; then
  echo -e "${RED}❌ ERRO: Não execute com 'sudo'.${NC}"
  exit 1
fi

echo -e "${BLUE}=== CICLO IA (AMD 7900 XTX) ===${NC}"

# Caminho do Disco
TARGET_DIR="/run/media/$USER/Dados_Fedora/IA_Empire"

# --- VERIFICAÇÃO DE MONTAGEM ---
if [ ! -d "$TARGET_DIR" ]; then
  echo -e "${RED}❌ ERRO: O disco 'Dados_Fedora' não está montado!${NC}"
  echo -e "Abra o explorador de ficheiros e clique no disco para o montar."
  exit 1
fi

export HSA_OVERRIDE_GFX_VERSION=11.0.0
export OLLAMA_LLM_LIBRARY=rocm
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_MAX_QUEUE=512
export OLLAMA_MODELS="$TARGET_DIR/ollama_models"
export LD_LIBRARY_PATH=/lib64:/usr/lib64

echo -e "${RED}[1/4] Limpando processos...${NC}"
pkill -f "ollama serve"
pkill -f "streamlit run"
sleep 2

echo -e "${GREEN}[2/4] Iniciando Ollama...${NC}"
nohup ollama serve > ollama_debug.log 2>&1 &
OLLAMA_PID=$!

echo -n "      Aguardando conexão..."
until curl -s -f -o /dev/null "http://localhost:11434"; do
    echo -n "."
    sleep 1
done
echo -e " ✅ OK!"

echo -e "${GREEN}[3/4] Ativando Python...${NC}"
source venv/bin/activate

echo -e "${GREEN}[4/4] Iniciando Interface...${NC}"
streamlit run main.py

echo -e "${RED}Encerrando...${NC}"
kill $OLLAMA_PID
