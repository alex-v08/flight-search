import os
import json
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

load_dotenv()

console = Console()


@dataclass
class FlightDeal:
    """Representa una oferta de vuelo encontrada"""

    airline: str
    origin: str
    destination: str
    price: float
    currency: str
    departure_date: str
    return_date: Optional[str]
    connections: int
    booking_url: str
    source: str
    reputation_score: float  # 0-100
    deal_score: float  # Indica si es "banda negativa" (error de precio)
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class BraveSearchClient:
    """Cliente para la API de Brave Search"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}

    def search(self, query: str, count: int = 20) -> List[Dict]:
        """Realiza búsqueda web con Brave"""
        params = {
            "q": query,
            "count": count,
            "search_lang": "es",
            "country": "AR",
            "freshness": "week",
        }

        try:
            response = requests.get(
                self.base_url, headers=self.headers, params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("web", {}).get("results", [])
        except Exception as e:
            console.print(f"[red]Error en búsqueda Brave: {e}[/red]")
            return []


class OllamaAnalyzer:
    """Analiza resultados usando modelos locales de Ollama"""

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"
    ):
        self.base_url = base_url
        self.model = model

    def analyze_flight_data(
        self, search_results: List[Dict], context: str
    ) -> List[FlightDeal]:
        """Analiza resultados de búsqueda y extrae ofertas de vuelo"""

        # Preparar contexto para el modelo
        results_text = "\n\n".join(
            [
                f"Título: {r.get('title', '')}\n"
                f"URL: {r.get('url', '')}\n"
                f"Descripción: {r.get('description', '')}"
                for r in search_results[:10]
            ]
        )

        prompt = f"""
Eres un experto en búsqueda de vuelos baratos y errores de precio ("banda negativa").

REGLAS ESTRICTAS:
1. SOLO extrae información que APAREZCA EXPLÍCITAMENTE en el título o descripción
2. El precio DEBE estar escrito claramente con números (ej: "$500", "USD 400", "€350")
3. La URL (booking_url) DEBE ser EXACTAMENTE la URL que aparece en el resultado de búsqueda
4. NO inventes precios, NO asumas, NO calcules - SOLO copia lo que ves
5. Si no hay precio claro, NO incluyas ese resultado

VALIDACIÓN DE PRECIOS:
- Vuelos internacionales largos (ej: Argentina-Europa): mínimo USD 300
- Si ves un precio < USD 200 para vuelos internacionales, DESCÁRTALO (es error)
- El precio debe estar mencionado en el título o descripción del resultado

CONTEXTO DE BÚSQUEDA:
{context}

RESULTADOS DE BÚSQUEDA (extraídos de Brave Search):
{results_text}

INSTRUCCIONES:
1. Lee cada resultado cuidadosamente
2. Busca precios explícitos en título o descripción
3. Copia la URL EXACTA del resultado
4. Valida que el precio sea realista para la ruta
5. Si tienes dudas, NO incluyas el resultado

Responde en formato JSON con esta estructura EXACTA:
{{
    "deals": [
        {{
            "airline": "Nombre de aerolínea (si está en el título/descripción)",
            "origin": "{context.split()[4] if len(context.split()) > 4 else 'origen'}",
            "destination": "{context.split()[6] if len(context.split()) > 6 else 'destino'}", 
            "price": 0.0,
            "currency": "USD",
            "departure_date": "{context.split()[-1] if 'fecha' in context else 'null'}",
            "return_date": null,
            "connections": 0,
            "booking_url": "COPIA EXACTA de la URL del resultado",
            "source": "Nombre del portal (de la URL)",
            "reputation_score": 70.0,
            "deal_score": 50.0,
            "notes": "Copia exacta de dónde viste el precio"
        }}
    ]
}}

