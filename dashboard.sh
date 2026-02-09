#!/bin/bash
# Launcher para Flight Search Dashboard

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activar virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Verificar dependencias de GUI
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "⚠️  Tkinter no instalado. Instalando..."
    sudo apt-get update && sudo apt-get install -y python3-tk
fi

# Ejecutar dashboard
echo "🚀 Iniciando Flight Search Dashboard..."
echo "💡 El dashboard es semi-transparente y se mantiene siempre visible"
echo "🔍 Buscará ofertas automáticamente cada 5 minutos"
echo "🔥 Te alertará cuando encuentre bandas negras"
echo ""
echo "Controles:"
echo "  - Arrastrar para mover"
echo "  - — para minimizar"
echo "  - × para cerrar"
echo "  - 👁️ para cambiar opacidad"
echo ""

python3 dashboard.py
