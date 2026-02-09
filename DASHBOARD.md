# Flight Search Dashboard 🎛️

Widget de escritorio transparente que busca ofertas de vuelos automáticamente y te alerta cuando encuentra bandas negativas.

## Características

✨ **Transparencia**: Ventana semi-transparente (85% opacidad)  
🔄 **Auto-búsqueda**: Actualiza ofertas cada 5 minutos  
🔥 **Alertas**: Notificaciones de escritorio para bandas negativas  
📌 **Siempre visible**: Se mantiene encima de otras ventanas  
🖱️ **Arrastrable**: Mueve el widget a donde prefieras  
🌐 **Links directos**: Click en oferta para abrir URL de reserva

## Inicio Rápido

### 1. Ejecutar Dashboard

```bash
cd /path/to/flight-search
./dashboard.sh
```

### 2. Agregar al Inicio (Opcional)

```bash
# Copiar al escritorio
cp flight-search-dashboard.desktop ~/Desktop/

# O agregar al inicio automático
mkdir -p ~/.config/autostart
cp flight-search-dashboard.desktop ~/.config/autostart/
```

## Controles

| Acción | Descripción |
|--------|-------------|
| **Arrastrar** | Mover el widget |
| **—** | Minimizar a barra pequeña |
| **×** | Cerrar aplicación |
| **🔍 Buscar** | Búsqueda manual inmediata |
| **➡️** | Cambiar a siguiente ruta |
| **👁️** | Cambiar opacidad (40% / 85%) |
| **⚙️** | Configuración avanzada |

## Configuración

### Cambiar Rutas Monitoreadas

Edita el archivo `dashboard.py` y modifica la lista `self.routes`:

```python
self.routes = [
    {"origin": "MDZ", "destination": "SLA", "name": "Mendoza → Salta"},
    {"origin": "EZE", "destination": "MAD", "name": "Buenos Aires → Madrid"},
    {"origin": "EZE", "destination": "BCN", "name": "Buenos Aires → Barcelona"},
    # Agrega más rutas aquí
]
```

### Configurar Alertas

Haz clic en **⚙️** y ajusta:
- **Intervalo de búsqueda**: Cada cuántos minutos busca
- **Score mínimo para alerta**: Por defecto 90 (bandas negativas)

## Notificaciones

Cuando se detecta una oferta con score ≥ 90, aparece:
- 🔴 **Notificación de escritorio** en Linux
- 🔥 **Resaltado rojo** en la oferta
- 🔔 **Sonido del sistema** (si está configurado)

## Personalización

### Cambiar Tamaño

En `dashboard.py`, modifica:
```python
self.root.geometry("400x600+50+50")  # Ancho x Alto + Posición X + Posición Y
```

### Cambiar Opacidad por Defecto

```python
self.root.attributes('-alpha', 0.85)  # 0.0 = invisible, 1.0 = opaco
```

### Cambiar Color de Fondo

Busca los colores hex en el código:
- `#1e1e1e` - Fondo principal (gris oscuro)
- `#2d2d2d` - Paneles secundarios
- `#4a9eff` - Azul acento
- `#4aff4a` - Verde precios buenos
- `#ff6b6b` - Rojo alertas

## Troubleshooting

### "Tkinter no instalado"
```bash
sudo apt-get install python3-tk
```

### "No aparecen notificaciones"
```bash
sudo apt-get install libnotify-bin
```

### "Error al buscar"
- Verificar que Ollama esté corriendo: `ollama serve`
- Verificar API Key de Brave en `.env`

## Integración con el Sistema

### Como Fondo de Pantalla Parcial

El dashboard tiene transparencia, puedes colocarlo:
- En una esquina del escritorio
- Sobre tu wallpaper
- En un monitor secundario

### Atajo de Teclado

Para crear un atajo de teclado en GNOME/KDE:
1. Configuración → Atajos de teclado
2. Agregar nuevo atajo
3. Comando: `/path/to/flight-search/dashboard.sh`

### Widget en Panel/KDE

Para integrar como widget de panel:
```bash
# KDE Plasma
# Agregar al panel como "Application Launcher"
# Seleccionar flight-search-dashboard.desktop
```

## Modo Headless (Sin GUI)

Si querés correr solo las alertas sin el dashboard visual:

```python
# Crear archivo monitor.py
from flight_search import FlightSearchEngine
import time
from datetime import datetime, timedelta

def monitor_fares():
    engine = FlightSearchEngine()
    while True:
        deals = engine.search_error_fares('MDZ', 'SLA', 
            (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        
        for deal in deals:
            if deal.deal_score >= 90:
                # Enviar notificación
                import subprocess
                subprocess.run([
                    'notify-send',
                    '-u', 'critical',
                    f'BANDA NEGATIVA: {deal.airline}',
                    f'{deal.currency} {deal.price:,.0f}'
                ])
        
        time.sleep(300)  # 5 minutos

monitor_fares()
```

## Performance

- **CPU**: ~5% durante búsquedas
- **RAM**: ~50MB
- **Red**: Usa Brave API (2000 queries/mes límite)

## Tips

💡 **Múltiples instancias**: Podés correr varios dashboards para diferentes rutas

💡 **Posición fija**: El dashboard recuerda su posición al moverlo

💡 **Modo minimalista**: Minimiza a barra fina cuando no lo usás

💡 **Atajo rápido**: Click en oferta = abre URL directa de reserva
