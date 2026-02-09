#!/bin/bash
# Test de notificación para Cosmic DE

echo "🧪 Probando notificación en Cosmic DE..."
echo ""

# Test básico
notify-send \
  --urgency=critical \
  --icon=airplane-mode-symbolic \
  --app-name="Flight Monitor Test" \
  --expire-time=5000 \
  "✈️ Test de Banda Negra" \
  "💰 ARS 145,000 | Iberia
📅 2026-03-15
⭐ Score: 95/100
🔗 Skyscanner"

if [ $? -eq 0 ]; then
    echo "✅ Notificación enviada correctamente"
    echo ""
    echo "Si NO viste la notificación:"
    echo "1. Verifica que libnotify-bin esté instalado"
    echo "2. Revisa la configuración de notificaciones en Cosmic Settings"
    echo "3. Ejecuta: journalctl --user -xe | grep notify"
else
    echo "❌ Error enviando notificación"
    echo ""
    echo "Instalar con: sudo apt install libnotify-bin"
fi
