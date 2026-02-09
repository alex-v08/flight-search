# Flight Monitor - Guía de Instalación para Cosmic DE

## 🎯 Sistema Detectado: Cosmic DE (System76)

Tu sistema está usando **Cosmic Desktop Environment** en Wayland. El monitor está optimizado para funcionar nativamente con este entorno.

## 📦 Instalación Paso a Paso

### 1. Instalar dependencias del sistema

```bash
# Notificaciones de escritorio (si no está instalado)
sudo apt install libnotify-bin

# Verificar instalación
which notify-send
```

### 2. Configurar entorno Python

```bash
cd /home/alexv/workspace/ROG/flight-search

# Crear entorno virtual si no existe
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Verificar configuración

```bash
# Ejecutar diagnóstico completo
./monitor.sh check
```

Deberías ver:
- ✅ Cosmic DE detectado
- ✅ notify-send disponible
- ✅ Entorno virtual Python configurado
- ✅ Archivo .env configurado
- ✅ Ollama corriendo

### 4. Probar notificaciones

```bash
# Test de notificación
./test_notification.sh
```

Deberías ver una notificación en la esquina superior derecha de Cosmic con:
```
✈️ Test de Banda Negra
💰 ARS 145,000 | Iberia
📅 2026-03-15
⭐ Score: 95/100
🔗 Skyscanner
```

### 5. Configurar rutas a monitorear

Editar el archivo `flight_monitor_daemon.py` (líneas 234-256):

```bash
nano flight_monitor_daemon.py
# O con tu editor preferido
code flight_monitor_daemon.py
```

Configura tus rutas:
```python
MONITORED_ROUTES = [
    {
        "origin": "MDZ",
        "destination": "SLA", 
        "name": "Mendoza → Salta",
        "days_ahead": 30
    },
    {
        "origin": "EZE",
        "destination": "MAD",
        "name": "Buenos Aires → Madrid",
        "days_ahead": 45
    }
    # Agrega más rutas...
]
```

**Códigos IATA comunes:**
- Argentina: EZE (Ezeiza), AEP (Aeroparque), MDZ (Mendoza), COR (Córdoba), SLA (Salta)
- Europa: MAD (Madrid), BCN (Barcelona), FCO (Roma), CDG (París)
- América: MIA (Miami), JFK (Nueva York), SCL (Santiago)

### 6. Instalar como servicio systemd

```bash
# Instalar el servicio
./monitor.sh install

# Habilitar inicio automático al arrancar
./monitor.sh enable

# Iniciar el monitor
./monitor.sh start

# Verificar que está corriendo
./monitor.sh status
```

## 🔔 Comportamiento de las Notificaciones

### Características en Cosmic DE

- **Ubicación**: Esquina superior derecha (área de notificaciones de Cosmic)
- **Persistencia**: No desaparecen automáticamente (expire-time=0)
- **Prioridad**: Crítica (urgency=critical) - aparecen con máxima prioridad
- **Icono**: `airplane-mode-symbolic` (iconos nativos de Cosmic)
- **Sonido**: Usa el sonido de notificación configurado en Cosmic Settings

### Solo Nuevas Oportunidades

El monitor **NO te va a spamear** con las mismas ofertas. Sistema inteligente:

1. **Primera ejecución**: Detecta todas las bandas negras actuales y las guarda en memoria
2. **Ejecuciones siguientes**: Solo notifica si aparece una banda negra NUEVA
3. **Persistencia**: El estado se guarda en `~/.config/flight-monitor/state.json`
4. **Reinicio**: Si borras el archivo de estado, volverá a notificar todas (útil para testing)

### Ejemplo de Flujo

```
T=0min:   Encuentra 2 bandas negras (EZE→MAD, MDZ→SLA)
          → Guarda en memoria, NO notifica (son conocidas)

T=5min:   Encuentra las mismas 2 bandas negras
          → NO notifica (ya existían)

T=10min:  Encuentra 3 bandas negras (las 2 anteriores + EZE→BCN nueva)
          → 🔔 NOTIFICA solo la nueva: EZE→BCN

T=15min:  La banda negra EZE→MAD desapareció, quedan 2
          → NO notifica (desapariciones no generan alertas)

T=20min:  Vuelve a aparecer EZE→MAD
          → 🔔 NOTIFICA porque es "nueva" otra vez
