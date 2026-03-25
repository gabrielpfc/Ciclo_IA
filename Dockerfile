FROM rocm/dev-ubuntu-22.04:6.0

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Instalar Python e dependências de sistema
RUN apt-get update && apt-get install -y \
    python3.11 python3-pip \
    ffmpeg libsm6 libxext6 \
    tesseract-ocr tesseract-ocr-por \
    alsa-utils pulseaudio-utils \
    && rm -rf /var/lib/apt/lists/*

# Atualizar PIP e instalar requisitos limpos
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

# Variáveis de ambiente para AMD
ENV HSA_OVERRIDE_GFX_VERSION=11.0.0
ENV OLLAMA_HOST=http://localhost:11434

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.runOnSave=true"]
