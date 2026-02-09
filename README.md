# ✈️ Flight Search AI - Monitor de Bandas Negras

Sistema inteligente de monitoreo permanente para detectar errores de precio en vuelos (bandas negras) usando IA local (Ollama) y búsqueda profunda con Brave Search. Optimizado para Cosmic DE (System76) con notificaciones nativas de Wayland.

## 🎯 Características Principales

- ✅ **Servicio Permanente 24/7**: Corre en background monitoreando ofertas todo el tiempo
- ✅ **Historial de Precios**: Registra el precio más bajo por ruta para comparación inteligente
- ✅ **Validación Triple**: Precios y URLs 100% reales (no generados)
- ✅ **Notificaciones Clickables**: Al hacer click abre el navegador con la oferta real
- ✅ **Solo Nuevas Oportunidades**: No spam, solo alerta bandas negras que no existían antes
- ✅ **Integración Nativa Cosmic**: Notificaciones y comportamiento optimizado para Cosmic DE
- ✅ **IA Local**: Análisis con Ollama (privacidad total, sin APIs de terceros)

## 🚀 Instalación Rápida (Cosmic DE / Pop!_OS)

### Requisitos Previos

```bash
# Instalar dependencias del sistema
sudo apt install libnotify-bin python3-venv

# Instalar y configurar Ollama
curl https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
```

### Instalación

```bash
# Clonar repositorio
git clone git@github.com:alex-v08/flight-search.git
cd flight-search

# Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar API Key de Brave Search
cp .env.example .env
nano .env  # Editar y añadir tu BRAVE_API_KEY

# Configurar rutas a monitorear
nano flight_monitor_daemon.py  # Editar MONITORED_ROUTES (líneas 234-256)

# Verificar configuración
./monitor.sh check

# Instalar e iniciar servicio
./monitor.sh install
./monitor.sh enable
./monitor.sh start
```

¡Listo! El monitor ahora corre en background 24/7 buscando bandas negras.

## 📖 Documentación

- **[COSMIC_SETUP.md](COSMIC_SETUP.md)** - Guía completa de instalación para Cosmic DE
- **[README_COSMIC.md](README_COSMIC.md)** - Setup rápido en 3 pasos
- **[SERVICIO.md](SERVICIO.md)** - Información del servicio permanente
- **[DASHBOARD.md](DASHBOARD.md)** - Sistema de historial de precios
- **[USAGE.md](USAGE.md)** - Guía de validaciones y uso
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Mejoras implementadas
- **[MONITOR.md](MONITOR.md)** - Monitor daemon documentation

## 🔧 Uso

### Comandos del Monitor

```bash
./monitor.sh status     # Ver estado del servicio
./monitor.sh logs       # Ver logs en tiempo real
./monitor.sh history    # Ver historial de precios
./monitor.sh restart    # Reiniciar después de cambios
./monitor.sh check      # Verificar dependencias
```

### Búsqueda Manual (CLI)

```bash
# Búsqueda simple
./search.sh -o EZE -d MAD --date 2026-03-15

# Buscar bandas negras
./search.sh -o MDZ -d SLA --date 2026-04-12 --error-fares-only

# Búsqueda profunda
./search.sh -o EZE -d BCN --date 2026-04-20 --deep-search
```

## 🔔 Notificaciones

Cuando detecta una banda negra (score >= 90), muestra notificación en Cosmic:

```
🔥 Banda Negra: EZE → MAD
💰 USD 476 | Iberia
📅 2026-03-15
⭐ Score: 95/100
🌐 https://www.expedia.com.ar/...

[CLICK] → Abre navegador automáticamente
```

### Scoring del Sistema

| Score | Significado |
|-------|-------------|
| 100 | 🏆 Nuevo mínimo histórico |
| 95-99 | ⚡ 5-10% sobre mínimo |
| 90-94 | 🔥 Banda negra confirmada |
| 80-89 | ✈️ Buen precio |
| < 80 | Normal (no notifica) |

## 📊 Arquitectura

