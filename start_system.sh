#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

if [ "$EUID" -eq 0 ]; then
  echo -e "${RED}❌ ERRO: Não execute com 'sudo'. Rode como usuário normal.${NC}"
  exit 1
fi

echo -e "${BLUE}=== CICLO IA (AMD 7900 XTX) ===${NC}"

# Pega o diretório do script
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# --- A CORREÇÃO ESTÁ AQUI EM BAIXO ---
# Caminho Atualizado: Dados_Fedora
TARGET_DIR="/run/media/$USER/Dados_Fedora/IA_Empire"

export HSA_OVERRIDE_GFX_VERSION=11.0.0
export OLLAMA_LLM_LIBRARY=rocm
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_MAX_QUEUE=512
export OLLAMA_MODELS="$TARGET_DIR/ollama_models"
export LD_LIBRARY_PATH=/lib64:/usr/lib64

# Garante que a pasta existe antes de arrancar
mkdir -p "$TARGET_DIR/ollama_models"

echo -e "${RED}[1/4] Limpando processos...${NC}"
pkill -f "ollama serve"
pkill -f "streamlit run"
sleep 2

echo -e "${GREEN}[2/4] Iniciando Ollama em: $TARGET_DIR/ollama_models${NC}"
nohup ollama serve > ollama_debug.log 2>&1 &
OLLAMA_PID=$!

echo -n "      Aguardando conexão..."
until curl -s -f -o /dev/null "http://localhost:11434"; do
    echo -n "."
    sleep 1
done
echo -e " ✅ OK!"

echo -e "${GREEN}[3/4] Ativando Python...${NC}"
cd "$PROJECT_DIR"
source venv/bin/activate

echo -e "${GREEN}[4/4] Iniciando Interface...${NC}"
streamlit run main.py

echo -e "${RED}Encerrando...${NC}"
kill $OLLAMA_PID