```

## 🎛️ Configuración de Cosmic

### Ajustar notificaciones en Cosmic Settings

```bash
# Abrir configuración de notificaciones
cosmic-settings
```

Navega a: **Notifications** → **Flight Monitor**

- ✅ Habilitar notificaciones
- ✅ Mostrar en pantalla
- ✅ Reproducir sonido
- ✅ Mostrar en Do Not Disturb (opcional)

### Panel de notificaciones

En Cosmic puedes:
- Ver historial de notificaciones: Click en el área de notificaciones (esquina superior derecha)
- Limpiar notificaciones antiguas
- Configurar Do Not Disturb para no ser interrumpido

## 🚀 Uso Diario

### Comandos rápidos

```bash
# Ver menú de opciones
./monitor.sh

# Ver estado actual
./monitor.sh status

# Ver logs en tiempo real
./monitor.sh logs

# Reiniciar después de cambiar rutas
./monitor.sh restart

# Detener temporalmente
./monitor.sh stop
```

### Monitoreo del servicio

```bash
# Ver logs del sistema
journalctl --user -u flight-monitor.service -f

# Ver archivo de log dedicado
tail -f ~/.config/flight-monitor/monitor.log
```

## 🐛 Troubleshooting Específico de Cosmic

### Notificaciones no aparecen

1. **Verificar notify-send**:
```bash
notify-send "Test" "Funcionando?"
```

2. **Verificar DBUS**:
```bash
echo $DBUS_SESSION_BUS_ADDRESS
# Debe mostrar algo como: unix:path=/run/user/1000/bus
```

3. **Verificar permisos de notificaciones en Cosmic**:
```bash
cosmic-settings
# → Notifications → Flight Monitor → Habilitar
```

4. **Reiniciar servicio de notificaciones** (si todo falla):
```bash
systemctl --user restart cosmic-comp.service
```

### El servicio no inicia al arrancar

```bash
# Verificar que el servicio está habilitado
systemctl --user is-enabled flight-monitor.service

# Si no está habilitado
./monitor.sh enable

# Verificar que graphical-session.target está activo
systemctl --user status graphical-session.target
```

### Ollama no responde

```bash
# Verificar si Ollama está corriendo
curl http://localhost:11434/api/tags

# Iniciar Ollama manualmente
ollama serve &

# O como servicio
systemctl --user start ollama
systemctl --user enable ollama
```

### Consumo de recursos

El monitor está configurado para ser ligero:
- **CPU**: Máximo 20% de un núcleo
- **RAM**: Máximo 512MB
- **Prioridad**: Baja (nice=10)

Ver uso actual:
```bash
systemctl --user status flight-monitor.service
```

## 📊 Estadísticas y Logs

### Archivo de estado

```bash
# Ver deals conocidos
cat ~/.config/flight-monitor/state.json | jq .
```

### Logs detallados

```bash
# Últimas 50 líneas
tail -n 50 ~/.config/flight-monitor/monitor.log

# Buscar bandas negras detectadas
grep "Nueva banda negra" ~/.config/flight-monitor/monitor.log

# Buscar notificaciones enviadas
grep "Notificación enviada" ~/.config/flight-monitor/monitor.log
```

## 🔄 Actualizar Configuración

Después de editar rutas o intervalos:

```bash
./monitor.sh restart
```

El estado (deals conocidos) se preserva entre reinicios.

## 🗑️ Resetear Estado

Si quieres que vuelva a notificar todas las bandas negras:

```bash
# Borrar estado
rm ~/.config/flight-monitor/state.json

# Reiniciar servicio
./monitor.sh restart
```

## 🎨 Integración Total con Cosmic

El monitor se integra perfectamente con Cosmic DE:

- ✅ **Notificaciones nativas**: Usa el sistema de notificaciones de Cosmic
- ✅ **Iconos del sistema**: Usa iconos simbólicos de Cosmic
- ✅ **Wayland compatible**: Funciona nativamente en Wayland
- ✅ **Bajo consumo**: Optimizado para no afectar rendimiento
- ✅ **Do Not Disturb**: Respeta el modo No Molestar de Cosmic

## 🆘 Soporte

Si tienes problemas:

1. Ejecutar diagnóstico:
```bash
./monitor.sh check
```

2. Ver logs en tiempo real:
```bash
./monitor.sh logs
```

3. Ejecutar en modo debug:
```bash
./monitor.sh foreground
```

Esto mostrará toda la salida en la terminal para diagnosticar problemas.

## 🎯 Próximos Pasos

1. ✅ Instalar dependencias
2. ✅ Configurar rutas a monitorear
3. ✅ Probar notificaciones
4. ✅ Instalar servicio
5. ✅ Habilitar autostart
6. ✅ Verificar que funciona

¡Listo! Ahora recibirás notificaciones automáticas cuando aparezcan nuevas bandas negras en tus rutas favoritas. 🎉
