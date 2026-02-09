# Flight Monitor - Servicio Permanente

## ✅ EL SISTEMA YA ESTÁ CORRIENDO 24/7

El Flight Monitor **ya es un servicio permanente** que corre en background todo el tiempo.

### 🔍 Verificación Rápida

```bash
# Ver estado actual
./monitor.sh status

# Ver logs en vivo
journalctl --user -u flight-monitor.service -f
```

## 📊 Información del Servicio

### Estado Actual
```
● flight-monitor.service - ACTIVO
   PID: 256676
   Tiempo corriendo: 8 minutos
   Memoria: 21.7 MB (de 512 MB máx)
   CPU: 1.2 segundos
   Autostart: ✅ HABILITADO
```

### Funcionamiento

```
┌──────────────────────────────────┐
│   SERVICIO PERMANENTE            │
│   Corre 24/7 en background       │
└──────────────────────────────────┘
            ↓
┌──────────────────────────────────┐
│   LOOP INFINITO                  │
│   1. Buscar vuelos (4 rutas)     │
│   2. Validar precios reales      │
│   3. Comparar con historial      │
│   4. Notificar si score >= 90    │
│   5. Esperar 5 minutos           │
│   6. Repetir →                   │
└──────────────────────────────────┘
```

## 🚀 Características Activas

### ✅ Permanente
- Corre en background (no se ve)
- No necesitas abrir nada manualmente
- Siempre escuchando ofertas

### ✅ Auto-restart
- Si falla, se reinicia solo
- Configurado para reintentar cada 30 segundos
- Logs de errores guardados

### ✅ Autostart
- Se inicia automáticamente al encender el PC
- No necesitas recordar ejecutarlo
- Siempre activo después del boot

### ✅ Bajo Consumo
- Memoria: ~22 MB (casi nada)
- CPU: Solo cuando busca (cada 5 min)
- Prioridad baja (nice=10)
- Límites: max 20% CPU, max 512 MB RAM

## 📱 Notificaciones Automáticas

El servicio **ya está** enviando notificaciones cuando encuentra:

1. ✅ **Precio real** (validado >= USD 200)
2. ✅ **URL real** (extraída de Brave Search)
3. ✅ **Deal nuevo** (nunca visto antes)
4. ✅ **Score >= 90** (banda negra confirmada por historial)

### Ejemplo de Notificación
```
🔥 Banda Negra: EZE → MAD
💰 USD 476 | Iberia
📅 2026-03-15
⭐ Score: 95/100
🌐 https://www.expedia.com.ar/...

[CLICK] → Abre navegador automáticamente
```

## 🎛️ Control del Servicio

### Comandos Disponibles

```bash
# Ver estado (si está corriendo, desde cuándo, etc)
./monitor.sh status

# Ver logs en tiempo real
./monitor.sh logs

# Reiniciar (si cambias configuración)
./monitor.sh restart

# Detener temporalmente
./monitor.sh stop

# Iniciar nuevamente
./monitor.sh start

# Ver historial de precios acumulado
./monitor.sh history

# Verificar dependencias
./monitor.sh check
```

## 📊 Monitoreo

### Ver Actividad en Tiempo Real

```bash
# Logs completos en vivo
journalctl --user -u flight-monitor.service -f

# Solo bandas negras detectadas
journalctl --user -u flight-monitor.service | grep "Nueva banda negra"

# Solo nuevos mínimos históricos
journalctl --user -u flight-monitor.service | grep "NUEVO MÍNIMO"

# Notificaciones enviadas
journalctl --user -u flight-monitor.service | grep "Notificación enviada"
```

### Archivos de Configuración

| Archivo | Ubicación | Propósito |
|---------|-----------|-----------|
| Servicio | `~/.config/systemd/user/flight-monitor.service` | Configuración systemd |
| Estado | `~/.config/flight-monitor/state.json` | Deals conocidos |
| Historial | `~/.config/flight-monitor/price_history.json` | Precios históricos |
| Logs | `~/.config/flight-monitor/monitor.log` | Registro de actividad |

