# Copyright 2026 Mohamed Dodda
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3
"""
gui_bot.py
Paper Trading Bot - Desktop GUI Application
==============================================

A modern desktop GUI for the Paper Trading Bot using CustomTkinter.
Provides a native window experience on PC/Win/Mac with real-time dashboard,
trade logging, and bot controls.

Run: python gui_bot.py

Configuration: Edit ../config/gui_config.json for easy customization
"""

import customtkinter as ctk
import threading
import queue
import time
import datetime
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load GUI configuration
def load_gui_config():
    """Load GUI configuration from gui_config.json"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'gui_config.json')
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

# Import bot components
try:
    from bots.cli_bot import (
        PortfolioManager, DataFetcher, TradingStrategy, Backtester, Visualizer,
        config, portfolio, data_fetcher, strategy, backtester, visualizer,
        bot, log_trade_step, reset_bot, alert, now
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
        self.primary_color = colors_config.get('primary', '#2CC985')
        self.secondary_color = colors_config.get('secondary', '#1F6AA5')
        self.danger_color = colors_config.get('danger', '#C93434')
        self.bg_color = colors_config.get('bg', '#0b0c10')
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main area
        self.create_main_area()
        
        # Bot state
        self.bot_running = False
        self.bot_thread = None
        self.cmd_queue = queue.Queue()
        self.trade_entries = []
        
        # Start input thread
        threading.Thread(target=self.input_thread, daemon=True).start()
        
        # Start bot update loop
        self.update_bot()
    
    def create_sidebar(self):
        """Create sidebar"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo/Title
        logo = ctk.CTkLabel(
            self.sidebar,
            text="🤖 Paper Trading",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        logo.pack(pady=20)
        
        # Bot controls
        self.btn_start = ctk.CTkButton(
            self.sidebar,
            text="▶ Start",
            command=self.start_bot,
            fg_color=self.primary_color
        )
        self.btn_start.pack(pady=10, padx=20, fill="x")
        
        self.btn_stop = ctk.CTkButton(
            self.sidebar,
            text="⏹ Stop",
            command=self.stop_bot,
            fg_color=self.danger_color,
            state="disabled"
        )
        self.btn_stop.pack(pady=10, padx=20, fill="x")
        
        self.btn_reset = ctk.CTkButton(
            self.sidebar,
            text="🔄 Reset",
            command=self.reset_bot,
            fg_color=self.secondary_color
        )
        self.btn_reset.pack(pady=10, padx=20, fill="x")
        
        # Status
        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="Status: Stopped",
            text_color="gray"
        )
        self.status_label.pack(pady=20)
        
        # Symbol selector
        self.symbol_label = ctk.CTkLabel(self.sidebar, text="Trading Symbol:")
        self.symbol_label.pack(pady=(20, 5))
        
        self.symbol_var = ctk.StringVar(value="BTC_USDT")
        self.symbol_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["BTC_USDT", "ETH_USDT", "SOL_USDT", "DOGE_USDT"],
            variable=self.symbol_var
        )
        self.symbol_menu.pack(pady=5, padx=20, fill="x")
        
        # Manual trade buttons
        self.buy_btn = ctk.CTkButton(
            self.sidebar,
            text="💰 Buy",
            command=self.manual_buy,
            fg_color=self.primary_color
        )
        self.buy_btn.pack(pady=10, padx=20, fill="x")
        
        self.sell_btn = ctk.CTkButton(
            self.sidebar,
            text="💸 Sell",
            command=self.manual_sell,
            fg_color=self.danger_color
        )
        self.sell_btn.pack(pady=10, padx=20, fill="x")
    
    def create_main_area(self):
        """Create main content area"""
        self.main_frame = ctk.CTkScrollableFrame(self, label_text="Dashboard")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Stats row
        self.stats_frame = ctk.CTkFrame(self.main_frame)
        self.stats_frame.pack(fill="x", pady=10)
        
        # Balance
        self.dash_balance = ctk.CTkLabel(
            self.stats_frame,
            text="$1,000,000.00",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.dash_balance.pack(side="left", padx=20, pady=20)
        
        # Portfolio value
        self.dash_portfolio = ctk.CTkLabel(
            self.stats_frame,
            text="$0.00",
            font=ctk.CTkFont(size=24)
        )
        self.dash_portfolio.pack(side="left", padx=20, pady=20)
        
        # PnL
        self.dash_pnl = ctk.CTkLabel(
            self.stats_frame,
            text="$0.00",
            font=ctk.CTkFont(size=24),
            text_color=self.primary_color
        )
        self.dash_pnl.pack(side="left", padx=20, pady=20)
        
        # Holdings section
        holdings_label = ctk.CTkLabel(
            self.main_frame,
            text="📦 Holdings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        holdings_label.pack(pady=(10, 5))
        
        self.holdings_scroll = ctk.CTkFrame(self.main_frame)
        self.holdings_scroll.pack(fill="x", pady=5)
        
        # Trade history section
        trades_label = ctk.CTkLabel(
            self.main_frame,
            text="📜 Trade History",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        trades_label.pack(pady=(20, 5))
        
        self.trades_scroll = ctk.CTkFrame(self.main_frame)
        self.trades_scroll.pack(fill="both", expand=True, pady=5)
        
        # Activity log
        log_label = ctk.CTkLabel(
            self.main_frame,
            text="📝 Activity Log",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        log_label.pack(pady=(20, 5))
        
        self.log_text = ctk.CTkTextbox(self.main_frame, height=150)
        self.log_text.pack(fill="x", pady=5)
    
    def log_activity(self, message):
        """Add message to activity log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
    
    def start_bot(self):
        """Start the trading bot"""
        if not self.bot_running:
            self.bot_running = True
            self.cmd_queue.put("start")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.status_label.configure(text="Status: Running", text_color=self.primary_color)
            self.log_activity("Bot started")
    
    def stop_bot(self):
        """Stop the trading bot"""
        if self.bot_running:
            self.bot_running = False
            self.cmd_queue.put("stop")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.status_label.configure(text="Status: Stopped", text_color="gray")
            self.log_activity("Bot stopped")
    
    def reset_bot(self):
        """Reset the bot"""
        self.cmd_queue.put("reset")
        self.log_activity("Bot reset to $1,000,000")
    
    def manual_buy(self):
        """Manual buy action"""
        symbol = self.symbol_var.get()
        self.cmd_queue.put(f"force buy {symbol}")
        self.log_activity(f"Manual BUY order for {symbol}")
    
    def manual_sell(self):
        """Manual sell action"""
        symbol = self.symbol_var.get()
        self.cmd_queue.put(f"force sell {symbol}")
        self.log_activity(f"Manual SELL order for {symbol}")
    
    def input_thread(self):
        """Input processing thread"""
        while True:
            try:
                cmd = input().strip().lower()
                self.cmd_queue.put(cmd)
            except:
                break
    
    def update_bot(self):
        """Update bot and UI"""
        try:
            # Process commands
            while not self.cmd_queue.empty():
                cmd = self.cmd_queue.get_nowait()
                if cmd == "start":
                    self.start_bot()
                elif cmd == "stop":
                    self.stop_bot()
                elif cmd == "reset":
                    self.reset_bot()
            
            # Update display if bot is running
            if self.bot_running:
                # Fetch prices
                try:
                    from bots.cli_bot import fetch_all_prices
                    prices = fetch_all_prices()
                except:
                    prices = {}
                
                # Update stats
                balance = 1000000.0  # Would come from portfolio
                portfolio_value = sum(
                    prices.get(sym, 0) * 0 for sym in ["BTC_USDT", "ETH_USDT"]
                )
                
                self.dash_balance.configure(text=f"${balance:,.2f}")
                self.dash_portfolio.configure(text=f"${portfolio_value:,.2f}")
                
                pnl = portfolio_value - 1000000.0
                pnl_color = self.primary_color if pnl >= 0 else self.danger_color
                self.dash_pnl.configure(text=f"${pnl:,.2f}", text_color=pnl_color)
                
                # Update holdings
                self.update_holdings(prices)
            
        except Exception as e:
            self.log_activity(f"Update error: {e}")
        
        # Schedule next update
        self.after(1000, self.update_bot)
    
    def update_holdings(self, prices):
        """Update holdings display"""
        # Clear existing
        for widget in self.holdings_scroll.winfo_children():
            widget.destroy()
        
        # Add holdings (placeholder - would come from portfolio)
        frame = ctk.CTkFrame(self.holdings_scroll)
        frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(frame, text="Symbol", width=80, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(frame, text="Qty", width=80, anchor="e").pack(side="left", padx=5)
        ctk.CTkLabel(frame, text="Price", width=80, anchor="e").pack(side="left", padx=5)
        ctk.CTkLabel(frame, text="Value", width=100, anchor="e").pack(side="left", padx=5)
        ctk.CTkLabel(frame, text="PnL%", width=60, anchor="e").pack(side="left", padx=5)
    
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
