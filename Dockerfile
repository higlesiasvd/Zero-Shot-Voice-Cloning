# IMPORTANTE: Este Dockerfile usa emulación x86 para compatibilidad con Mac M4
# Será más lento pero funcionará correctamente con XTTS-v2

FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV COQUI_TOS_AGREED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    curl \
    libsndfile1 \
    ffmpeg \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instalar PyTorch (versión CPU para ser más ligero)
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Instalar dependencias base
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    scipy==1.10.1 \
    librosa==0.10.1 \
    soundfile==0.12.1 \
    matplotlib==3.7.0 \
    pydub==0.25.1 \
    datasets==2.14.5 \
    transformers==4.35.0

# Instalar Coqui TTS (con todas sus dependencias)
RUN pip install --no-cache-dir TTS==0.22.0

# Instalar resemblyzer para métricas
RUN pip install --no-cache-dir resemblyzer

# Instalar pyarrow compatible
RUN pip install --no-cache-dir "pyarrow<15.0.0"

# Copiar código
COPY . .

RUN mkdir -p audio_samples results

CMD ["python", "main.py"]