#!/bin/bash

# =====================================================
# ReClip - Script de inicio con auto-instalación y verificación
# =====================================================

set -e  # Salir si hay error crítico

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}==> ReClip Starting...${NC}"

# -----------------------------------------
# 1. Verificar dependencias del sistema
# -----------------------------------------
MISSING_SYSTEM=0

check_cmd() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Missing: $1${NC}"
        MISSING_SYSTEM=1
    else
        echo -e "${GREEN}Found: $1${NC}"
    fi
}

echo -e "\n${YELLOW}Checking system dependencies...${NC}"
check_cmd python3
check_cmd pip3
check_cmd ffmpeg

if [ $MISSING_SYSTEM -eq 1 ]; then
    echo -e "\n${YELLOW}Attempting to install missing packages (requires sudo)...${NC}"
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv ffmpeg
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip ffmpeg
    elif command -v brew &> /dev/null; then
        brew install python3 ffmpeg
    else
        echo -e "${RED}Could not auto-install. Please install python3, pip, and ffmpeg manually.${NC}"
        exit 1
    fi
fi

# -----------------------------------------
# 2. Verificar cookies.txt (recomendado)
# -----------------------------------------
if [ ! -f "cookies.txt" ]; then
    echo -e "${YELLOW}⚠️  cookies.txt not found. Some YouTube videos may fail.${NC}"
    echo -e "${YELLOW}   Get it from browser extension 'Get cookies.txt LOCALLY' and place it here.${NC}"
else
    echo -e "${GREEN}✅ cookies.txt found.${NC}"
fi

# -----------------------------------------
# 3. Crear y activar entorno virtual
# -----------------------------------------
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activar el entorno virtual
source venv/bin/activate

# -----------------------------------------
# 4. Instalar/actualizar dependencias Python
# -----------------------------------------
echo -e "\n${YELLOW}Installing/updating Python packages...${NC}"
pip install --upgrade pip
pip install flask yt-dlp

# Asegurar última versión de yt-dlp (útil para evitar bloqueos)
pip install --upgrade yt-dlp

# -----------------------------------------
# 5. Crear directorio de descargas si no existe
# -----------------------------------------
mkdir -p downloads

# -----------------------------------------
# 6. Lanzar la aplicación Flask
# -----------------------------------------
echo -e "\n${GREEN}Starting ReClip server...${NC}"
export FLASK_APP=app.py
PORT=${PORT:-8899}

# Mostrar direcciones de acceso
echo -e "${GREEN}ReClip will be available at:${NC}"
echo -e "  - http://localhost:$PORT"
# Obtener IP local (funciona en la mayoría de sistemas)
IP=$(hostname -I | awk '{print $1}')
if [ -n "$IP" ]; then
    echo -e "  - http://$IP:$PORT (from other devices)"
fi
echo -e "\n${YELLOW}Press Ctrl+C to stop.${NC}\n"

# Ejecutar Flask (app.py ya tiene host='0.0.0.0' y port)
python3 app.py
