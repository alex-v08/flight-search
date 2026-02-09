# Flight Monitor Daemon - Monitor de Bandas Negras

Sistema de monitoreo continuo para detectar errores de precio en vuelos (bandas negras) con notificaciones nativas de Wayland/Cosmic.

## 🎯 Características

- ✅ **Solo nuevas oportunidades**: Detecta y notifica únicamente deals que NO existían antes
- ✅ **Bandas negras exclusivamente**: Solo alerta cuando `deal_score >= 90`
- ✅ **Notificaciones nativas**: Compatible con Wayland/Cosmic vía `notify-send`
- ✅ **Servicio systemd**: Corre en background sin consumir recursos visuales
- ✅ **Persistencia de estado**: Guarda deals conocidos en `~/.config/flight-monitor/`
- ✅ **Logs detallados**: Registro completo de actividad

## 🚀 Instalación Rápida

### 1. Instalar dependencias del sistema

```bash
# Notificaciones de escritorio
sudo apt-get install libnotify-bin

# Verificar que está instalado
which notify-send
```

### 2. Configurar rutas a monitorear

Editar `flight_monitor_daemon.py` líneas 234-256:

```python
MONITORED_ROUTES = [
    {
        "origin": "MDZ",
        "destination": "SLA", 
        "name": "Mendoza → Salta",
        "days_ahead": 30  # Buscar vuelos a 30 días
    },
    {
        "origin": "EZE",
        "destination": "MAD",
        "name": "Buenos Aires → Madrid",
        "days_ahead": 45
    },
    # Agregar tus rutas...
]
```

### 3. Instalar como servicio systemd

```bash
cd /home/alexv/workspace/ROG/flight-search

# Instalar el servicio
./monitor.sh install

# Habilitar inicio automático al arrancar
./monitor.sh enable

# Iniciar el monitor
./monitor.sh start
```

## 📖 Uso

### Comandos principales

```bash
# Ver menú de ayuda
./monitor.sh

# Iniciar monitor
./monitor.sh start

# Detener monitor
./monitor.sh stop

# Ver estado y logs recientes
./monitor.sh status

# Ver logs en tiempo real
./monitor.sh logs

# Verificar dependencias
./monitor.sh check

# Ejecutar en primer plano (debug)
./monitor.sh foreground
```

### Habilitar/deshabilitar autostart

```bash
# Iniciar automáticamente al arrancar sesión
./monitor.sh enable

# Deshabilitar autostart
./monitor.sh disable
```

## 🔔 Notificaciones

Las notificaciones incluyen:
- 🔥 Título: Origen → Destino
- 💰 Precio y moneda
- ✈️ Aerolínea
- 📅 Fecha de salida
- ⭐ Deal score (90-100)
- 🔗 Portal fuente

**Ejemplo:**
```
🔥 Banda Negra: EZE → MAD
💰 ARS 145,000 | Iberia
📅 2026-03-15
⭐ Score: 95/100
🔗 Skyscanner
```

## ⚙️ Configuración

### Ajustar intervalo de verificación

Editar `flight_monitor_daemon.py` línea 26:

```python
CHECK_INTERVAL = 300  # Segundos (300 = 5 minutos)
```

### Cambiar umbral de banda negra

Editar línea 27:

```python
ALERT_THRESHOLD = 90  # Score mínimo (90-100)
```

### Archivos del sistema

| Archivo | Ubicación | Propósito |
|---------|-----------|-----------|
| Estado | `~/.config/flight-monitor/state.json` | Deals conocidos |
| Logs | `~/.config/flight-monitor/monitor.log` | Registro de actividad |
| Servicio | `~/.config/systemd/user/flight-monitor.service` | Unidad systemd |

## 🐛 Debug

### Ver logs del servicio

```bash
# Logs en tiempo real
journalctl --user -u flight-monitor.service -f

# Últimas 50 líneas
journalctl --user -u flight-monitor.service -n 50
```

### Ejecutar en primer plano

```bash
./monitor.sh foreground
```

Esto permite ver la salida directa y errores sin systemd.

### Verificar que todo funciona

```bash
./monitor.sh check
```

Verifica:
- ✅ notify-send instalado
- ✅ Entorno virtual Python
- ✅ Archivo .env configurado
- ✅ Ollama corriendo

### Probar notificación manualmente

```bash
notify-send --urgency=critical --icon=airplane-mode \
  "🔥 Banda Negra: Test" \
  "💰 Esto es una prueba"
```

## 📊 Monitoreo del Sistema

### Ver uso de recursos

```bash
systemctl --user status flight-monitor.service
```

### Límites configurados

- **CPU**: 20% máximo
- **Memoria**: 512MB máximo
- **Nice**: 10 (baja prioridad)

## 🔄 Actualizar Configuración

Después de editar rutas en `flight_monitor_daemon.py`:

```bash
./monitor.sh restart
```

## ⚠️ Notas Importantes

1. **Primera ejecución**: No enviará notificaciones hasta que detecte nuevas oportunidades después de cargar el estado inicial.

2. **Límites de API**: Brave Search tiene límite de 2000 queries/mes. Con 4 rutas cada 5 minutos = ~34,560 queries/mes. Ajustar intervalo si es necesario.

3. **Ollama debe estar corriendo**: El daemon necesita Ollama activo. Para auto-iniciar Ollama:
   ```bash
   systemctl --user enable ollama.service
   ```

4. **Cosmic Desktop**: Las notificaciones usan el estándar freedesktop.org, compatible con Cosmic/Wayland.

## 🎨 Integración con Cosmic

El daemon es invisible en el escritorio, solo muestra notificaciones cuando hay nuevas bandas negras. Para ver el widget visual (dashboard anterior):

```bash
./dashboard.sh  # Dashboard gráfico en ventana
```

El daemon y dashboard pueden correr simultáneamente sin conflictos.

## 📝 Desinstalación

```bash
# Detener y deshabilitar
./monitor.sh stop
./monitor.sh disable

# Eliminar servicio
rm ~/.config/systemd/user/flight-monitor.service
systemctl --user daemon-reload

# Eliminar datos (opcional)
rm -rf ~/.config/flight-monitor/
```
