#!/usr/bin/env python3
"""
Script de configuración para Flight Search AI
Instala dependencias y verifica configuración
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Verifica versión de Python"""
    print("🔍 Verificando Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requerido")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")


def install_dependencies():
    """Instala paquetes necesarios"""
    print("\n📦 Instalando dependencias...")

    deps = [
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.7.0",
        "pydantic>=2.5.0",
        "beautifulsoup4>=4.12.0",
    ]

    for dep in deps:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=True,
                capture_output=True,
            )
            print(f"  ✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"  ❌ Error instalando {dep}")


def check_ollama():
    """Verifica que Ollama esté corriendo"""
    print("\n🤖 Verificando Ollama...")

    import requests

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama corriendo ({len(models)} modelos disponibles)")

            # Verificar modelos recomendados
            recommended = ["llama3.1:8b", "deepseek-coder-v2:16b-lite-instruct-q4_K_M"]
            for model in recommended:
                if any(m.get("name", "").startswith(model) for m in models):
                    print(f"  ✅ {model} disponible")
                else:
                    print(f"  ⚠️  {model} no encontrado. Ejecuta: ollama pull {model}")
        else:
            print("❌ Ollama no responde correctamente")
    except Exception as e:
        print(f"❌ Error conectando a Ollama: {e}")
        print("   Asegúrate de que Ollama esté corriendo: ollama serve")


def setup_env():
    """Configura archivo .env"""
    print("\n⚙️  Configuración de entorno...")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return

    if env_example.exists():
        print("📄 Copiando .env.example a .env")
        env_file.write_text(env_example.read_text())
        print("⚠️  IMPORTANTE: Edita .env y agrega tu BRAVE_API_KEY")
    else:
        print("❌ No se encontró .env.example")


def main():
    print("=" * 60)
    print("  FLIGHT SEARCH AI - Configuración")
    print("=" * 60)

    check_python_version()
    install_dependencies()
    check_ollama()
    setup_env()

    print("\n" + "=" * 60)
    print("✅ Configuración completada!")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Edita el archivo .env y agrega tu BRAVE_API_KEY")
    print("2. Ejecuta: python flight_search.py --help")
    print("3. Ejemplo: python flight_search.py -o EZE -d MAD --date 2026-03-15")
    print("\nPara obtener API Key de Brave:")
    print("  → https://brave.com/search/api/")


if __name__ == "__main__":
    main()
