# 🚀 Configuración Rápida para Cosmic DE

## Instalación en 3 pasos

### 1️⃣ Instalar notify-send
```bash
sudo apt install libnotify-bin
```

### 2️⃣ Configurar rutas
Editar `flight_monitor_daemon.py` líneas 234-256 con tus rutas favoritas.

### 3️⃣ Iniciar monitor
```bash
./monitor.sh check      # Verificar todo
./test_notification.sh  # Probar notificaciones
./monitor.sh install    # Instalar servicio
./monitor.sh enable     # Habilitar autostart
./monitor.sh start      # Iniciar
```

## 🔔 Cómo Funciona

- **Solo nuevas oportunidades**: No te molesta con ofertas que ya conoces
- **Bandas negras únicamente**: Solo alerta cuando deal_score ≥ 90
- **Notificaciones nativas**: Aparecen en el área de notificaciones de Cosmic
- **Verificación cada 5 minutos**: Configurable en `flight_monitor_daemon.py`

## 📖 Documentación Completa

Ver **[COSMIC_SETUP.md](COSMIC_SETUP.md)** para guía detallada.

## 🎯 Comandos Útiles

```bash
./monitor.sh status    # Ver estado
./monitor.sh logs      # Ver logs en tiempo real
./monitor.sh restart   # Reiniciar después de cambios
./monitor.sh check     # Diagnosticar problemas
```

¡Disfruta de las bandas negras! ✈️
