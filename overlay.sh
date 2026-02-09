#!/bin/bash
# Launcher para Flight Search Overlay (Versión Transparente)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activar virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Verificar dependencias
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "⚠️  Instalando tkinter..."
    sudo apt-get install -y python3-tk
fi

echo "🚀 Iniciando Flight Search Overlay - Modo Transparente"
echo "=================================================="
echo "💎 Fondo: Transparente"
echo "📝 Texto: Blanco"
echo "🎯 Origen: Mendoza (MDZ)"
echo "🌍 Destinos: Todos (rotativos)"
echo "⏱️  Intervalo: 10 minutos"
echo "🔥 Alertas: Banda negra (Score ≥ 90)"
echo ""
echo "Características:"
echo "  ✓ Overlay sobre el escritorio"
echo "  ✓ Siempre visible"
echo "  ✓ Click en oferta = abre navegador"
echo "  ✓ Notificaciones de escritorio"
echo ""
echo "Controles:"
echo "  - Arrastrar: Mover widget"
echo "  - Click oferta: Abrir URL"
echo "  - 🔍: Buscar ahora"
echo "  - —: Minimizar"
echo "  - ×: Cerrar"
echo ""

python3 dashboard_overlay.py
