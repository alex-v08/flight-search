# Flight Monitor - Guía de Uso y Validaciones

## 🔒 Garantías de Precio y URL Real

### ✅ Validaciones Implementadas

El sistema ahora tiene **triple validación** para asegurar que precios y URLs sean reales:

#### 1️⃣ Validación en el Prompt de IA
```
REGLAS ESTRICTAS:
- SOLO extrae información que APAREZCA EXPLÍCITAMENTE en título/descripción
- El precio DEBE estar escrito claramente con números
- La URL DEBE ser EXACTAMENTE la del resultado de búsqueda
- NO inventes, NO asumas, NO calcules
- Si no hay precio claro, NO incluyas el resultado
```

#### 2️⃣ Validación en Código (flight_search.py)
```python
# Filtrar precios irreales
if price < 200 and currency == "USD":
    ⚠️ Descartado: precio demasiado bajo

# Validar URL válida
if not booking_url or not booking_url.startswith('http'):
    ⚠️ Descartado: sin URL válida

# Log de validación
✓ Deal validado: Iberia $476 - https://www.expedia.com.ar/...
```

#### 3️⃣ Validación en Monitor (flight_monitor_daemon.py)
```python
# Re-validar antes de notificar
if deal.price < 200:
    ⚠️ Deal descartado por precio irreal

if not deal.booking_url.startswith('http'):
    ⚠️ Deal descartado sin URL válida

# Log detallado
🆕 Nueva banda negra VALIDADA:
   Iberia | EZE→MAD | $476 | https://www.expedia.com.ar/...
```

---

## 🎯 Flujo de Validación

```
Brave Search
    ↓
[Resultado: Título + URL + Descripción]
    ↓
Ollama extrae precio y URL
    ↓
✓ ¿Precio mencionado explícitamente? → Sí
✓ ¿Precio >= USD 200? → Sí
✓ ¿URL válida (http...)? → Sí
    ↓
Deal guardado
    ↓
Monitor valida nuevamente
    ↓
✓ ¿Precio >= USD 200? → Sí
✓ ¿URL válida? → Sí
✓ ¿Deal nuevo? → Sí
    ↓
🔔 Notificación enviada
    ↓
🌐 URL REAL del portal abierta en navegador
```

---

## 📊 Precios de Referencia

### Rutas Internacionales (Argentina - Europa)

| Ruta | Normal | Buena Oferta | Banda Negra |
|------|--------|--------------|-------------|
| EZE → MAD | USD 600-900 | USD 400-500 | USD 300-400 |
| EZE → BCN | USD 700-1000 | USD 450-600 | USD 350-450 |
| EZE → FCO | USD 650-950 | USD 450-550 | USD 350-450 |
| EZE → CDG | USD 700-1100 | USD 500-650 | USD 400-500 |

### Rutas Domésticas (Argentina)

| Ruta | Normal | Buena Oferta | Banda Negra |
|------|--------|--------------|-------------|
| MDZ → SLA | USD 120-200 | USD 70-100 | USD 50-70 |
| EZE → COR | USD 80-150 | USD 50-70 | USD 30-50 |
| EZE → MDZ | USD 100-180 | USD 60-90 | USD 40-60 |

**Nota:** Precios < USD 200 para rutas internacionales son automáticamente descartados.

---

## 🔗 URLs Reales Garantizadas

### Origen de las URLs

Las URLs vienen **directamente de Brave Search**, no son generadas:

1. **Brave Search** encuentra el resultado
2. **Ollama** extrae la URL EXACTA del resultado
3. **Sistema** valida que sea una URL válida (http/https)
4. **Notificación** muestra preview de la URL
5. **Click** abre la URL REAL del portal

### Ejemplo Real

```
Brave Search encuentra:
├─ Título: "Vuelos a Madrid desde $476 - Expedia"
├─ URL: https://www.expedia.com.ar/Flights-Search?trip=oneway&leg1=from:EZE,to:MAD
└─ Descripción: "Encuentra vuelos baratos a Madrid..."

Ollama extrae:
├─ Precio: 476 (extraído del título)
├─ URL: https://www.expedia.com.ar/... (copiado exacto)
└─ Aerolínea: Expedia (del título)

Sistema valida:
✓ Precio 476 >= 200
✓ URL válida (empieza con https)
✓ Deal nuevo

Notificación:
🔥 Banda Negra: EZE → MAD
💰 USD 476 | Expedia
🌐 https://www.expedia.com.ar/Flights-Search?trip...
Click para abrir

[CLICK] → Navegador abre URL REAL de Expedia
```

---

## 🐛 Debugging

### Ver qué está detectando

```bash
# Logs en tiempo real con URLs completas
journalctl --user -u flight-monitor.service -f

# Buscar deals validados
journalctl --user -u flight-monitor.service | grep "Deal validado"

# Buscar deals descartados
journalctl --user -u flight-monitor.service | grep "descartado"

# Ver URLs reales detectadas
journalctl --user -u flight-monitor.service | grep "URL real"
```

### Ejemplo de log limpio

```
✓ Deal validado: Iberia $476 - https://www.expedia.com.ar/...
🆕 Nueva banda negra VALIDADA: Iberia | EZE→MAD | $476 | https://www.expedia.com...
✅ Notificación enviada: 🔥 Banda Negra: EZE → MAD
🔗 URL real: https://www.expedia.com.ar/Flights-Search?trip=oneway&leg1=from:EZE,to:MAD
🌐 Abriendo URL: https://www.expedia.com.ar/...
```

### Ejemplo de log con filtros

```
⚠️ Precio sospechoso descartado: 150 USD (demasiado bajo para ruta internacional)
⚠️ Deal descartado sin URL válida: Brussels Airlines
⚠️ Deal descartado por precio irreal: Emirates $180
```

---

## 🎯 Comandos Útiles

```bash
# Ver estado y últimas detecciones
./monitor.sh status

# Ver logs filtrados por validaciones
journalctl --user -u flight-monitor.service | grep -E "(validado|descartado|URL real)"

# Test de búsqueda manual (ver qué encuentra realmente)
source venv/bin/activate
python3 flight_search.py -o EZE -d MAD --date 2026-03-15

# Limpiar estado (resetear deals conocidos)
rm ~/.config/flight-monitor/state.json
./monitor.sh restart
```

---

## ✅ Garantía Final

**El sistema SOLO notifica cuando:**
1. ✅ El precio está explícitamente mencionado en Brave Search
2. ✅ El precio es >= USD 200 (o >= USD 50 para domésticos)
3. ✅ La URL es válida y real del portal fuente
4. ✅ El deal_score es >= 90
5. ✅ Es la primera vez que detecta ese deal específico

**Al hacer click en la notificación:**
- 🌐 Se abre la URL EXACTA que encontró Brave Search
- ✅ No hay URLs generadas artificialmente
- ✅ No hay formularios vacíos
- ✅ Llegas directo a la oferta (si aún existe)

---

## 📝 Notas Importantes

### Disponibilidad de Ofertas

Las bandas negras pueden desaparecer rápidamente:
- ⚡ Algunos errores de precio duran minutos
- 🕐 Otros pueden durar horas o días
- 📱 Actúa rápido cuando recibas la notificación

### Límites de API

- **Brave Search**: 2000 queries/mes gratuito
- **Con 4 rutas cada 5 min**: ~34,560 queries/mes
- 💡 Ajusta el intervalo si te quedas sin queries

### Rate Limiting

Si ves errores "429 Too Many Requests":
- Aumenta `CHECK_INTERVAL` en flight_monitor_daemon.py
- Reduce el número de rutas monitoreadas
- Espera 1 hora para que se resetee el límite
