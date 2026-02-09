#!/usr/bin/env python3
"""
Flight Monitor Daemon - Monitoreo de bandas negras para Wayland Cosmic
Servicio de fondo que detecta NUEVAS oportunidades y envía notificaciones nativas
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Set
import logging
from dataclasses import asdict

# Añadir path del proyecto
sys.path.insert(0, str(Path(__file__).parent))
from flight_search import FlightSearchEngine, FlightDeal
from price_history import PriceHistoryTracker

# Configuración
STATE_FILE = Path.home() / ".config" / "flight-monitor" / "state.json"
LOG_FILE = Path.home() / ".config" / "flight-monitor" / "monitor.log"
CHECK_INTERVAL = 300  # 5 minutos
ALERT_THRESHOLD = 90  # Score mínimo para banda negra


class FlightMonitor:
    """Monitor de vuelos con detección de nuevas oportunidades"""

    def __init__(self, routes: List[Dict]):
        self.routes = routes
        self.engine = None
        self.known_deals: Set[str] = set()
        
        # Crear directorios
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Cargar estado previo
        self.load_state()

    def load_state(self):
        """Carga estado de deals conocidos"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.known_deals = set(data.get('known_deals', []))
                self.logger.info(f"Estado cargado: {len(self.known_deals)} deals conocidos")
            except Exception as e:
                self.logger.error(f"Error cargando estado: {e}")

    def save_state(self):
        """Guarda estado de deals conocidos"""
        try:
            data = {
                'known_deals': list(self.known_deals),
                'last_update': datetime.now().isoformat()
            }
            with open(STATE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando estado: {e}")

    def deal_fingerprint(self, deal: FlightDeal) -> str:
        """Genera un ID único para un deal"""
        return f"{deal.airline}|{deal.origin}|{deal.destination}|{deal.price}|{deal.departure_date}"

    def send_notification(self, deal: FlightDeal):
        """Envía notificación nativa de Cosmic/Wayland con URL REAL clickable"""
        title = f"🔥 Banda Negra: {deal.origin} → {deal.destination}"
        
        # Mostrar la URL real en la notificación
        url_preview = deal.booking_url[:60] + "..." if len(deal.booking_url) > 60 else deal.booking_url
        
        body = (
            f"💰 {deal.currency} {deal.price:,.0f} | {deal.airline}\n"
            f"📅 {deal.departure_date}\n"
            f"⭐ Score: {deal.deal_score:.0f}/100\n"
            f"🌐 {url_preview}\n"
            f"Click para abrir"
        )
        
        # Usar URL REAL del deal (extraída de Brave Search)
        booking_url = deal.booking_url
        
        try:
            # Notificación compatible con Cosmic DE (System76)
            # Usa el protocolo estándar freedesktop.org con acción clickable
            result = subprocess.run([
                'notify-send',
                '--urgency=critical',
                '--icon=airplane-mode-symbolic',
                '--app-name=Flight Monitor',
                '--category=network.flight',
                '--expire-time=0',
                '--hint=string:desktop-entry:flight-monitor',
                # Añadir acción por defecto al hacer click
                '--action=default=Abrir en navegador',
                title,
                body
            ], capture_output=True, text=True)
            
            # Si el usuario hace click, abrir URL
            if result.returncode == 0:
                self.logger.info(f"✅ Notificación enviada: {title}")
                self.logger.info(f"🔗 URL real: {booking_url}")
                
                # Si notify-send retorna con acción, abrir navegador
                if result.stdout.strip() == 'default':
                    self.open_url(booking_url)
                else:
                    # En Cosmic, la notificación se queda esperando click
                    # Abrir URL inmediatamente después de mostrar notificación
                    time.sleep(1)
                    self.open_url(booking_url)
            else:
                self.logger.warning(f"⚠️ notify-send salió con código {result.returncode}")
                
        except FileNotFoundError:
            self.logger.warning("⚠️ notify-send no disponible, instalando...")
            self.install_notify()
        except Exception as e:
            self.logger.error(f"❌ Error enviando notificación: {e}")
    
    def generate_search_url(self, deal: FlightDeal) -> str:
        """Genera URL de búsqueda con TODOS los parámetros completos"""
        origin = deal.origin
        dest = deal.destination
        date = deal.departure_date.replace('-', '')  # Formato YYYYMMDD
        date_formatted = deal.departure_date  # YYYY-MM-DD
        
        # URLs completamente formadas con todos los parámetros
        urls = {
            'skyscanner': f"https://www.skyscanner.com.ar/transport/flights/{origin.lower()}/{dest.lower()}/{date_formatted}/?adultsv2=1&cabinclass=economy&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0",
            
            'google': f"https://www.google.com/travel/flights/search?tfs=CBwQAhooEgoyMDI2LTAzLTE1agcIARIDRVpFcgcIARIDTUFEQAFIAXABggELCP___________wGYAQE&hl=es&curr=ARS",
            
            'kayak': f"https://www.kayak.com.ar/flights/{origin}-{dest}/{date_formatted}?sort=bestflight_a&fs=stops=0",
            
            'despegar': f"https://www.despegar.com.ar/shop/flights/results/oneway/{origin}/{dest}/{date_formatted}/1/0/0",
            
            'momondo': f"https://www.momondo.com.ar/flightsearch/?Search=true&TripType=1&SegNo=1&SO0={origin}&SD0={dest}&SDP0={date_formatted}&AD=1&currency=ARS",
            
            'expedia': f"https://www.expedia.com.ar/Flights-Search?trip=oneway&leg1=from:{origin},to:{dest},departure:{date_formatted}&passengers=adults:1&mode=search",
            
            'omio': f"https://www.omio.com.ar/vuelos/{origin}/{dest}?departure={date_formatted}&adults=1",
        }
        
        # Detectar fuente y retornar URL apropiada
        source_lower = deal.source.lower()
        
        if 'skyscanner' in source_lower:
            return urls['skyscanner']
        elif 'google' in source_lower or 'flights' in source_lower:
            return urls['google']
        elif 'kayak' in source_lower:
            return urls['kayak']
        elif 'despegar' in source_lower:
            return urls['despegar']
        elif 'momondo' in source_lower:
            return urls['momondo']
        elif 'expedia' in source_lower:
            return urls['expedia']
        elif 'omio' in source_lower:
            return urls['omio']
        else:
            # Fallback: Google Flights con búsqueda específica
            return f"https://www.google.com/travel/flights?q=Flights+to+{dest}+from+{origin}+on+{date_formatted}+oneway"
    
    def open_url(self, url: str):
        """Abre URL en el navegador predeterminado"""
        try:
            subprocess.run(['xdg-open', url], check=False)
            self.logger.info(f"🌐 Abriendo URL: {url}")
        except Exception as e:
            self.logger.error(f"❌ Error abriendo URL: {e}")

    def install_notify(self):
        """Instala libnotify si no está disponible (Pop!_OS/Cosmic)"""
        self.logger.info("💡 Para instalar notificaciones en Pop!_OS/Cosmic:")
        self.logger.info("   sudo apt install libnotify-bin")
        self.logger.info("💡 O usando el Pop!_Shop buscar 'libnotify'")
        
        # Intentar instalación automática
        try:
            result = subprocess.run([
                'pkexec', 'apt', 'install', '-y', 'libnotify-bin'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.logger.info("✅ libnotify-bin instalado correctamente")
            else:
                self.logger.warning(f"⚠️ Instalación cancelada o falló: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.logger.warning("⚠️ Timeout en instalación")
        except Exception as e:
            self.logger.error(f"Error en instalación: {e}")

    def check_route(self, route: Dict) -> List[FlightDeal]:
        """Verifica una ruta y busca bandas negras"""
        origin = route['origin']
        destination = route['destination']
        date = (datetime.now() + timedelta(days=route.get('days_ahead', 30))).strftime('%Y-%m-%d')
        
        self.logger.info(f"🔍 Buscando: {origin} → {destination} ({date})")
        
        try:
            if not self.engine:
                self.engine = FlightSearchEngine()
            
            deals = self.engine.search_error_fares(origin, destination, date)
            
            # Filtrar solo bandas negras
            black_friday_deals = [
                deal for deal in deals 
                if deal.deal_score >= ALERT_THRESHOLD
            ]
            
            return black_friday_deals
        
        except Exception as e:
            self.logger.error(f"❌ Error buscando {origin}->{destination}: {e}")
            return []

    def process_deals(self, deals: List[FlightDeal]) -> List[FlightDeal]:
        """Procesa deals y detecta nuevos - VALIDANDO precios y URLs reales + historial"""
        new_deals = []
        
        for deal in deals:
            # VALIDACIÓN ADICIONAL: precio y URL deben ser reales
            if deal.price < 200:
                self.logger.warning(f"⚠️ Deal descartado por precio irreal: {deal.airline} ${deal.price}")
                continue
            
            if not deal.booking_url or not deal.booking_url.startswith('http'):
                self.logger.warning(f"⚠️ Deal descartado sin URL válida: {deal.airline}")
                continue
            
            # Actualizar historial de precios
            is_new_min = self.price_tracker.update_price(
                deal.origin, 
                deal.destination, 
                deal.price,
                deal.currency,
                deal.source
            )
            
            # Recalcular deal_score basándose en historial
            historical_score, explanation = self.price_tracker.calculate_deal_quality(
                deal.origin,
                deal.destination,
                deal.price
            )
            
            # Usar el score histórico si es más alto
            if historical_score > deal.deal_score:
                deal.deal_score = historical_score
                deal.notes = f"{explanation}. {deal.notes}"
                self.logger.info(f"📊 Score ajustado por historial: {deal.deal_score:.0f} - {explanation}")
            
            fingerprint = self.deal_fingerprint(deal)
            
            # Notificar si es nuevo Y supera el umbral
            if fingerprint not in self.known_deals and deal.deal_score >= ALERT_THRESHOLD:
                new_deals.append(deal)
                self.known_deals.add(fingerprint)
                
                if is_new_min:
                    self.logger.info(f"🏆 NUEVO MÍNIMO HISTÓRICO!")
                
                self.logger.info(
                    f"🆕 Nueva banda negra VALIDADA: "
                    f"{deal.airline} | {deal.origin}→{deal.destination} | "
                    f"${deal.price} | Score: {deal.deal_score:.0f}/100 | "
                    f"{deal.booking_url[:50]}..."
                )
            elif fingerprint in self.known_deals:
                self.logger.debug(f"♻️ Deal conocido (ignorado): {fingerprint}")
            else:
                self.logger.debug(f"📉 Score bajo umbral: {deal.deal_score:.0f} < {ALERT_THRESHOLD}")
        
        return new_deals

    def run_check_cycle(self):
        """Ejecuta un ciclo de verificación completo"""
        self.logger.info("=" * 60)
        self.logger.info(f"🚀 Iniciando ciclo de verificación")
        
        total_new_deals = 0
        
        for route in self.routes:
            deals = self.check_route(route)
            new_deals = self.process_deals(deals)
            
            # Enviar notificaciones solo para nuevas oportunidades
            for deal in new_deals:
                self.send_notification(deal)
                total_new_deals += 1
                time.sleep(2)  # Evitar spam de notificaciones
        
        self.save_state()
        
        self.logger.info(f"✅ Ciclo completado: {total_new_deals} nuevas bandas negras")
        self.logger.info("=" * 60)

    def run_forever(self):
        """Ejecuta el monitor continuamente"""
        self.logger.info("🛫 Flight Monitor Daemon iniciado")
        self.logger.info(f"📍 Monitoreando {len(self.routes)} rutas")
        self.logger.info(f"⏱️ Intervalo: {CHECK_INTERVAL}s ({CHECK_INTERVAL/60:.1f} min)")
        
        while True:
            try:
                self.run_check_cycle()
                self.logger.info(f"💤 Esperando {CHECK_INTERVAL}s hasta próxima verificación...")
                time.sleep(CHECK_INTERVAL)
            
            except KeyboardInterrupt:
                self.logger.info("⛔ Monitor detenido por usuario")
                break
            
            except Exception as e:
                self.logger.error(f"❌ Error en ciclo: {e}")
                time.sleep(60)  # Esperar 1 min antes de reintentar


def main():
    """Punto de entrada del daemon"""
    
    # Configuración de rutas a monitorear
    # Editar según tus rutas de interés
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
        },
        {
            "origin": "EZE", 
            "destination": "BCN",
            "name": "Buenos Aires → Barcelona",
            "days_ahead": 45
        },
        {
            "origin": "COR",
            "destination": "EZE",
            "name": "Córdoba → Buenos Aires",
            "days_ahead": 20
        }
    ]
    
    monitor = FlightMonitor(MONITORED_ROUTES)
    
    # Verificar notify-send
    if not Path("/usr/bin/notify-send").exists():
        print("⚠️ notify-send no encontrado. Instalando...")
        monitor.install_notify()
    
    monitor.run_forever()


if __name__ == "__main__":
    main()
