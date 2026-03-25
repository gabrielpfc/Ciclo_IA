#!/bin/bash
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== NEURAL OS: FIXING EXTERNAL DISK & START ===${NC}"

# 1. LIMPEZA DE PROCESSOS
fuser -k 8505/tcp 8000/tcp 11434/tcp 5173/tcp 2>/dev/null
pkill -9 -f "ollama"
pkill -9 -f "telemetry_server"
pkill -9 -f "vite"

# 2. VOLTAR PARA DISCO EXTERNO
TARGET_DIR="/run/media/user/Dados_Fedora/IA_Empire"
export OLLAMA_MODELS="$TARGET_DIR/ollama_models"

# 3. APAGAR O BLOCO CORROMPIDO (O que causa o Erro 500)
# Vamos apagar o blob específico que o Ollama disse estar com erro
CORRUPT_BLOB="$OLLAMA_MODELS/blobs/sha256-5a4a07cda24d5ede8a2e37ce0fbe93497171fb98c2d75843ac25fd7ef2445650"
if [ -f "$CORRUPT_BLOB" ]; then
    echo -e "${RED}Removendo bloco corrompido do Disco Externo...${NC}"
    rm -f "$CORRUPT_BLOB"
fi

# 4. CONFIGURAÇÕES AMD
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export OLLAMA_LLM_LIBRARY=rocm

# 5. INICIAR OLLAMA E REPARAR
echo -e "${GREEN}[1/4] Iniciando Ollama (Disco Externo)...${NC}"
ollama serve > ollama.log 2>&1 &
sleep 5
echo -e "${BLUE}Reparando apenas o ficheiro em falta...${NC}"
ollama pull ServiceNow-AI/Apriel-1.6-15b-Thinker:Q4_K_M

# 6. INICIAR KANBAN
echo -e "${GREEN}[2/4] Iniciando Kanban...${NC}"
cd /home/user/Documentos/Repos/sprint-board
npx vite --port 5173 --strictPort --host 127.0.0.1 > kanban.log 2>&1 &

# 7. INICIAR TELEMETRIA
echo -e "${GREEN}[3/4] Iniciando Telemetria...${NC}"
cd /home/user/Documentos/Repos/Ciclo_IA
source venv/bin/activate
python src/services/telemetry_server.py > telemetry.log 2>&1 &
sleep 2

# 8. INICIAR INTERFACE
echo -e "${GREEN}[4/4] Neural OS pronto em http://localhost:8505${NC}"
streamlit run main.py --server.port=8505 --server.address=0.0.0.0
