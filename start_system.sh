#!/bin/bash
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== NEURAL OS CORE: STARTUP ===${NC}"

# 1. LIMPEZA TOTAL
echo -e "${RED}[1/4] Limpando processos e portas...${NC}"
kill_port() {
    local port=$1
    fuser -k -n tcp $port 2>/dev/null
    local pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then kill -9 $pid 2>/dev/null; fi
}
kill_port 3000
kill_port 8000
pkill -9 -f "server.py" 2>/dev/null
pkill -9 -f "vite" 2>/dev/null

# 2. CONFIGURAÇÕES AMD / DISCO
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export OLLAMA_LLM_LIBRARY=rocm
export OLLAMA_MODELS="/run/media/user/Dados_Fedora1/IA_Empire/ollama_models"

# 3. LANÇAR CÉREBRO (Ollama)
if ! curl -s localhost:11434 > /dev/null; then
    echo -e "${GREEN}[2/4] Lançando Cérebro (Ollama)...${NC}"
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# 4. LANÇAR MÚSCULO (Python)
echo -e "${GREEN}[3/4] Lançando Músculo (Python)...${NC}"
source venv/bin/activate
python src/logic/server.py & 

# 5. LANÇAR INTERFACE (React)
echo -e "${GREEN}[4/4] Lançando Interface (React)...${NC}"
npm run dev &

echo -e "======================================="
echo -e "✅ SISTEMA OPERACIONAL! http://localhost:3000"
echo -e "======================================="
tail -f ~/Documentos/Repos/Ciclo_IA/neural_os.log
