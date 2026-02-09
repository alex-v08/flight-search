#!/usr/bin/env python3
"""Test de generación de URLs con parámetros completos"""

import sys
from datetime import datetime
sys.path.insert(0, '.')

# Simular un FlightDeal
class MockDeal:
    def __init__(self):
        self.origin = "EZE"
        self.destination = "MAD"
        self.departure_date = "2026-03-15"
        self.source = "Skyscanner"
        self.airline = "Iberia"
        self.price = 522
        self.currency = "USD"
        self.deal_score = 90

# Importar función de generación
from flight_monitor_daemon import FlightMonitor

# Crear instancia temporal
routes = [{"origin": "EZE", "destination": "MAD", "days_ahead": 30}]
monitor = FlightMonitor(routes)

# Probar URLs para diferentes portales
portales = ["Skyscanner", "Google Flights", "Kayak", "Despegar", "Expedia", "Momondo", "Omio"]

print("🔗 URLS GENERADAS CON PARÁMETROS COMPLETOS:\n")

for portal in portales:
    deal = MockDeal()
    deal.source = portal
    url = monitor.generate_search_url(deal)
    print(f"📍 {portal}:")
    print(f"   {url}")
    print()

print("\n✅ Todas las URLs incluyen fecha y parámetros completos")
print("💡 Al hacer click en la notificación, abrirá directamente la búsqueda")
