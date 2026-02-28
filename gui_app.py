#!/usr/bin/env python3
"""
gui_app.py
Paper Trading Bot - Desktop GUI Application
==============================================

A modern desktop GUI for the Paper Trading Bot using CustomTkinter.
Provides a native window experience on PC/Win/Mac with real-time dashboard,
trade logging, and bot controls.

Run: python gui_app.py

Configuration: Edit gui_config.json for easy customization
"""

import customtkinter as ctk
import threading
import queue
import time
import datetime
import sys
import os
import json

# Load GUI configuration
def load_gui_config():
    """Load GUI configuration from gui_config.json"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui_config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load gui_config.json: {e}")
    return {}

GUI_CONFIG = load_gui_config()

# Get config values with defaults
app_config = GUI_CONFIG.get('app', {})
appearance_config = GUI_CONFIG.get('appearance', {})
sidebar_config = GUI_CONFIG.get('sidebar', {})
colors_config = GUI_CONFIG.get('colors', {})

# Set appearance and theme from config
ctk.set_appearance_mode(appearance_config.get('theme', 'dark'))
ctk.set_default_color_theme(appearance_config.get('color_theme', 'blue'))

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import bot components
try:
    from bot import (
        PortfolioManager, DataFetcher, TradingStrategy, Backtester, Visualizer,
        config, portfolio, data_fetcher, strategy, backtester, visualizer,
        bot_step, reset_bot, log_trade, alert, now
    )
    BOT_IMPORTED = True
except ImportError as e:
    BOT_IMPORTED = False
    print(f"Warning: Could not import bot modules: {e}")


class TradingBotGUI(ctk.CTk):
    """Main GUI Application for Paper Trading Bot"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration from config file
        self.title(app_config.get('title', 'Paper Trading Bot'))
        self.geometry(app_config.get('window_size', '1000x700'))
        min_size = app_config.get('min_window_size', '800x600').split('x')
        self.minsize(int(min_size[0]), int(min_size[1]))
        
        # Colors from config
        self.primary_color = colors_config.get('primary', '#2fa572')
        self.secondary_color = colors_config.get('secondary', '#1f6aa5')
        self.danger_color = colors_config.get('danger', '#c53b3b')
        
        # Bot control variables
        self.bot_running = False
        self.bot_thread = None
        self.update_queue = queue.Queue()
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_area()
        
        # Create status bar
        self.create_status_bar()
        
        # Start GUI update loop
        self.after(100, self.process_queue)
        
    def create_sidebar(self):
        """Create the left sidebar with controls"""
        sidebar_width = sidebar_config.get('width', 200)
        self.sidebar_frame = ctk.CTkFrame(self, width=sidebar_width, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
        # Logo/Title from config
        logo_text = sidebar_config.get('logo_text', '📈 Paper Trading\nBot')
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text=logo_text,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Bot Status
        self.status_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Status: Stopped",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=10)
        
        # Control Buttons (using colors from config)
        self.start_button = ctk.CTkButton(
            self.sidebar_frame,
            text="▶ Start Bot",
            command=self.start_bot,
            fg_color=self.primary_color,
            hover_color="#258f5a"
        )
        self.start_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.stop_button = ctk.CTkButton(
            self.sidebar_frame,
            text="⏹ Stop Bot",
            command=self.stop_bot,
            fg_color=self.danger_color,
            hover_color="#a33030",
            state="disabled"
        )
        self.stop_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.reset_button = ctk.CTkButton(
            self.sidebar_frame,
            text="🔄 Reset Bot",
            command=self.reset_bot,
            fg_color=self.secondary_color,
            hover_color="#155a85"
        )
        self.reset_button.grid(row=4, column=0, padx=20, pady=10)
        
        # Separator
        self.separator = ctk.CTkFrame(self.sidebar_frame, height=2)
        self.separator.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        # Quick Stats in Sidebar
        self.balance_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Balance: $0.00",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.balance_label.grid(row=6, column=0, padx=20, pady=5)
        
        self.portfolio_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Portfolio: $0.00",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.portfolio_label.grid(row=7, column=0, padx=20, pady=5)
        
        # Info text
        self.info_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Paper Trading Only\nNo Real Money",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.info_label.grid(row=9, column=0, padx=20, pady=(10, 20))
        
    def create_main_area(self):
        """Create the main content area with tabs"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Dashboard Tab
        self.dashboard_tab = self.tabview.add("📊 Dashboard")
        self.create_dashboard_tab()
        
        # Trade Log Tab
        self.trades_tab = self.tabview.add("📜 Trade Log")
        self.create_trades_tab()
        
        # Holdings Tab
        self.holdings_tab = self.tabview.add("💼 Holdings")
        self.create_holdings_tab()
        
        # Settings Tab
        self.settings_tab = self.tabview.add("⚙️ Settings")
        self.create_settings_tab()
        
    def create_dashboard_tab(self):
        """Create the dashboard tab content"""
        self.dashboard_tab.grid_columnconfigure(0, weight=1)
        self.dashboard_tab.grid_rowconfigure(1, weight=1)
        
        # Stats frame
        self.stats_frame = ctk.CTkFrame(self.dashboard_tab)
        self.stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Create stat labels
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(self.stats_frame, text="Balance", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=5)
        self.dash_balance = ctk.CTkLabel(self.stats_frame, text="$0.00", font=ctk.CTkFont(size=16, weight="bold"))
        self.dash_balance.grid(row=1, column=0, padx=10, pady=5)
        
        ctk.CTkLabel(self.stats_frame, text="Portfolio Value", font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=10, pady=5)
        self.dash_portfolio = ctk.CTkLabel(self.stats_frame, text="$0.00", font=ctk.CTkFont(size=16, weight="bold"))
        self.dash_portfolio.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(self.stats_frame, text="Total P&L", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=10, pady=5)
        self.dash_pnl = ctk.CTkLabel(self.stats_frame, text="$0.00", font=ctk.CTkFont(size=16, weight="bold"))
        self.dash_pnl.grid(row=1, column=2, padx=10, pady=5)
        
        ctk.CTkLabel(self.stats_frame, text="Trades Today", font=ctk.CTkFont(size=12)).grid(row=0, column=3, padx=10, pady=5)
        self.dash_trades = ctk.CTkLabel(self.stats_frame, text="0", font=ctk.CTkFont(size=16, weight="bold"))
        self.dash_trades.grid(row=1, column=3, padx=10, pady=5)
        
        # Activity Log (scrollable)
        self.activity_frame = ctk.CTkFrame(self.dashboard_tab)
        self.activity_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.activity_label = ctk.CTkLabel(self.activity_frame, text="Activity Log", font=ctk.CTkFont(size=14, weight="bold"))
        self.activity_label.pack(pady=(10, 5))
        
        self.activity_textbox = ctk.CTkTextbox(self.activity_frame, wrap="word", height=300)
        self.activity_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.activity_textbox.insert("1.0", "Bot started. Press 'Start Bot' to begin trading simulation.\n")
        
    def create_trades_tab(self):
        """Create the trade log tab"""
        self.trades_tab.grid_columnconfigure(0, weight=1)
        self.trades_tab.grid_rowconfigure(1, weight=1)
        
        # Header
        self.trades_header = ctk.CTkFrame(self.trades_tab)
        self.trades_header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.trades_header, text="Trade History", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        
        self.clear_trades_button = ctk.CTkButton(
            self.trades_header,
            text="Clear",
            command=self.clear_trades,
            width=60
        )
        self.clear_trades_button.pack(side="right", padx=10)
        
        # Trades list (scrollable frame)
        self.trades_scroll = ctk.CTkScrollableFrame(self.trades_tab, label_text="All Trades")
        self.trades_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Trade entries will be added dynamically
        self.trade_entries = []
        
    def create_holdings_tab(self):
        """Create the holdings tab"""
        self.holdings_tab.grid_columnconfigure(0, weight=1)
        self.holdings_tab.grid_rowconfigure(1, weight=1)
        
        # Header
        self.holdings_header = ctk.CTkFrame(self.holdings_tab)
        self.holdings_header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.holdings_header, text="Current Holdings", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        
        # Holdings scroll
        self.holdings_scroll = ctk.CTkScrollableFrame(self.holdings_tab, label_text="Assets")
        self.holdings_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.holding_entries = []
        
    def create_settings_tab(self):
        """Create the settings tab"""
        self.settings_tab.grid_columnconfigure(0, weight=1)
        
        # Settings container
        self.settings_container = ctk.CTkFrame(self.settings_tab)
        self.settings_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.settings_container, text="Bot Settings", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Update interval
        ctk.CTkLabel(self.settings_container, text="Update Interval (seconds):").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.update_interval_slider = ctk.CTkSlider(self.settings_container, from_=5, to=60, number_of_steps=11)
        self.update_interval_slider.set(config['update_interval'])
        self.update_interval_slider.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        # Max risk
        ctk.CTkLabel(self.settings_container, text="Max Risk per Trade (%):").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.risk_slider = ctk.CTkSlider(self.settings_container, from_=1, to=10, number_of_steps=9)
        self.risk_slider.set(config['max_risk_pct'] * 100)
        self.risk_slider.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        # AI Toggle
        self.ai_enabled = ctk.CTkSwitch(self.settings_container, text="AI Trading Enabled")
        self.ai_enabled.grid(row=3, column=0, padx=20, pady=20, sticky="w")
        
    def create_status_bar(self):
        """Create the bottom status bar"""
        self.statusbar = ctk.CTkFrame(self, height=30)
        self.statusbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.status_text = ctk.CTkLabel(
            self.statusbar,
            text="Ready - Paper Trading Bot v3.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.status_text.pack(side="left", padx=10)
        
        self.time_text = ctk.CTkLabel(
            self.statusbar,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.time_text.pack(side="right", padx=10)
        
    def log_activity(self, message: str):
        """Add message to activity log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.activity_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.activity_textbox.see("end")
        
    def start_bot(self):
        """Start the trading bot in a separate thread"""
        if self.bot_running:
            return
            
        self.bot_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="Status: Running", text_color=self.primary_color)
        
        self.log_activity("Bot started!")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
        
    def stop_bot(self):
        """Stop the trading bot"""
        if not self.bot_running:
            return
            
        self.bot_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Status: Stopped", text_color=self.danger_color)
        
        self.log_activity("Bot stopped!")
        
    def reset_bot(self):
        """Reset the bot"""
        reset_bot()
        self.log_activity("Bot reset!")
        self.update_display()
        
    def run_bot(self):
        """Run the bot loop in background thread"""
        if not BOT_IMPORTED:
            self.update_queue.put({"type": "error", "message": "Bot modules not imported"})
            return
            
        last_update = 0
        
        while self.bot_running:
            try:
                if time.time() - last_update >= config['update_interval']:
                    bot_step()
                    last_update = time.time()
                    
                    # Queue update for GUI
                    self.update_queue.put({
                        "type": "update",
                        "balance": portfolio.sim_balance,
                        "portfolio": portfolio.get_total_value(data_fetcher.fetch_all_prices()),
                        "holdings": portfolio.portfolio.copy()
                    })
                    
                time.sleep(0.1)
            except Exception as e:
                self.update_queue.put({"type": "error", "message": str(e)})
                break
                
    def process_queue(self):
        """Process messages from bot thread"""
        try:
            while True:
                msg = self.update_queue.get_nowait()
                
                if msg["type"] == "update":
                    self.update_display()
                elif msg["type"] == "error":
                    self.log_activity(f"ERROR: {msg['message']}")
                    
        except queue.Empty:
            pass
            
        # Update time
        self.time_text.configure(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Schedule next check
        self.after(100, self.process_queue)
        
    def update_display(self):
        """Update all display elements"""
        try:
            prices = data_fetcher.fetch_all_prices()
            balance = portfolio.sim_balance
            portfolio_value = portfolio.get_total_value(prices)
            
            # Update sidebar
            self.balance_label.configure(text=f"Balance: ${balance:,.2f}")
            self.portfolio_label.configure(text=f"Portfolio: ${portfolio_value:,.2f}")
            
            # Update dashboard
            self.dash_balance.configure(text=f"${balance:,.2f}")
            self.dash_portfolio.configure(text=f"${portfolio_value:,.2f}")
            
            pnl = portfolio_value - config['initial_balance']
            pnl_color = self.primary_color if pnl >= 0 else self.danger_color
            self.dash_pnl.configure(text=f"${pnl:,.2f}", text_color=pnl_color)
            
            # Update holdings
            self.update_holdings(prices)
            
        except Exception as e:
            self.log_activity(f"Display update error: {e}")
            
    def update_holdings(self, prices):
        """Update holdings display"""
        # Clear existing
        for widget in self.holdings_scroll.winfo_children():
            widget.destroy()
            
        # Add holdings
        for symbol, qty in portfolio.portfolio.items():
            if qty > 0:
                price = prices.get(symbol, 0)
                value = qty * price
                entry_price = portfolio.entry_prices.get(symbol, price)
                pnl_pct = ((price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
                
                frame = ctk.CTkFrame(self.holdings_scroll)
                frame.pack(fill="x", padx=5, pady=2)
                
                ctk.CTkLabel(frame, text=symbol, width=80, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=f"{qty:.4f}", width=80, anchor="e").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=f"${price:.2f}", width=80, anchor="e").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=f"${value:,.2f}", width=100, anchor="e").pack(side="left", padx=5)
                
                pnl_color = self.primary_color if pnl_pct >= 0 else self.danger_color
                ctk.CTkLabel(frame, text=f"{pnl_pct:+.2f}%", width=60, anchor="e", text_color=pnl_color).pack(side="left", padx=5)
                
    def clear_trades(self):
        """Clear trade history"""
        for widget in self.trades_scroll.winfo_children():
            widget.destroy()
        self.trade_entries = []
        
    def on_closing(self):
        """Handle window closing"""
        if self.bot_running:
            self.stop_bot()
        self.destroy()


def main():
    """Main entry point"""
    app = TradingBotGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
