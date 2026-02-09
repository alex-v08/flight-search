#!/bin/bash
# Script de control del Flight Monitor Daemon

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/flight-monitor.service"
DAEMON_SCRIPT="$SCRIPT_DIR/flight_monitor_daemon.py"
USER_SERVICE_DIR="$HOME/.config/systemd/user"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  ✈️  Flight Monitor - Cosmic DE Edition${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

install_service() {
    echo -e "${YELLOW}📦 Instalando servicio systemd...${NC}"
    
    # Crear directorio si no existe
    mkdir -p "$USER_SERVICE_DIR"
    
    # Copiar archivo de servicio
    cp "$SERVICE_FILE" "$USER_SERVICE_DIR/"
    
    # Recargar systemd
    systemctl --user daemon-reload
    
    echo -e "${GREEN}✅ Servicio instalado${NC}"
    echo ""
    echo "Para iniciar automáticamente al arrancar:"
    echo "  systemctl --user enable flight-monitor.service"
}

start_daemon() {
    echo -e "${YELLOW}🚀 Iniciando Flight Monitor...${NC}"
    
    # Verificar si ya está corriendo
    if systemctl --user is-active --quiet flight-monitor.service; then
        echo -e "${YELLOW}⚠️  El servicio ya está corriendo${NC}"
        return
    fi
    
    systemctl --user start flight-monitor.service
    
    if systemctl --user is-active --quiet flight-monitor.service; then
        echo -e "${GREEN}✅ Flight Monitor iniciado${NC}"
        echo ""
        echo "Ver logs en tiempo real:"
        echo "  journalctl --user -u flight-monitor.service -f"
    else
        echo -e "${RED}❌ Error al iniciar el servicio${NC}"
        journalctl --user -u flight-monitor.service -n 20
    fi
}

stop_daemon() {
    echo -e "${YELLOW}⛔ Deteniendo Flight Monitor...${NC}"
    systemctl --user stop flight-monitor.service
    echo -e "${GREEN}✅ Flight Monitor detenido${NC}"
}

status_daemon() {
    echo -e "${BLUE}📊 Estado del servicio:${NC}"
    systemctl --user status flight-monitor.service --no-pager
    
    echo ""
    echo -e "${BLUE}📝 Últimas 10 líneas del log:${NC}"
    journalctl --user -u flight-monitor.service -n 10 --no-pager
}

enable_autostart() {
    echo -e "${YELLOW}🔧 Habilitando inicio automático...${NC}"
    systemctl --user enable flight-monitor.service
    echo -e "${GREEN}✅ El monitor se iniciará automáticamente${NC}"
}

disable_autostart() {
    echo -e "${YELLOW}🔧 Deshabilitando inicio automático...${NC}"
    systemctl --user disable flight-monitor.service
    echo -e "${GREEN}✅ Inicio automático deshabilitado${NC}"
}

view_logs() {
    echo -e "${BLUE}📖 Logs en tiempo real (Ctrl+C para salir):${NC}"
    journalctl --user -u flight-monitor.service -f
}

run_foreground() {
    echo -e "${YELLOW}🔍 Ejecutando en primer plano (Ctrl+C para detener)...${NC}"
    echo ""
    source "$SCRIPT_DIR/venv/bin/activate"
    python3 "$DAEMON_SCRIPT"
}

check_dependencies() {
    echo -e "${BLUE}🔍 Verificando dependencias (Cosmic DE)...${NC}"
    
    # Verificar entorno Cosmic
    if [ "$XDG_CURRENT_DESKTOP" = "COSMIC" ]; then
        echo -e "${GREEN}✅ Cosmic DE detectado${NC}"
    else
        echo -e "${YELLOW}⚠️  Cosmic DE no detectado (actual: $XDG_CURRENT_DESKTOP)${NC}"
    fi
    
    # Verificar notify-send
    if command -v notify-send &> /dev/null; then
        echo -e "${GREEN}✅ notify-send disponible${NC}"
        # Probar notificación
        if notify-send --app-name="Flight Monitor Test" "✈️ Test" "Notificaciones funcionando" 2>/dev/null; then
            echo -e "${GREEN}   → Notificaciones operativas${NC}"
        fi
    else
        echo -e "${RED}❌ notify-send no encontrado${NC}"
        echo "   Instalar con: sudo apt install libnotify-bin"
        echo "   O desde Pop!_Shop buscar 'libnotify'"
    fi
    
    # Verificar Python
    if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
        echo -e "${GREEN}✅ Entorno virtual Python configurado${NC}"
    else
        echo -e "${RED}❌ Entorno virtual no encontrado${NC}"
        echo "   Crear con: python3 -m venv venv"
        echo "   Luego: source venv/bin/activate && pip install -r requirements.txt"
    fi
    
    # Verificar .env
    if [ -f "$SCRIPT_DIR/.env" ]; then
        echo -e "${GREEN}✅ Archivo .env configurado${NC}"
        # Verificar que tenga la API key
        if grep -q "BRAVE_API_KEY=BSA" "$SCRIPT_DIR/.env"; then
            echo -e "${GREEN}   → BRAVE_API_KEY configurada${NC}"
        else
            echo -e "${YELLOW}   ⚠️  Verificar BRAVE_API_KEY en .env${NC}"
        fi
    else
        echo -e "${RED}❌ Archivo .env no encontrado${NC}"
        echo "   Copiar desde .env.example y configurar"
    fi
    
    # Verificar Ollama
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✅ Ollama corriendo${NC}"
        # Listar modelos disponibles
        MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | head -3)
        if [ -n "$MODELS" ]; then
            echo -e "${GREEN}   → Modelos: $(echo $MODELS | tr '\n' ', ')${NC}"
        fi
    else
        echo -e "${RED}❌ Ollama no responde${NC}"
        echo "   Iniciar con: ollama serve"
        echo "   O: systemctl --user start ollama"
    fi
    
    # Verificar DBUS (importante para notificaciones en Wayland)
    if [ -n "$DBUS_SESSION_BUS_ADDRESS" ]; then
        echo -e "${GREEN}✅ DBUS session bus activo${NC}"
    else
        echo -e "${YELLOW}⚠️  DBUS_SESSION_BUS_ADDRESS no configurado${NC}"
    fi
}

