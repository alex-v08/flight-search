# Flight Search AI - Skill para Agentes

## Descripción

Skill para buscar pasajes de avión usando IA local (Ollama) y búsqueda profunda con Brave Search. Detecta bandas negras (errores de precio), analiza conexiones y compara reputación de aerolíneas.

## Requisitos

```bash
# Dependencias ya instaladas en el proyecto
pip install requests python-dotenv rich

# Variables de entorno necesarias
cat /home/alexv/workspace/ROG/flight-search/.env
# BRAVE_API_KEY=BSApP-v-1YFxsDMCpzj7UwJr43tlTpF
# OLLAMA_URL=http://localhost:11434
```

## Uso Rápido

### 1. Búsqueda Simple

```bash
cd /home/alexv/workspace/ROG/flight-search
./search.sh -o [ORIGEN] -d [DESTINO] --date [YYYY-MM-DD]
```

### 2. Búsqueda de Bandas Negras

```bash
./search.sh -o MDZ -d SLA --date 2026-04-12 --error-fares-only
```

### 3. Búsqueda Profunda

```bash
./search.sh -o EZE -d MAD --date 2026-03-15 --deep-search
```

### 4. Guardar Resultados

```bash
./search.sh -o MDZ -d SLA --date 2026-04-12 --save resultados.md
```

## Parámetros

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `-o, --origin` | Código IATA origen | EZE, MDZ, BCN |
| `-d, --destination` | Código IATA destino | MAD, SLA, JFK |
| `--date` | Fecha de salida | 2026-04-15 |
| `--error-fares-only` | Solo buscar errores de precio | -- |
| `--deep-search` | Búsqueda más exhaustiva | -- |
| `--model` | Modelo Ollama a usar | llama3.1:8b, deepseek-coder-v2:16b |
| `--save` | Guardar en archivo markdown | --save resultados.md |
| `--no-save` | No guardar archivo de resultados | -- |

## Códigos IATA Comunes

### Argentina
- **EZE** - Buenos Aires (Ezeiza)
- **AEP** - Buenos Aires (Aeroparque)
- **MDZ** - Mendoza
- **COR** - Córdoba
- **SLA** - Salta

### Europa
- **MAD** - Madrid
- **BCN** - Barcelona
- **CDG** - París
- **LHR** - Londres
- **FCO** - Roma
- **AMS** - Ámsterdam

### América
- **JFK** - Nueva York
- **MIA** - Miami
- **LAX** - Los Ángeles
- **GRU** - São Paulo
- **SCL** - Santiago

## Interpretación de Resultados

### Score de Oferta (deal_score)
- **90-100**: 🔥 Banda negra probable (error de precio)
- **70-89**: ⭐ Excelente oferta
- **50-69**: ✈️ Buen precio
- **<50**: Precio normal

### Reputación de Aerolíneas
- **90-100**: Qatar Airways, Singapore Airlines
- **80-89**: Emirates, Air France, KLM, Lufthansa
- **70-79**: Iberia, LATAM, American Airlines
- **60-69**: Aerolíneas Argentinas, JetSMART

### Portales Analizados
- Skyscanner
- Google Flights
- Kayak
- Despegar
- Expedia
- Secret Flying (errores de precio)
- Fly4free

## Ejemplos de Búsquedas

### Escapada de Fin de Semana
```bash
./search.sh -o EZE -d COR --date 2026-03-15 --error-fares-only
```

### Viaje Internacional
```bash
./search.sh -o EZE -d MAD --date 2026-06-15 --deep-search
```

### Búsqueda con Modelo Potente
```bash
./search.sh -o MDZ -d SLA --date 2026-04-12 --model deepseek-coder-v2:16b-lite-instruct-q4_K_M
```

## Archivos Generados

Los resultados se guardan automáticamente en archivos markdown con:
- Lista de ofertas encontradas
- Links directos a reserva
- Análisis de IA
- Recomendaciones

Formato: `flight_search_[ORIGEN]_[DESTINO]_[TIMESTAMP].md`

## Modelos Ollama Disponibles

| Modelo | Uso | Velocidad |
|--------|-----|-----------|
| llama3.1:8b | Búsquedas rápidas | ⚡ Rápido |
| deepseek-coder-v2:16b | Análisis profundo | 🐢 Lento |
| moondream:latest | Visión (imágenes) | ⚡ Rápido |

## Troubleshooting

### Error 429 - Too Many Requests
- Esperar unos minutos entre búsquedas
- Brave API tiene límite de 2000 queries/mes

### Ollama no responde
```bash
ollama serve
```

### No se encuentran ofertas
- Probar diferentes fechas
- Usar `--deep-search` para búsqueda exhaustiva
- Verificar códigos IATA

## Integración con Otros Proyectos

```python
import sys
sys.path.insert(0, '/home/alexv/workspace/ROG/flight-search')
from flight_search import FlightSearchEngine

engine = FlightSearchEngine()
deals = engine.search_error_fares('MDZ', 'SLA', '2026-04-12')
engine.display_results(deals)
```

## Notas Importantes

⚠️ **Disclaimer**: Los precios mostrados son referencias encontradas en búsqueda web. Siempre verificar en el sitio oficial antes de comprar. Las "bandas negras" pueden cancelarse.

✅ **Verificar siempre**:
1. Fechas disponibles
2. Condiciones de la tarifa
3. Equipaje incluido
4. Sitio oficial de la aerolínea
