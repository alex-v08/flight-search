#!/bin/bash
# Listener de notificaciones clickables para Cosmic DE
# Este script alternativo usa dunst/mako si notify-send no soporta acciones

echo "🧪 Probando sistema de notificaciones con URL clickable..."

# Detectar el servidor de notificaciones
NOTIF_SERVER=$(dbus-send --print-reply --dest=org.freedesktop.Notifications \
  /org/freedesktop/Notifications \
  org.freedesktop.Notifications.GetServerInformation 2>/dev/null | grep string | head -1 | cut -d'"' -f2)

echo "📡 Servidor de notificaciones: $NOTIF_SERVER"

# URL de prueba
TEST_URL="https://www.google.com/travel/flights?q=flights%20from%20EZE%20to%20MAD%20on%202026-03-15"

# Enviar notificación con URL embebida
gdbus call --session \
  --dest org.freedesktop.Notifications \
  --object-path /org/freedesktop/Notifications \
  --method org.freedesktop.Notifications.Notify \
  "Flight Monitor" \
  0 \
  "airplane-mode-symbolic" \
  "🔥 Banda Negra: EZE → MAD" \
  "💰 ARS 145,000 | Iberia\n📅 2026-03-15\n⭐ Score: 95/100\n\n🌐 Click para ver ofertas" \
  "['default', 'Abrir navegador', 'dismiss', 'Cerrar']" \
  "{'urgency': <byte 2>, 'x-kde-urls': <'$TEST_URL'>}" \
  10000

echo ""
echo "✅ Notificación enviada con URL embebida"
echo "💡 En Cosmic, la notificación debería ser clickable"
echo ""
echo "Si no funciona, el monitor usará el método alternativo:"
echo "  - Genera URL automática según el portal (Skyscanner, Google Flights, etc)"
echo "  - Al hacer click abre xdg-open con la URL"