show_config() {
    echo -e "${BLUE}⚙️  Configuración actual:${NC}"
    echo ""
    echo "📁 Directorio: $SCRIPT_DIR"
    echo "🗂️  Estado: $HOME/.config/flight-monitor/state.json"
    echo "📊 Historial: $HOME/.config/flight-monitor/price_history.json"
    echo "📝 Logs: $HOME/.config/flight-monitor/monitor.log"
    echo ""
    echo "Rutas monitoreadas (ver en flight_monitor_daemon.py):"
    grep -A 1 "origin.*destination" "$DAEMON_SCRIPT" | head -20
}

show_history() {
    echo -e "${BLUE}📊 Historial de Precios:${NC}"
    echo ""
    if [ -f "$HOME/.config/flight-monitor/price_history.json" ]; then
        cd "$SCRIPT_DIR"
        source venv/bin/activate 2>/dev/null
        python3 price_history.py stats
    else
        echo "Sin datos históricos aún. El historial se construye automáticamente."
    fi
}

show_menu() {
    print_header
    echo ""
    echo "Opciones:"
    echo "  install     - Instalar servicio systemd"
    echo "  start       - Iniciar monitor"
    echo "  stop        - Detener monitor"
    echo "  restart     - Reiniciar monitor"
    echo "  status      - Ver estado actual"
    echo "  logs        - Ver logs en tiempo real"
    echo "  enable      - Habilitar inicio automático"
    echo "  disable     - Deshabilitar inicio automático"
    echo "  foreground  - Ejecutar en primer plano (debug)"
    echo "  check       - Verificar dependencias"
    echo "  config      - Ver configuración"
    echo "  history     - Ver historial de precios"
    echo ""
}

# Procesar comandos
case "$1" in
    install)
        print_header
        install_service
        ;;
    start)
        print_header
        start_daemon
        ;;
    stop)
        print_header
        stop_daemon
        ;;
    restart)
        print_header
        stop_daemon
        sleep 2
        start_daemon
        ;;
    status)
        print_header
        status_daemon
        ;;
    logs)
        print_header
        view_logs
        ;;
    enable)
        print_header
        enable_autostart
        ;;
    disable)
        print_header
        disable_autostart
        ;;
    foreground|fg)
        print_header
        run_foreground
        ;;
    check)
        print_header
        check_dependencies
        ;;
    config)
        print_header
        show_config
        ;;
    history)
        print_header
        show_history
        ;;
    *)
        show_menu
        ;;
esac
