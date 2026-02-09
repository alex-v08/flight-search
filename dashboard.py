#!/usr/bin/env python3
"""
Flight Search Dashboard - Widget de escritorio transparente
Muestra ofertas de vuelos en tiempo real con actualizaciones automáticas
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Añadir path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flight_search import FlightSearchEngine, FlightDeal


class FlightDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Flight Search Dashboard")
        self.root.geometry("400x600+50+50")  # Posición arriba a la izquierda

        # Configurar transparencia
        self.root.attributes("-alpha", 0.85)  # 85% opacidad
        self.root.attributes("-topmost", True)  # Siempre encima

        # Permitir movimiento sin bordes
        self.root.overrideredirect(True)  # Sin bordes de ventana

        # Variables de seguimiento
        self.drag_data = {"x": 0, "y": 0}
        self.is_minimized = False
        self.is_searching = False

        # Configuración
        self.routes = [
            {"origin": "MDZ", "destination": "SLA", "name": "Mendoza → Salta"},
            {"origin": "EZE", "destination": "MAD", "name": "Buenos Aires → Madrid"},
            {"origin": "EZE", "destination": "BCN", "name": "Buenos Aires → Barcelona"},
        ]
        self.current_route_index = 0
        self.search_interval = 300  # 5 minutos entre búsquedas
        self.alert_threshold = 90  # Score para alertar

        # Motor de búsqueda
        self.engine = None

        # Resultados
        self.deals_cache = []
        self.last_search = None

        self.setup_ui()
        self.setup_drag()

        # Iniciar búsqueda en background
        self.start_monitoring()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Frame principal con fondo semi-transparente
        self.main_frame = tk.Frame(
            self.root, bg="#1e1e1e", highlightbackground="#333", highlightthickness=1
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Barra de título con controles
        title_frame = tk.Frame(self.main_frame, bg="#2d2d2d")
        title_frame.pack(fill=tk.X, pady=(0, 5))

        # Título
        title_label = tk.Label(
            title_frame,
            text="✈️ Flight Search AI",
            font=("Arial", 10, "bold"),
            fg="#4a9eff",
            bg="#2d2d2d",
        )
        title_label.pack(side=tk.LEFT, padx=10)

        # Botón minimizar
        min_btn = tk.Label(
            title_frame,
            text="—",
            font=("Arial", 10, "bold"),
            fg="#888",
            bg="#2d2d2d",
            cursor="hand2",
        )
        min_btn.pack(side=tk.RIGHT, padx=5)
        min_btn.bind("<Button-1>", lambda e: self.minimize())

        # Botón cerrar
        close_btn = tk.Label(
            title_frame,
            text="×",
            font=("Arial", 12, "bold"),
            fg="#ff6b6b",
            bg="#2d2d2d",
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        close_btn.bind("<Button-1>", lambda e: self.root.quit())

        # Estado
        self.status_label = tk.Label(
            self.main_frame,
            text="🔄 Iniciando...",
            font=("Arial", 8),
            fg="#888",
            bg="#1e1e1e",
        )
        self.status_label.pack(pady=5)

        # Ruta actual
        self.route_label = tk.Label(
            self.main_frame, text="", font=("Arial", 9, "bold"), fg="#fff", bg="#1e1e1e"
        )
        self.route_label.pack(pady=5)

        # Frame para ofertas
        self.deals_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.deals_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Botones de control
        control_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Botón buscar ahora
        search_btn = tk.Button(
            control_frame,
            text="🔍 Buscar",
            command=self.manual_search,
            bg="#4a9eff",
            fg="#fff",
            font=("Arial", 8),
            relief=tk.FLAT,
            cursor="hand2",
        )
        search_btn.pack(side=tk.LEFT, padx=2)

        # Botón siguiente ruta
        next_btn = tk.Button(
            control_frame,
            text="➡️",
            command=self.next_route,
            bg="#333",
            fg="#fff",
            font=("Arial", 8),
            relief=tk.FLAT,
            cursor="hand2",
        )
        next_btn.pack(side=tk.LEFT, padx=2)

        # Botón toggle opacidad
        opacity_btn = tk.Button(
            control_frame,
            text="👁️",
            command=self.toggle_opacity,
            bg="#333",
            fg="#fff",
            font=("Arial", 8),
            relief=tk.FLAT,
            cursor="hand2",
        )
        opacity_btn.pack(side=tk.RIGHT, padx=2)

        # Botón configuración
        config_btn = tk.Button(
            control_frame,
            text="⚙️",
            command=self.show_config,
            bg="#333",
            fg="#fff",
            font=("Arial", 8),
            relief=tk.FLAT,
            cursor="hand2",
        )
        config_btn.pack(side=tk.RIGHT, padx=2)

        # Última actualización
        self.last_update_label = tk.Label(
            self.main_frame, text="", font=("Arial", 7), fg="#666", bg="#1e1e1e"
        )
        self.last_update_label.pack(pady=5)

    def setup_drag(self):
        """Configurar arrastre de la ventana"""

        def start_drag(event):
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

        def do_drag(event):
            x = self.root.winfo_x() + event.x - self.drag_data["x"]
            y = self.root.winfo_y() + event.y - self.drag_data["y"]
            self.root.geometry(f"+{x}+{y}")

        self.main_frame.bind("<Button-1>", start_drag)
        self.main_frame.bind("<B1-Motion>", do_drag)

    def minimize(self):
        """Minimizar a barra de tareas"""
        if not self.is_minimized:
            self.root.geometry("200x30")
            self.is_minimized = True
        else:
            self.root.geometry("400x600")
            self.is_minimized = False

    def toggle_opacity(self):
        """Cambiar opacidad"""
        current = self.root.attributes("-alpha")
        new_opacity = 0.4 if current > 0.5 else 0.85
        self.root.attributes("-alpha", new_opacity)

    def show_config(self):
        """Mostrar ventana de configuración"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuración")
        config_window.geometry("300x200")
        config_window.configure(bg="#1e1e1e")

        tk.Label(
            config_window,
            text="Intervalo de búsqueda (minutos):",
            fg="#fff",
            bg="#1e1e1e",
        ).pack(pady=10)

        interval_var = tk.StringVar(value=str(self.search_interval // 60))
        interval_entry = tk.Entry(config_window, textvariable=interval_var)
        interval_entry.pack()

        tk.Label(
            config_window, text="Score mínimo para alerta:", fg="#fff", bg="#1e1e1e"
        ).pack(pady=10)

        alert_var = tk.StringVar(value=str(self.alert_threshold))
        alert_entry = tk.Entry(config_window, textvariable=alert_var)
        alert_entry.pack()

        def save_config():
            try:
                self.search_interval = int(interval_var.get()) * 60
                self.alert_threshold = int(alert_var.get())
                config_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Valores inválidos")

        tk.Button(
            config_window, text="Guardar", command=save_config, bg="#4a9eff", fg="#fff"
        ).pack(pady=20)

    def next_route(self):
        """Cambiar a la siguiente ruta"""
        self.current_route_index = (self.current_route_index + 1) % len(self.routes)
        self.update_route_display()

    def update_route_display(self):
        """Actualizar display de ruta"""
        route = self.routes[self.current_route_index]
        self.route_label.config(text=f"📍 {route['name']}")

    def clear_deals(self):
        """Limpiar frame de ofertas"""
        for widget in self.deals_frame.winfo_children():
            widget.destroy()

    def display_deal(self, deal: FlightDeal, index: int):
        """Mostrar una oferta en el dashboard"""
        # Frame de la oferta
        deal_frame = tk.Frame(
            self.deals_frame,
            bg="#2d2d2d",
            highlightbackground="#444",
            highlightthickness=1,
        )
        deal_frame.pack(fill=tk.X, pady=2, padx=2)

        # Color según score
        if deal.deal_score >= self.alert_threshold:
            deal_frame.configure(highlightbackground="#ff6b6b", highlightthickness=2)
            bg_color = "#3d2d2d"
        elif deal.deal_score >= 70:
            bg_color = "#2d3d2d"
        else:
            bg_color = "#2d2d2d"

        deal_frame.configure(bg=bg_color)

        # Aerolínea y precio
        header = tk.Frame(deal_frame, bg=bg_color)
        header.pack(fill=tk.X, padx=5, pady=2)

        airline_label = tk.Label(
            header,
            text=f"✈️ {deal.airline or 'Desconocida'}",
            font=("Arial", 8, "bold"),
            fg="#4a9eff",
            bg=bg_color,
        )
        airline_label.pack(side=tk.LEFT)

        price_text = f"{deal.currency} {deal.price:,.0f}" if deal.price else "Consultar"
        price_label = tk.Label(
            header,
            text=price_text,
            font=("Arial", 9, "bold"),
            fg="#4aff4a" if deal.deal_score >= 80 else "#fff",
            bg=bg_color,
        )
        price_label.pack(side=tk.RIGHT)

        # Detalles
        details = tk.Frame(deal_frame, bg=bg_color)
        details.pack(fill=tk.X, padx=5, pady=2)

        date_text = deal.departure_date or "Fecha variable"
        date_label = tk.Label(
            details, text=f"📅 {date_text}", font=("Arial", 7), fg="#aaa", bg=bg_color
        )
        date_label.pack(side=tk.LEFT)

        score_text = (
            f"🔥 Score: {deal.deal_score:.0f}"
            if deal.deal_score >= 90
            else f"⭐ Score: {deal.deal_score:.0f}"
        )
        score_label = tk.Label(
            details,
            text=score_text,
            font=("Arial", 7),
            fg="#ff6b6b" if deal.deal_score >= 90 else "#ffaa4a",
            bg=bg_color,
        )
        score_label.pack(side=tk.RIGHT)

        # Click para abrir URL
        url = self.engine.generate_booking_url(deal) if self.engine else ""
        if url:

            def open_url(event, url=url):
                import webbrowser

                webbrowser.open(url)

            deal_frame.bind("<Button-1>", open_url)
            deal_frame.configure(cursor="hand2")

        # Nota corta
        if deal.notes:
            note = tk.Label(
                deal_frame,
                text=deal.notes[:50] + "..." if len(deal.notes) > 50 else deal.notes,
                font=("Arial", 7),
                fg="#888",
                bg=bg_color,
                wraplength=350,
            )
            note.pack(fill=tk.X, padx=5, pady=2)

    def show_alert(self, deal: FlightDeal):
        """Mostrar alerta de banda negra"""
        try:
            import subprocess

            title = f"🔥 BANDA NEGRA DETECTADA"
            message = f"{deal.airline}: {deal.currency} {deal.price:,.0f}\n{deal.origin} → {deal.destination}"

            # Notificación de escritorio Linux
            subprocess.run(
                ["notify-send", "-u", "critical", "-t", "10000", title, message]
            )
        except:
            pass

    def start_monitoring(self):
        """Iniciar monitoreo en background"""
        self.update_route_display()

        def monitor():
            while True:
                try:
                    if not self.is_searching:
                        self.search_current_route()
                    time.sleep(self.search_interval)
                except Exception as e:
                    print(f"Error en monitoreo: {e}")
                    time.sleep(60)

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def manual_search(self):
        """Búsqueda manual"""
        if not self.is_searching:
            threading.Thread(target=self.search_current_route, daemon=True).start()

    def search_current_route(self):
        """Buscar ofertas para la ruta actual"""
        if self.is_searching:
            return

        self.is_searching = True
        self.status_label.config(text="🔄 Buscando...", fg="#4a9eff")

        try:
            # Inicializar motor si es necesario
            if not self.engine:
                self.engine = FlightSearchEngine()

            route = self.routes[self.current_route_index]

            # Fecha: hoy + 30 días
            date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

            # Buscar
            deals = self.engine.search_error_fares(
                route["origin"], route["destination"], date
            )

            # Actualizar UI en thread principal
            self.root.after(0, lambda: self.update_deals(deals))

        except Exception as e:
            self.root.after(
                0,
                lambda: self.status_label.config(
                    text=f"❌ Error: {str(e)[:30]}", fg="#ff6b6b"
                ),
            )
        finally:
            self.is_searching = False

    def update_deals(self, deals: list):
        """Actualizar display de ofertas"""
        self.clear_deals()
        self.deals_cache = deals

        if not deals:
            self.status_label.config(text="❌ No se encontraron ofertas", fg="#ffaa4a")
            label = tk.Label(
                self.deals_frame,
                text="No hay ofertas disponibles\nIntenta más tarde",
                font=("Arial", 9),
                fg="#888",
                bg="#1e1e1e",
            )
            label.pack(pady=20)
        else:
            # Ordenar por score
            deals.sort(key=lambda x: x.deal_score or 0, reverse=True)

            # Mostrar top 5
            for i, deal in enumerate(deals[:5]):
                self.display_deal(deal, i)

                # Alertar si es banda negra
                if deal.deal_score and deal.deal_score >= self.alert_threshold:
                    self.show_alert(deal)

            self.status_label.config(
                text=f"✅ {len(deals)} ofertas encontradas", fg="#4aff4a"
            )

        # Actualizar timestamp
        self.last_search = datetime.now()
        self.last_update_label.config(
            text=f"🕐 Última actualización: {self.last_search.strftime('%H:%M:%S')}"
        )

    def run(self):
        """Iniciar aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    dashboard = FlightDashboard()
    dashboard.run()