```
Brave Search API
    ↓ (búsqueda profunda)
Ollama (IA Local)
    ↓ (extrae precio + URL real)
Validación Triple
    ↓ (precio real, URL real, score)
Historial de Precios
    ↓ (compara con mínimo histórico)
Notificación Cosmic
    ↓ (solo si nuevo Y score >= 90)
Navegador Web
    (abre URL real al hacer click)
```

## 🛠️ Tecnologías

- **Python 3.8+** - Lenguaje principal
- **Brave Search API** - Búsqueda web profunda
- **Ollama** - IA local (Llama 3.1, DeepSeek)
- **systemd** - Gestión de servicio permanente
- **libnotify** - Notificaciones nativas de Wayland
- **Cosmic DE** - Entorno de escritorio (System76)

## 📁 Estructura del Proyecto

```
flight-search/
├── flight_search.py              # Motor de búsqueda CLI
├── flight_monitor_daemon.py      # Daemon de monitoreo permanente
├── price_history.py              # Tracker de precios históricos
├── dashboard.py                  # Dashboard gráfico (Tkinter)
├── monitor.sh                    # Script de control del servicio
├── search.sh                     # Wrapper CLI
├── flight-monitor.service        # Configuración systemd
├── requirements.txt              # Dependencias Python
├── .env.example                  # Ejemplo de configuración
└── docs/                         # Documentación completa
    ├── COSMIC_SETUP.md
    ├── README_COSMIC.md
    ├── SERVICIO.md
    ├── DASHBOARD.md
    ├── USAGE.md
    └── IMPROVEMENTS.md
```

## 🔒 Seguridad y Privacidad

- ✅ **IA 100% local**: Ollama corre en tu máquina, nada sale a internet
- ✅ **Sin tracking**: No enviamos datos a terceros
- ✅ **API Key local**: Tu Brave API Key solo se usa localmente
- ✅ **URLs reales**: Extraídas de búsquedas, no generadas por nosotros

## ⚙️ Configuración

### Cambiar Rutas Monitoreadas

Editar `flight_monitor_daemon.py` (líneas 234-256):

```python
MONITORED_ROUTES = [
    {
        "origin": "EZE",
        "destination": "MAD",
        "name": "Buenos Aires → Madrid",
        "days_ahead": 45
    },
    # Añadir más rutas...
]
```

### Ajustar Intervalo de Búsqueda

```python
CHECK_INTERVAL = 300  # Segundos (300 = 5 minutos)
```

### Cambiar Umbral de Alerta

```python
ALERT_THRESHOLD = 90  # Score mínimo para notificar
```

## 🐛 Troubleshooting

### Ver logs del servicio

```bash
journalctl --user -u flight-monitor.service -f
```

### Servicio no inicia

```bash
./monitor.sh check      # Verificar dependencias
./monitor.sh restart    # Forzar reinicio
```

### No recibo notificaciones

```bash
./test_notification.sh  # Probar notificaciones
./monitor.sh logs       # Ver actividad
./monitor.sh history    # Ver si hay datos
```

### Errores de API (429)

```bash
# Aumentar intervalo a 10 minutos
nano flight_monitor_daemon.py
# Cambiar: CHECK_INTERVAL = 600
./monitor.sh restart
```

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto para uso personal y educativo.

## ⚠️ Disclaimer

Los precios mostrados son referencias encontradas mediante búsqueda web. **Siempre verifica** en el sitio oficial antes de comprar. Las "bandas negras" pueden cancelarse por la aerolínea sin previo aviso.

## 🙏 Agradecimientos

- **System76** - Por Cosmic DE
- **Brave** - Por la API de búsqueda
- **Ollama** - Por hacer IA local accesible
- **Comunidad Python** - Por las increíbles bibliotecas

## 📞 Contacto

- GitHub: [@alex-v08](https://github.com/alex-v08)
- Proyecto: [flight-search](https://github.com/alex-v08/flight-search)

---

**Optimizado para**: Cosmic DE (System76)  
**Modelos IA**: Llama 3.1, DeepSeek Coder v2 (via Ollama)  
**Búsqueda**: Brave Search API
