#!/usr/bin/env python3
"""
Price History Tracker - Monitoreo de precios históricos por ruta
Almacena el precio más bajo encontrado por ruta para comparación
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

HISTORY_FILE = Path.home() / ".config" / "flight-monitor" / "price_history.json"

@dataclass
class PriceRecord:
    """Registro de precio histórico"""
    route: str  # "EZE-MAD"
    min_price: float
    currency: str
    found_date: str
    last_checked: str
    source: str
    samples: int  # Número de veces que se ha visto

class PriceHistoryTracker:
    """Rastrea precios históricos para determinar ofertas reales"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.history: Dict[str, PriceRecord] = {}
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.load_history()
    
    def load_history(self):
        """Carga historial de precios"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                    for route, record_data in data.items():
                        self.history[route] = PriceRecord(**record_data)
                self.logger.info(f"📊 Historial cargado: {len(self.history)} rutas")
            except Exception as e:
                self.logger.error(f"Error cargando historial: {e}")
    
    def save_history(self):
        """Guarda historial de precios"""
        try:
            data = {
                route: asdict(record) 
                for route, record in self.history.items()
            }
            with open(HISTORY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando historial: {e}")
    
    def route_key(self, origin: str, destination: str) -> str:
        """Genera clave única para ruta"""
        return f"{origin}-{destination}"
    
    def update_price(self, origin: str, destination: str, price: float, 
                    currency: str, source: str) -> bool:
        """
        Actualiza precio histórico si es más bajo
        Retorna True si es un nuevo mínimo
        """
        route = self.route_key(origin, destination)
        today = datetime.now().strftime("%Y-%m-%d")
        
        if route not in self.history:
            # Primer registro para esta ruta
            self.history[route] = PriceRecord(
                route=route,
                min_price=price,
                currency=currency,
                found_date=today,
                last_checked=today,
                source=source,
                samples=1
            )
            self.save_history()
            self.logger.info(f"📝 Nueva ruta registrada: {route} @ {currency} {price}")
            return True
        
        record = self.history[route]
        record.last_checked = today
        record.samples += 1
        
        # Nuevo mínimo encontrado
        if price < record.min_price:
            old_price = record.min_price
            record.min_price = price
            record.currency = currency
            record.found_date = today
            record.source = source
            self.save_history()
            
            discount = ((old_price - price) / old_price) * 100
            self.logger.info(f"🔥 NUEVO MÍNIMO: {route} @ {currency} {price} (antes {old_price}, -{discount:.1f}%)")
            return True
        
        self.save_history()
        return False
    
    def get_min_price(self, origin: str, destination: str) -> Optional[PriceRecord]:
        """Obtiene precio mínimo histórico para ruta"""
        route = self.route_key(origin, destination)
        return self.history.get(route)
    
    def calculate_deal_quality(self, origin: str, destination: str, 
                              current_price: float) -> Tuple[float, str]:
        """
        Calcula calidad de la oferta comparando con histórico
        
        Retorna:
            - deal_score: 0-100 (100 = mejor precio histórico)
            - explanation: descripción del análisis
        """
        record = self.get_min_price(origin, destination)
        
        if not record:
            # Sin historial, usar heurística básica
            return self._heuristic_score(origin, destination, current_price)
        
        # Comparar con precio mínimo histórico
        min_price = record.min_price
        
        if current_price <= min_price:
            # Igual o mejor que el mínimo histórico!
            score = 100
            explanation = (
                f"¡INCREÍBLE! Precio igual/mejor que mínimo histórico "
                f"({record.currency} {min_price:.0f} el {record.found_date}). "
                f"Encontrado {record.samples} veces en historial."
            )
        else:
            # Calcular qué tan cerca está del mínimo
            diff_percent = ((current_price - min_price) / min_price) * 100
            
            if diff_percent <= 5:
                score = 95
                explanation = (
                    f"Excelente! Solo {diff_percent:.1f}% sobre el mínimo histórico "
                    f"({record.currency} {min_price:.0f}). Comprar YA."
                )
            elif diff_percent <= 10:
                score = 90
                explanation = (
                    f"Muy bueno! {diff_percent:.1f}% sobre el mínimo histórico "
                    f"({record.currency} {min_price:.0f}). Muy recomendado."
                )
            elif diff_percent <= 20:
                score = 80
                explanation = (
                    f"Buen precio. {diff_percent:.1f}% sobre el mínimo histórico "
                    f"({record.currency} {min_price:.0f}). Considerar."
                )
            elif diff_percent <= 30:
                score = 70
                explanation = (
                    f"Precio aceptable. {diff_percent:.1f}% sobre el mínimo histórico "
                    f"({record.currency} {min_price:.0f}). Normal."
                )
            else:
                score = 50
                explanation = (
                    f"Precio alto. {diff_percent:.1f}% sobre el mínimo histórico "
                    f"({record.currency} {min_price:.0f}). Esperar mejor oferta."
                )
        
        return score, explanation
    
    def _heuristic_score(self, origin: str, destination: str, 
                        price: float) -> Tuple[float, str]:
        """
        Score heurístico cuando no hay historial
        Basado en distancia y precios típicos
        """
        # Rutas internacionales Argentina-Europa
        international_routes = {
            ('EZE', 'MAD'): 450,  # Precio típico "bueno"
            ('EZE', 'BCN'): 500,
            ('EZE', 'FCO'): 480,
            ('EZE', 'CDG'): 520,
            ('EZE', 'LHR'): 550,
        }
        
        # Rutas domésticas Argentina
        domestic_routes = {
            ('MDZ', 'SLA'): 80,
            ('EZE', 'COR'): 60,
            ('EZE', 'MDZ'): 70,
            ('COR', 'SLA'): 90,
        }
        
        route = (origin, destination)
        route_rev = (destination, origin)
        
        reference_price = None
        if route in international_routes:
            reference_price = international_routes[route]
        elif route_rev in international_routes:
            reference_price = international_routes[route_rev]
        elif route in domestic_routes:
            reference_price = domestic_routes[route]
        elif route_rev in domestic_routes:
            reference_price = domestic_routes[route_rev]
        
        if not reference_price:
            # Sin referencia, score neutro
            return 50, "Sin datos históricos ni referencia. Verificar manualmente."
        
        # Comparar con precio de referencia
        diff_percent = ((price - reference_price) / reference_price) * 100
        
        if diff_percent <= -30:
            score = 100
            explanation = f"¡BANDA NEGRA! {abs(diff_percent):.0f}% bajo precio típico (USD {reference_price})"
        elif diff_percent <= -20:
            score = 95
            explanation = f"Excelente oferta! {abs(diff_percent):.0f}% bajo precio típico (USD {reference_price})"
        elif diff_percent <= -10:
            score = 90
            explanation = f"Muy buen precio! {abs(diff_percent):.0f}% bajo precio típico (USD {reference_price})"
        elif diff_percent <= 0:
            score = 80
            explanation = f"Buen precio, {abs(diff_percent):.0f}% bajo precio típico (USD {reference_price})"
        elif diff_percent <= 10:
            score = 70
            explanation = f"Precio normal, {diff_percent:.0f}% sobre típico (USD {reference_price})"
        else:
            score = 50
            explanation = f"Precio alto, {diff_percent:.0f}% sobre típico (USD {reference_price})"
        
        return score, explanation
    
    def get_stats(self) -> str:
        """Retorna estadísticas del historial"""
        if not self.history:
            return "📊 Sin datos históricos aún"
        
        lines = [f"📊 Historial de Precios ({len(self.history)} rutas):"]
        lines.append("")
        
        # Ordenar por precio (más baratos primero)
        sorted_routes = sorted(
            self.history.items(),
            key=lambda x: x[1].min_price
        )
        
        for route, record in sorted_routes:
            days_ago = (datetime.now() - datetime.fromisoformat(record.found_date)).days
            lines.append(
                f"  {record.route}: {record.currency} {record.min_price:.0f} "
                f"(hace {days_ago}d, {record.samples} muestras)"
            )
        
        return "\n".join(lines)


# Función de utilidad para CLI
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    tracker = PriceHistoryTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        print(tracker.get_stats())
    else:
        print("Uso: python3 price_history.py stats")
