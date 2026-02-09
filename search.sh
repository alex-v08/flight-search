#!/bin/bash
# Script de conveniencia para ejecutar Flight Search AI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activar virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment no encontrado. Ejecuta: python3 setup.py"
    exit 1
fi

# Verificar si existe .env configurado
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado. Creando desde .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita .env y agrega tu BRAVE_API_KEY"
    exit 1
fi

# Ejecutar el buscador con todos los argumentos
python flight_search.py "$@"
