#!/bin/bash
# Test de notificación clickable para Cosmic DE

echo "🧪 Probando notificación clickable en Cosmic DE..."
echo ""

# Test con acción clickable
RESULT=$(notify-send \
  --urgency=critical \
  --icon=airplane-mode-symbolic \
  --app-name="Flight Monitor Test" \
  --action="default=Abrir en navegador" \
  --action="dismiss=Cerrar" \
  "✈️ Test Banda Negativa Clickable" \
  "💰 ARS 145,000 | Iberia
📅 2026-03-15
⭐ Score: 95/100
Click para abrir en navegador")

echo "Resultado del click: $RESULT"

if [ "$RESULT" = "default" ]; then
    echo "✅ Click detectado! Abriendo URL..."
    xdg-open "https://www.google.com/travel/flights?q=flights%20from%20EZE%20to%20MAD"
elif [ "$RESULT" = "dismiss" ]; then
    echo "ℹ️ Notificación cerrada"
else
    echo "ℹ️ Notificación expiró o fue cerrada"
fi