## 🔧 Personalización

### Cambiar Intervalo de Búsqueda

Editar `flight_monitor_daemon.py` línea 26:
```python
CHECK_INTERVAL = 300  # Segundos (300 = 5 minutos)
```

Opciones:
- `180` = 3 minutos (más frecuente)
- `300` = 5 minutos (actual, balanceado)
- `600` = 10 minutos (menos frecuente, ahorra API)

Después de cambiar:
```bash
./monitor.sh restart
```

### Cambiar Umbral de Banda Negra

Editar `flight_monitor_daemon.py` línea 27:
```python
ALERT_THRESHOLD = 90  # Score mínimo para notificar
```

Opciones:
- `95` = Solo ofertas excepcionales
- `90` = Bandas negras (actual, recomendado)
- `80` = Incluir buenos precios

### Añadir/Quitar Rutas

Editar `flight_monitor_daemon.py` líneas 234-256:
```python
MONITORED_ROUTES = [
    {
        "origin": "EZE",
        "destination": "MAD",
        "name": "Buenos Aires → Madrid",
        "days_ahead": 45
    },
    # Añadir más rutas aquí...
]
```

Después de cambiar:
```bash
./monitor.sh restart
```

## 🔄 Ciclo de Vida

### Al Iniciar el PC
```
1. Cosmic DE inicia
2. systemd carga servicios de usuario
3. flight-monitor.service arranca automáticamente
4. Daemon comienza a buscar vuelos
5. Loop infinito: buscar → esperar → buscar...
```

### Al Apagar el PC
```
1. systemd detiene servicios
2. flight-monitor.service recibe señal de parada
3. Guarda estado actual
4. Termina limpiamente
```

### Al Reiniciar
```
1. Servicio se detiene (guarda estado)
2. Sistema reinicia
3. Servicio arranca automáticamente
4. Carga estado anterior
5. Continúa monitoreando
```

## 📈 Rendimiento

### Recursos Actuales
```
Memoria: 21.7 MB (~0.14% de 16 GB)
CPU: 1.2 segundos total
Uso pico: 23.6 MB
Límite configurado: 512 MB
```

### Impacto en el Sistema
- ⚡ **Mínimo**: Casi imperceptible
- 🔋 **Batería**: Impacto despreciable
- 🌐 **Red**: Solo al buscar (cada 5 min)
- 💾 **Disco**: ~100 KB (logs + historial)

## ⚠️ Resolución de Problemas

### Servicio no está corriendo

```bash
# Ver por qué falló
systemctl --user status flight-monitor.service

# Ver logs de error
journalctl --user -u flight-monitor.service -n 50

# Reiniciar
./monitor.sh restart
```

### No recibo notificaciones

```bash
# Verificar que está buscando
./monitor.sh logs

# Verificar historial (puede que no haya deals >= 90)
./monitor.sh history

# Test de notificación manual
./test_notification.sh
```

### Errores 429 (Too Many Requests)

```bash
# Aumentar intervalo a 10 minutos
nano flight_monitor_daemon.py
# Cambiar CHECK_INTERVAL = 600

./monitor.sh restart
```

## 🎯 Resumen

**El servicio YA ESTÁ:**
- ✅ Corriendo en background
- ✅ Buscando cada 5 minutos
- ✅ Validando precios reales
- ✅ Comparando con historial
- ✅ Notificando bandas negras
- ✅ Auto-reiniciándose si falla
- ✅ Iniciándose al arrancar PC

**NO necesitas:**
- ❌ Abrir ningún programa
- ❌ Ejecutar nada manualmente
- ❌ Recordar iniciarlo
- ❌ Dejarlo corriendo en terminal

**Solo espera las notificaciones** cuando aparezcan ofertas reales con score >= 90! 🔔
