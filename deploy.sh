#!/bin/bash
# AUTO-INSTALLER / DEPLOYMENT SCRIPT (CID ADN)
# Asegura el despliegue íntegro del proyecto en un entorno virtual (venv)

PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/venv"

echo "🛡️ [DEPLOY] Iniciando despliegue de $(basename $PROJECT_DIR)..."

# 1. Verificación de Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado."
    exit 1
fi

# 2. Creación de venv si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creando entorno virtual en $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Entorno virtual ya existe."
fi

# 3. Activación e instalación de requerimientos
echo "📥 Instalando dependencias desde requirements.txt..."
source "$VENV_DIR/bin/activate"

# Asegurar pip actualizado
pip install --upgrade pip &> /dev/null

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️ Advertencia: No se encontró requirements.txt. Instalando dependencias base..."
    # Dependencias base comunes para proyectos Aiara
    pip install python-dotenv requests &> /dev/null
fi

# 4. Verificación de integridad
if [ $? -eq 0 ]; then
    echo "✅ [DEPLOY SUCCESS] Proyecto listo para ejecución offline."
    echo "🚀 Para usar manualmente: source venv/bin/activate"
else
    echo "❌ [DEPLOY FAILED] Hubo un error en la instalación de dependencias."
    exit 1
fi