IMPORTANTE: Si no hay precios claros y reales, devuelve lista vacía: {{"deals": []}}
"""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()

            # Extraer JSON de la respuesta
            content = result.get("response", "")
            json_match = re.search(r"\{.*\}", content, re.DOTALL)

            if json_match:
                data = json.loads(json_match.group())
                deals = []
                for deal_data in data.get("deals", []):
                    try:
                        deal_data.setdefault("airline", "Desconocida")
                        deal_data.setdefault("origin", "")
                        deal_data.setdefault("destination", "")
                        deal_data.setdefault("price", 0.0)
                        deal_data.setdefault("currency", "USD")
                        deal_data.setdefault("departure_date", "")
                        deal_data.setdefault("connections", 0)
                        deal_data.setdefault("booking_url", "")
                        deal_data.setdefault("source", "")
                        deal_data.setdefault("reputation_score", 70.0)
                        deal_data.setdefault("deal_score", 50.0)
                        deal_data.setdefault("notes", "")
                        
                        # VALIDACIÓN: Filtrar precios absurdamente bajos
                        price = float(deal_data.get("price", 0))
                        booking_url = deal_data.get("booking_url", "")
                        
                        # Validar precio realista
                        if price < 200 and deal_data.get("currency") == "USD":
                            console.print(f"[yellow]⚠️ Precio sospechoso descartado: {price} USD (demasiado bajo para ruta internacional)[/yellow]")
                            continue
                        
                        # Validar que tenga URL real (no generada)
                        if not booking_url or booking_url.startswith("http") == False:
                            console.print(f"[yellow]⚠️ Deal descartado: sin URL válida[/yellow]")
                            continue
                        
                        # Log para debugging
                        console.print(f"[green]✓ Deal validado: {deal_data.get('airline')} ${price} - {booking_url[:50]}...[/green]")
                        
                        deal = FlightDeal(**deal_data)
                        deals.append(deal)
                    except Exception as e:
                        console.print(f"[yellow]Error parseando oferta: {e}[/yellow]")
                return deals

            return []

        except Exception as e:
            console.print(f"[red]Error en análisis Ollama: {e}[/red]")
            return []

    def evaluate_deal_quality(self, deal: FlightDeal) -> Tuple[float, str]:
        """Evalúa la calidad de una oferta y determina si es error de precio"""

        prompt = f"""
Evalúa esta oferta de vuelo y determina si es un error de precio ("banda negativa"):

AEROLÍNEA: {deal.airline}
ORIGEN: {deal.origin} → DESTINO: {deal.destination}
PRECIO: {deal.currency} {deal.price}
CONEXIONES: {deal.connections}
REPUTACIÓN: {deal.reputation_score}/100

Analiza:
1. Si el precio es anormalmente bajo para esta ruta
2. Si hay señales de error de precio (disponibilidad limitada, restricciones inusuales)
3. Puntaje de oportunidad (0-100)

