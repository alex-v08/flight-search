#!/usr/bin/env python3
"""
Flight Search Dashboard - Overlay transparente de escritorio
Muestra bandas negras (error fares) desde Mendoza a cualquier destino
Fondo transparente real, texto blanco, siempre en background
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import random
from datetime import datetime, timedelta
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flight_search import FlightSearchEngine, FlightDeal


class TransparentDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Flight Search Overlay")
        
        # Configurar ventana full transparente
        self.root.geometry("500x700+20+20")  # Esquina superior izquierda
        self.root.overrideredirect(True)  # Sin bordes
        
        # Hacer verdaderamente transparente (sin fondo)
        self.root.attributes('-alpha', 0.95)  # Casi transparente
        self.root.attributes('-topmost', True)  # Siempre encima
        
        # Para Linux/X11 - transparencia real
        try:
            self.root.wait_visibility(self.root)
            self.root.attributes('-transparentcolor', 'gray15')
        except:
            pass
        
        # Variables
        self.drag_data = {"x": 0, "y": 0}
        self.is_searching = False
        self.engine = None
        self.all_deals = []
        self.search_count = 0
        
        # Destinos populares desde MDZ
        self.destinations = [
            "EZE", "AEP", "COR", "BRC", "SLA", "FTE", "USH", 
            "MAD", "BCN", "MIA", "JFK", "GRU", "SCL", "BOG"
        ]
        
        self.setup_ui()
        self.setup_drag()
        
        # Iniciar búsqueda
        self.start_monitoring()
        
    def setup_ui(self):
        """UI minimalista con texto blanco sobre fondo transparente"""
        # Frame principal transparente
        self.main_frame = tk.Frame(
            self.root,
            bg='gray15',  # Color que será transparente
            highlightthickness=0
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para dibujar fondo semi-transparente manual
        self.canvas = tk.Canvas(
            self.main_frame,
            bg='gray15',
            highlightthickness=0,
            width=500,
            height=700
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Fondo oscuro semi-transparente
        self.canvas.create_rectangle(
            0, 0, 500, 700,
            fill='#000000',
            stipple='gray50',  # Patrón de puntos para transparencia
            outline=''
        )
        
        # Header
        self.canvas.create_text(
            250, 20,
            text="✈️ FLIGHT SEARCH AI",
            font=('Arial', 14, 'bold'),
            fill='#ffffff',
            anchor='center'
        )
        
        self.canvas.create_text(
            250, 40,
            text="Bandas Negras desde Mendoza (MDZ)",
            font=('Arial', 9),
            fill='#aaaaaa',
            anchor='center'
        )
        
        # Status
        self.status_text = self.canvas.create_text(
            250, 65,
            text="🔄 Iniciando búsqueda...",
            font=('Arial', 8),
            fill='#4a9eff',
            anchor='center'
        )
        
        # Contador
        self.counter_text = self.canvas.create_text(
            480, 20,
            text="0",
            font=('Arial', 10, 'bold'),
            fill='#ffffff',
            anchor='e'
        )
        
        # Frame scrollable para ofertas
        self.deals_frame = tk.Frame(self.canvas, bg='gray15')
        self.deals_frame.place(x=10, y=90, width=480, height=550)
        
        # Canvas interior para scrolling
        self.deals_canvas = tk.Canvas(
            self.deals_frame,
            bg='gray15',
            highlightthickness=0,
            width=460,
            height=550
        )
        self.deals_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.deals_frame, orient=tk.VERTICAL, command=self.deals_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.deals_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno para las ofertas
        self.deals_inner = tk.Frame(self.deals_canvas, bg='gray15')
        self.deals_canvas.create_window((0, 0), window=self.deals_inner, anchor='nw', width=460)
        
        # Botones de control (abajo)
        control_y = 660
        
        # Botón buscar ahora
        btn_search = tk.Button(
            self.canvas,
            text="🔍",
            command=self.manual_search,
            bg='#333333',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2',
            width=3
        )
        btn_search.place(x=380, y=control_y)
        
        # Botón refrescar
        btn_refresh = tk.Button(
            self.canvas,
            text="🔄",
            command=self.refresh_display,
            bg='#333333',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2',
            width=3
        )
        btn_refresh.place(x=420, y=control_y)
        
        # Botón minimizar
        btn_min = tk.Button(
            self.canvas,
            text="—",
            command=self.minimize,
            bg='#333333',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2',
            width=3
        )
        btn_min.place(x=460, y=control_y)
        
        # Timestamp
        self.time_text = self.canvas.create_text(
            20, control_y + 10,
            text="",
            font=('Arial', 7),
            fill='#666666',
            anchor='w'
        )
        
    def setup_drag(self):
        """Configurar arrastre desde cualquier parte"""
        def start_drag(event):
            self.drag_data["x"] = event.x_root - self.root.winfo_x()
            self.drag_data["y"] = event.y_root - self.root.winfo_y()
            
        def do_drag(event):
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.root.geometry(f"+{x}+{y}")
            
        # Hacer toda la ventana arrastrable
        self.root.bind('<Button-1>', start_drag)
        self.root.bind('<B1-Motion>', do_drag)
        
    def minimize(self):
        """Minimizar a icono pequeño"""
        if self.root.winfo_height() > 100:
            self.root.geometry("500x40")
            self.deals_frame.place_forget()
        else:
            self.root.geometry("500x700")
            self.deals_frame.place(x=10, y=90, width=480, height=550)
            
    def clear_deals(self):
        """Limpiar lista de ofertas"""
        for widget in self.deals_inner.winfo_children():
            widget.destroy()
            
    def create_deal_card(self, deal: FlightDeal, index: int):
        """Crear tarjeta de oferta con texto blanco"""
        # Frame de la oferta
        card = tk.Frame(
            self.deals_inner,
            bg='#1a1a1a',
            highlightbackground='#333333',
            highlightthickness=1
        )
        card.pack(fill=tk.X, pady=3, padx=2)
        
        # Color según score
        if deal.deal_score and deal.deal_score >= 90:
            border_color = '#ff3333'  # Rojo para bandas negras
            bg_color = '#2d1a1a'
        elif deal.deal_score and deal.deal_score >= 70:
            border_color = '#ffaa33'  # Naranja para buenas ofertas
            bg_color = '#2d251a'
        else:
            border_color = '#333333'
            bg_color = '#1a1a1a'
            
        card.configure(bg=bg_color, highlightbackground=border_color, highlightthickness=2)
        
        # Aerolínea y precio (fila superior)
        header = tk.Frame(card, bg=bg_color)
        header.pack(fill=tk.X, padx=8, pady=4)
        
        # Emoji según score
        emoji = "🔥" if deal.deal_score and deal.deal_score >= 90 else "⭐" if deal.deal_score and deal.deal_score >= 70 else "✈️"
        
        airline = tk.Label(
            header,
            text=f"{emoji} {deal.airline or 'Desconocida'}",
            font=('Arial', 9, 'bold'),
            fg='#ffffff',
            bg=bg_color
        )
        airline.pack(side=tk.LEFT)
        
        price_text = f"{deal.currency} {deal.price:,.0f}" if deal.price else "Consultar"
        price_color = '#4aff4a' if deal.deal_score and deal.deal_score >= 90 else '#ffffff'
        
        price = tk.Label(
            header,
            text=price_text,
            font=('Arial', 10, 'bold'),
            fg=price_color,
            bg=bg_color
        )
        price.pack(side=tk.RIGHT)
        
        # Ruta y fecha
        route_frame = tk.Frame(card, bg=bg_color)
        route_frame.pack(fill=tk.X, padx=8, pady=2)
        
        route_text = f"{deal.origin or 'MDZ'} → {deal.destination or '?'}"
        route = tk.Label(
            route_frame,
            text=route_text,
            font=('Arial', 8),
            fg='#aaaaaa',
            bg=bg_color
        )
        route.pack(side=tk.LEFT)
        
        date_text = deal.departure_date or "Fecha flexible"
        date_label = tk.Label(
            route_frame,
            text=f"📅 {date_text}",
            font=('Arial', 7),
            fg='#888888',
            bg=bg_color
        )
        date_label.pack(side=tk.RIGHT)
        
        # Score y reputación
        score_frame = tk.Frame(card, bg=bg_color)
        score_frame.pack(fill=tk.X, padx=8, pady=2)
        
        score_val = deal.deal_score or 0
        score_text = f"Score: {score_val:.0f}/100"
        score_color = '#ff6666' if score_val >= 90 else '#ffaa66' if score_val >= 70 else '#aaaaaa'
        
        score = tk.Label(
            score_frame,
            text=score_text,
            font=('Arial', 7),
            fg=score_color,
            bg=bg_color
        )
        score.pack(side=tk.LEFT)
        
        rep_val = deal.reputation_score or 70
        rep = tk.Label(
            score_frame,
            text=f"Rep: {rep_val:.0f}/100",
            font=('Arial', 7),
            fg='#888888',
            bg=bg_color
        )
        rep.pack(side=tk.RIGHT)
        
        # Click para abrir URL
        if self.engine:
            url = self.engine.generate_booking_url(deal)
            
            def open_url(event, url=url):
                import webbrowser
                webbrowser.open(url)
                
            card.bind('<Button-1>', open_url)
            for child in card.winfo_children():
                child.bind('<Button-1>', open_url)
                for grandchild in child.winfo_children():
                    grandchild.bind('<Button-1>', open_url)
            card.configure(cursor='hand2')
            
    def show_alert(self, deal: FlightDeal):
        """Mostrar notificación de banda negra"""
        try:
            price_text = f"{deal.currency} {deal.price:,.0f}" if deal.price else "Error de precio"
            route_text = f"{deal.origin or 'MDZ'} → {deal.destination or '?'}"
            
            subprocess.run([
                'notify-send',
                '-u', 'critical',
                '-t', '15000',
                '-i', 'airplane-mode',
                f'🔥 BANDA NEGRA: {deal.airline or "Desconocida"}',
                f'{price_text}\n{route_text}\n¡Click en el dashboard para reservar!'
            ])
        except Exception as e:
            print(f"Error mostrando alerta: {e}")
            
    def start_monitoring(self):
        """Iniciar monitoreo continuo"""
        def monitor_loop():
            while True:
                try:
                    if not self.is_searching:
                        self.search_all_destinations()
                    # Esperar 10 minutos entre búsquedas completas
                    time.sleep(600)
                except Exception as e:
                    print(f"Error en monitoreo: {e}")
                    self.update_status(f"❌ Error: {str(e)[:30]}", '#ff6666')
                    time.sleep(60)
                    
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
    def manual_search(self):
        """Búsqueda manual"""
        if not self.is_searching:
            threading.Thread(target=self.search_all_destinations, daemon=True).start()
            
    def update_status(self, text, color='#4a9eff'):
        """Actualizar texto de status"""
        self.root.after(0, lambda: self.canvas.itemconfig(self.status_text, text=text, fill=color))
        
    def search_all_destinations(self):
        """Buscar bandas negras desde MDZ a múltiples destinos"""
        if self.is_searching:
            return
            
        self.is_searching = True
        self.update_status("🔄 Buscando bandas negras desde MDZ...", '#4a9eff')
        
        try:
            if not self.engine:
                self.engine = FlightSearchEngine()
                
            all_new_deals = []
            date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Buscar a 5 destinos aleatorios (para no sobrecargar la API)
            destinations_to_search = random.sample(self.destinations, min(5, len(self.destinations)))
            
            for dest in destinations_to_search:
                self.update_status(f"🔍 Buscando MDZ → {dest}...", '#aaaaaa')
                
                try:
                    deals = self.engine.search_error_fares('MDZ', dest, date)
                    
                    # Filtrar solo bandas negras (score >= 85)
                    error_fares = [d for d in deals if d.deal_score and d.deal_score >= 85]
                    all_new_deals.extend(error_fares)
                    
                    # Pequeña pausa entre búsquedas
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error buscando {dest}: {e}")
                    continue
            
            # Actualizar cache
            if all_new_deals:
                self.all_deals.extend(all_new_deals)
                # Eliminar duplicados
                seen = set()
                unique = []
                for d in self.all_deals:
                    key = f"{d.airline}_{d.destination}_{d.price}"
                    if key not in seen:
                        seen.add(key)
                        unique.append(d)
                self.all_deals = unique
                
                # Ordenar por score
                self.all_deals.sort(key=lambda x: x.deal_score or 0, reverse=True)
                
                # Mantener solo top 20
                self.all_deals = self.all_deals[:20]
                
                # Alertar sobre nuevas bandas negras
                for deal in all_new_deals:
                    if deal.deal_score and deal.deal_score >= 90:
                        self.show_alert(deal)
            
            # Actualizar UI
            self.root.after(0, self.update_display)
            
            self.search_count += 1
            
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)[:30]}", '#ff6666')
        finally:
            self.is_searching = False
            
    def update_display(self):
        """Actualizar display de ofertas"""
        self.clear_deals()
        
        # Actualizar contador
        self.canvas.itemconfig(self.counter_text, text=str(len(self.all_deals)))
        
        if not self.all_deals:
            self.update_status("❌ No se encontraron bandas negras", '#ffaa66')
            
            label = tk.Label(
                self.deals_inner,
                text="No hay bandas negras activas\nBuscando cada 10 minutos...",
                font=('Arial', 10),
                fg='#666666',
                bg='gray15',
                justify='center'
            )
            label.pack(pady=50)
        else:
            bandas_negras = len([d for d in self.all_deals if d.deal_score and d.deal_score >= 90])
            self.update_status(f"✅ {bandas_negras} bandas negras | {len(self.all_deals)} ofertas totales", '#4aff4a')
            
            # Mostrar ofertas
            for i, deal in enumerate(self.all_deals[:15]):  # Top 15
                self.create_deal_card(deal, i)
                
        # Actualizar scrollregion
        self.deals_inner.update_idletasks()
        self.deals_canvas.configure(scrollregion=self.deals_canvas.bbox('all'))
        
        # Timestamp
        now = datetime.now().strftime('%H:%M:%S')
        self.canvas.itemconfig(self.time_text, text=f"Última actualización: {now}")
        
    def refresh_display(self):
        """Refrescar display sin buscar"""
        self.update_display()
        
    def run(self):
        """Iniciar aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    print("🚀 Iniciando Flight Search Overlay...")
    print("💡 Fondo transparente - Texto blanco")
    print("🔍 Buscando bandas negras desde MDZ a cualquier destino")
    print("⏱️  Actualización automática cada 10 minutos")
    print("")
    print("Controles:")
    print("  - Arrastrar desde cualquier parte para mover")
    print("  - Click en oferta para abrir URL")
    print("  - 🔍 Buscar ahora")
    print("  - — Minimizar")
    print("")
    
    dashboard = TransparentDashboard()
    dashboard.run()