Responde en formato JSON:
{{
    "is_error_fare": true/false,
    "confidence": 0-100,
    "explanation": "explicación detallada",
    "urgency": "alta/media/baja"
}}
"""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            content = result.get("response", "")

            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                confidence = data.get("confidence", 50)
                explanation = data.get("explanation", "No disponible")
                return confidence, explanation

            return 50, "No se pudo evaluar"

        except Exception as e:
            return 50, f"Error: {e}"


class FlightSearchEngine:
    """Motor principal de búsqueda de vuelos"""

    PORTALS = [
        "Skyscanner",
        "Google Flights",
        "Kayak",
        "Expedia",
        "Momondo",
        "Scott's Cheap Flights",
        "Secret Flying",
        "Vuelos Error",
        "Fly4free",
        " airfarewatchdog",
    ]

    REPUTATION_DB = {
        "Qatar Airways": 95,
        "Singapore Airlines": 94,
        "Emirates": 92,
        "Japan Airlines": 91,
        "Turkish Airlines": 88,
        "Air France": 87,
        "Lufthansa": 87,
        "KLM": 86,
        "Iberia": 84,
        "LATAM": 82,
        "American Airlines": 81,
        "Delta": 83,
        "United": 80,
        "British Airways": 85,
        "Copa Airlines": 79,
        "Avianca": 77,
        "GOL": 75,
        "Aerolíneas Argentinas": 76,
        "JetSMART": 72,
        "Flybondi": 70,
    }

    def __init__(self):
        brave_key = os.getenv("BRAVE_API_KEY")
        if not brave_key:
            raise ValueError("BRAVE_API_KEY no configurada en variables de entorno")

        self.brave = BraveSearchClient(brave_key)
        self.ollama = OllamaAnalyzer(
            os.getenv("OLLAMA_URL", "http://localhost:11434"),
            os.getenv("DEFAULT_MODEL", "llama3.1:8b"),
        )

    def search_error_fares(
        self, origin: str, destination: str, date: str
    ) -> List[FlightDeal]:
        """Busca errores de precio (bandas negativas)"""

        queries = [
            f"error fare {origin} {destination} {date}",
            f"banda negativa vuelo {origin} {destination}",
            f"mistake fare flight {origin} to {destination}",
            f"vuelo barato error precio {origin} {destination}",
            f"oferta vuelo error {origin} {destination} site:secretflying.com",
            f"vuelo {origin} {destination} {date} site:fly4free.com",
        ]

        all_deals = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for query in queries:
                task = progress.add_task(f"Buscando: {query[:50]}...", total=None)

                results = self.brave.search(query, count=15)

                if results:
                    context = f"Buscar errores de precio de {origin} a {destination} para fecha {date}"
                    deals = self.ollama.analyze_flight_data(results, context)

                    for deal in deals:
                        # Verificar reputación
                        deal.reputation_score = self.REPUTATION_DB.get(deal.airline, 70)

                        # Evaluar calidad con Ollama
                        confidence, explanation = self.ollama.evaluate_deal_quality(
                            deal
                        )
                        deal.deal_score = confidence
                        if explanation:
                            deal.notes = explanation

                    all_deals.extend(deals)

                progress.remove_task(task)

        # Eliminar duplicados y ordenar por deal_score
        unique_deals = self._deduplicate_deals(all_deals)
        unique_deals.sort(key=lambda x: x.deal_score, reverse=True)

        return unique_deals

    def search_with_connections(
        self, origin: str, destination: str, date: str, max_connections: int = 2
    ) -> List[FlightDeal]:
        """Busca vuelos con conexiones específicas"""

        queries = [
            f"vuelo {origin} {destination} {date} con escala",
            f"vuelo {origin} {destination} {date} conexión",
            f"flight {origin} to {destination} {date} with connection",
            f"vuelo barato {origin} {destination} varias escalas",
            f"multicity {origin} {destination} {date}",
            f"vuelo indirecto {origin} {destination} oferta",
        ]

        all_deals = []

        for query in queries:
            results = self.brave.search(query, count=10)

            if results:
                context = f"Buscar vuelos con conexiones de {origin} a {destination}"
                deals = self.ollama.analyze_flight_data(results, context)

                # Filtrar por número de conexiones (manejar None)
                deals = [
                    d
                    for d in deals
                    if d.connections is not None and d.connections <= max_connections
                ]

                for deal in deals:
                    deal.reputation_score = self.REPUTATION_DB.get(deal.airline, 70)

                all_deals.extend(deals)

        return self._deduplicate_deals(all_deals)

    def search_cheap_fares(
        self, origin: str, destination: str, date: str
    ) -> List[FlightDeal]:
        """Busca los pasajes más económicos"""

        queries = [
            f"vuelo barato {origin} {destination} {date}",
            f"vuelo más económico {origin} {destination}",
            f"cheap flight {origin} to {destination} {date}",
            f"lowest price flight {origin} {destination}",
            f"vuelo {origin} {destination} site:skyscanner.net",
            f"vuelo {origin} {destination} site:google.com/travel/flights",
        ]

        all_deals = []

        for query in queries:
            results = self.brave.search(query, count=10)

            if results:
                context = f"Buscar vuelos baratos de {origin} a {destination}"
                deals = self.ollama.analyze_flight_data(results, context)

                for deal in deals:
                    deal.reputation_score = self.REPUTATION_DB.get(deal.airline, 70)

                all_deals.extend(deals)

        # Ordenar por precio
        deals = self._deduplicate_deals(all_deals)
        deals.sort(key=lambda x: x.price)

        return deals

    def _deduplicate_deals(self, deals: List[FlightDeal]) -> List[FlightDeal]:
        """Elimina ofertas duplicadas"""
        seen = set()
        unique = []

        for deal in deals:
            key = f"{deal.airline}_{deal.origin}_{deal.destination}_{deal.price}_{deal.departure_date}"
            if key not in seen:
                seen.add(key)
                unique.append(deal)

        return unique

    def generate_booking_url(self, deal: FlightDeal) -> str:
        """Genera URL directa de reserva según la fuente"""
        origin = deal.origin or ""
        destination = deal.destination or ""
        date = deal.departure_date or ""

        # URLs directas por portal
        source_lower = deal.source.lower() if deal.source else ""
        booking_url_lower = deal.booking_url.lower() if deal.booking_url else ""

        if "kayak" in source_lower or "kayak" in booking_url_lower:
            return f"https://www.kayak.com/flights/{origin}-{destination}/{date}"
        elif "skyscanner" in source_lower:
            return f"https://www.skyscanner.com/transport/flights/{origin.lower()}/{destination.lower()}/?adultsv2=1&cabinclass=economy&childrenv2=&ref=home&rtn=0&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&oym={date[:7].replace('-', '')}"
        elif "google" in source_lower or "google flights" in source_lower:
            return f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{date}"
        elif "despegar" in source_lower:
            return f"https://www.despegar.com.ar/vuelos/{origin}/{destination}/"
        elif "expedia" in source_lower:
            return f"https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{origin},to:{destination},departure:{date}TANYT&passengers=adults:1&mode=search"
        elif deal.airline and "jetsmart" in deal.airline.lower():
            return f"https://www.jetsmart.com/ar/es/reservas"
        elif deal.airline and "aerolineas" in deal.airline.lower():
            return f"https://www.aerolineas.com.ar/es-ar"
        elif deal.booking_url and deal.booking_url.startswith("http"):
            return deal.booking_url
        else:
            # Fallback a Google Flights
            return f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{date}"

    def display_results(self, deals: List[FlightDeal], title: str = "Resultados"):
        """Muestra los resultados en formato tabla con links"""

        if not deals:
            console.print(Panel("[yellow]No se encontraron ofertas[/yellow]"))
            return

        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("#", justify="center", width=4)
        table.add_column("Aerolínea", style="cyan", width=18)
        table.add_column("Ruta", width=12)
        table.add_column("Precio", justify="right", width=11)
        table.add_column("Fechas", width=12)
        table.add_column("Rep", justify="center", width=5)
        table.add_column("Score", justify="center", width=6)

        for i, deal in enumerate(deals[:10], 1):  # Mostrar top 10
            route = f"{deal.origin}→{deal.destination}"
            price = (
                f"{deal.currency} {deal.price:,.0f}"
                if deal.price and deal.currency
                else "N/A"
            )
            dates = f"{deal.departure_date}" if deal.departure_date else "N/A"
            if deal.return_date:
                dates += f"\n↳ {deal.return_date}"

            # Color según deal_score
            score_color = (
                "green"
                if deal.deal_score >= 80
                else "yellow"
                if deal.deal_score >= 60
                else "red"
            )

            table.add_row(
                str(i),
                deal.airline or "Desconocida",
                route,
                price,
                dates,
                f"{deal.reputation_score:.0f}" if deal.reputation_score else "N/A",
                f"[{score_color}]{deal.deal_score:.0f}[/{score_color}]",
            )

        console.print(table)
        console.print(f"\n[dim]Total de ofertas encontradas: {len(deals)}[/dim]")

        # Mostrar links directos
        console.print("\n[bold cyan]🔗 LINKS DIRECTOS A LAS OFERTAS:[/bold cyan]")
        for i, deal in enumerate(deals[:5], 1):
            url = self.generate_booking_url(deal)
            console.print(
                f"\n[bold]{i}. {deal.airline} - {deal.currency} {deal.price:,.0f}[/bold]"
            )
            console.print(f"   [blue][link={url}]{url}[/link][/blue]")
            if deal.notes:
                console.print(f"   [dim]{deal.notes[:80]}...[/dim]")

    def save_results_to_markdown(
        self,
        deals: List[FlightDeal],
        origin: str,
        destination: str,
        filename: Optional[str] = None,
    ):
        """Guarda los resultados en un archivo markdown con links"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flight_search_{origin}_{destination}_{timestamp}.md"

        filepath = Path(filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# ✈️ Resultados de Búsqueda: {origin} → {destination}\n\n")
            f.write(
                f"**Fecha de búsqueda:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            f.write(f"**Total de ofertas:** {len(deals)}\n\n")

            if not deals:
                f.write("*No se encontraron ofertas disponibles.*\n")
                return filepath

            # Mejores ofertas
            f.write("## 🏆 Top Ofertas\n\n")

            for i, deal in enumerate(deals[:10], 1):
                url = self.generate_booking_url(deal)

                # Emoji según deal_score
                emoji = (
                    "🔥"
                    if deal.deal_score >= 90
                    else "⭐"
                    if deal.deal_score >= 70
                    else "✈️"
                )

                f.write(f"### {emoji} {i}. {deal.airline}\n\n")
                f.write(
                    f"- **Ruta:** {deal.origin or 'N/A'} → {deal.destination or 'N/A'}\n"
                )
                price_str = (
                    f"{deal.currency} {deal.price:,.2f}"
                    if deal.price and deal.currency
                    else "Consultar"
                )
                f.write(f"- **Precio:** {price_str}\n")
                f.write(f"- **Fecha:** {deal.departure_date or 'Consultar'}\n")
                rep_score = (
                    deal.reputation_score if deal.reputation_score is not None else 70
                )
                f.write(f"- **Reputación:** {rep_score:.0f}/100\n")
                deal_score = deal.deal_score if deal.deal_score is not None else 50
                f.write(f"- **Score de Oferta:** {deal_score:.0f}/100\n")
                f.write(f"- **Conexiones:** {deal.connections or 0}\n")
                f.write(f"- **Fuente:** {deal.source or 'N/A'}\n")
                f.write(f"- **🔗 Link Directo:** [{url}]({url})\n")
                if deal.notes:
                    f.write(f"- **Notas:** {deal.notes}\n")
                f.write("\n---\n\n")

            # Resumen
            f.write("\n## 📊 Resumen\n\n")
            prices = [d.price for d in deals if d.price is not None]
            if prices:
                best_price = min(prices)
                best_deal = next(d for d in deals if d.price == best_price)
                f.write(
                    f"- **Mejor precio:** {best_deal.currency or 'USD'} {best_price:,.2f}\n"
                )
            scores = [d.deal_score for d in deals if d.deal_score is not None]
            if scores:
                f.write(f"- **Mejor score:** {max(scores):.0f}/100\n")
            airlines = set(d.airline for d in deals if d.airline)
            f.write(f"- **Aerolíneas encontradas:** {len(airlines)}\n")

        console.print(f"\n[green]✅ Resultados guardados en: {filepath}[/green]")
        return filepath


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Buscador inteligente de vuelos")
    parser.add_argument(
        "--origin", "-o", required=True, help="Código IATA de origen (ej: EZE)"
    )
    parser.add_argument(
        "--destination", "-d", required=True, help="Código IATA de destino (ej: MAD)"
    )
    parser.add_argument("--date", required=True, help="Fecha de salida (YYYY-MM-DD)")
    parser.add_argument("--return-date", help="Fecha de regreso (YYYY-MM-DD)")
    parser.add_argument(
        "--deep-search",
        action="store_true",
        help="Búsqueda profunda (más lenta pero exhaustiva)",
    )
    parser.add_argument(
        "--max-connections", type=int, default=2, help="Máximo de conexiones permitidas"
    )
    parser.add_argument(
        "--error-fares-only", action="store_true", help="Buscar solo errores de precio"
    )
    parser.add_argument(
        "--model", default="llama3.1:8b", help="Modelo de Ollama a usar"
    )
    parser.add_argument(
        "--save", type=str, help="Guardar resultados en archivo markdown específico"
    )
    parser.add_argument(
        "--no-save", action="store_true", help="No guardar resultados en archivo"
    )

    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold blue]Flight Search AI[/bold blue]\n"
            "Buscador inteligente de pasajes de avión",
            border_style="blue",
        )
    )

    try:
        engine = FlightSearchEngine()
        engine.ollama.model = args.model

        console.print(f"\n[bold]Búsqueda:[/bold] {args.origin} → {args.destination}")
        console.print(f"[bold]Fecha:[/bold] {args.date}")
        if args.return_date:
            console.print(f"[bold]Regreso:[/bold] {args.return_date}")
        console.print(f"[bold]Modelo IA:[/bold] {args.model}\n")

        all_deals = []

        # Buscar errores de precio (bandas negativas)
        console.print(
            "[bold yellow]🔍 Buscando errores de precio (bandas negativas)...[/bold yellow]"
        )
        error_deals = engine.search_error_fares(
            args.origin, args.destination, args.date
        )
        if error_deals:
            engine.display_results(error_deals, "🚨 Posibles Errores de Precio")
            all_deals.extend(error_deals)

        # Buscar vuelos con conexiones
        console.print(
            "\n[bold yellow]🔍 Buscando vuelos con conexiones...[/bold yellow]"
        )
        connection_deals = engine.search_with_connections(
            args.origin, args.destination, args.date, args.max_connections
        )
        if connection_deals:
            engine.display_results(connection_deals, "✈️ Vuelos con Conexiones")
            all_deals.extend(connection_deals)

        # Buscar pasajes económicos
        if not args.error_fares_only:
            console.print(
                "\n[bold yellow]🔍 Buscando los pasajes más económicos...[/bold yellow]"
            )
            cheap_deals = engine.search_cheap_fares(
                args.origin, args.destination, args.date
            )
            if cheap_deals:
                engine.display_results(cheap_deals, "💰 Vuelos más Económicos")
                all_deals.extend(cheap_deals)

        # Resumen final
        if all_deals:
            console.print("\n" + "=" * 80)
            console.print("[bold green]✅ BÚSQUEDA COMPLETADA[/bold green]")

            # Eliminar duplicados para el resumen
            unique_deals = engine._deduplicate_deals(all_deals)
            unique_deals.sort(key=lambda x: x.deal_score, reverse=True)

            console.print(f"Total de ofertas únicas: {len(unique_deals)}")

            # Guardar resultados en markdown (si no se desactivó)
            md_file = None
            if not args.no_save:
                md_file = engine.save_results_to_markdown(
                    unique_deals, args.origin, args.destination, args.save
                )

            # Mejor oferta
            best_deals = unique_deals[:3]
            console.print("\n[bold cyan]🏆 TOP 3 MEJORES OFERTAS:[/bold cyan]")
            for i, deal in enumerate(best_deals, 1):
                url = engine.generate_booking_url(deal)
                console.print(
                    f"{i}. {deal.airline}: {deal.currency} {deal.price:,.0f} "
                    f"(Score: {deal.deal_score:.0f})"
                )
                console.print(f"   [blue]{url}[/blue]")

            if md_file:
                console.print(f"\n[dim]📄 Resultados guardados en: {md_file}[/dim]")
        else:
            console.print("\n[bold red]❌ No se encontraron ofertas[/bold red]")

    except ValueError as e:
        console.print(f"[bold red]Error de configuración: {e}[/bold red]")
        console.print("\n[dim]Crea un archivo .env con:[/dim]")
        console.print("[dim]BRAVE_API_KEY=tu_api_key_de_brave[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


if __name__ == "__main__":
    main()
