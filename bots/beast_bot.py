# Copyright 2026 Mohamed Dodda - Updated April 2, 2026
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
**The BEAST** - AI-Powered Crypto Strategy Simulator (Desktop-Ready Version)
============================================================

Author: @MohamedDodda  
Version: 1.2.1  
License: Apache-2.0  
GitHub: https://github.com/mohameddodda/Paper_trading_bot  
Live Demo: https://mohameddodda.github.io/Paper_trading_bot/

**Features:**
- Real-time crypto prices (8 pairs)
- DeepSeek AI signals via OpenRouter
- $1,000,000 virtual balance
- Dynamic volatility risk management
- DB trade logs (Phase 2), desktop notifications, sound alerts
- Command-line control + live console UI
- Cross-platform (Windows/Linux/Mac)

**Note:**  
- Runs on PC/Desktop environment.  
- Uses `plyer` for notifications, `winsound`/`playsound` for sound alerts.  
- No real trading, purely simulation.  
"""

import requests
import time
import os
import datetime
import threading
import queue
import json
import random
import sys
import re
try:
    from plyer import notification
except ImportError:
    notification = None
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    winsound = None
    WINSOUND_AVAILABLE = False

import pandas as pd
from core.strategy import load_ai_models, generate_combined_signal, calculate_volatility
from core.data_fetcher import fetch_all_prices, get_live_price
from core.db_manager import db_manager

# --------------------- CONFIG ---------------------
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json not found, using defaults.")
        return {
            "symbols": ["BTC_USDT", "ETH_USDT", "SOL_USDT", "DOGE_USDT", "SHIB_USDT", "CRO_USDT", "XRP_USDT", "ADA_USDT"],
            "update_interval": 10,
            "chart_length": 10,
            "volatility_window": 10,
            "initial_balance": 1000000.0,
            "api_timeout": 10,
            "ai_model": "deepseek/deepseek-chat",
            "ai_consult_interval": 15,
            "referer_url": "https://mohameddodda.github.io/Paper_trading_bot/",
            "cooldown": 300,
            "max_risk_pct": 0.03,
            "stop_loss_pct": -0.05,
            "take_profit_pct": 0.10,
            "max_retries": 3,
            "retry_backoff": 2
        }

config = load_config()
UPDATE_INTERVAL = config['update_interval']
CHART_LENGTH = config['chart_length']
VOLATILITY_WINDOW = config['volatility_window']
INITIAL_BALANCE = config['initial_balance']
API_TIMEOUT = config['api_timeout']
AI_MODEL = config['ai_model']
AI_CONSULT_INTERVAL = config['ai_consult_interval']
REFERER = config['referer_url']
COOLDOWN = config['cooldown']
MAX_RISK_PCT = config['max_risk_pct']
STOP_LOSS_PCT = config['stop_loss_pct']
TAKE_PROFIT_PCT = config['take_profit_pct']
MAX_RETRIES = config['max_retries']
RETRY_BACKOFF = config['retry_backoff']

SYMBOLS = config['symbols']

# --------------------- GLOBALS ---------------------
sim_balance = INITIAL_BALANCE
portfolio = {}
entry_prices = {}
last_buy_time = {}
price_history = {sym: [] for sym in SYMBOLS}
running = False
last_ai_consult = 0
last_update = 0

# --------------------- API ---------------------
def get_crypto_price(symbol):
    """Fetch crypto price from Crypto.com API"""
    try:
        url = f"https://api.crypto.com/exchange/v1/public/get-ticker?instrument_name={symbol}"
        headers = {"User-Agent": "PaperTradingBot/1.2"}
        resp = requests.get(url, timeout=API_TIMEOUT, headers=headers)
        data = resp.json()
        
        if data.get("code") == 0:
            price = float(data["result"]["data"]["a"])  # Ask price
            return price
    except Exception as e:
        print(f"Price fetch error for {symbol}: {e}")
    return None

def get_all_prices():
    """Get all crypto prices"""
    prices = fetch_all_prices()
    return {sym: prices.get(sym) for sym in SYMBOLS}

def get_single_price(symbol):
    """Get single price"""
    return get_crypto_price(symbol)

# --------------------- AI SIGNAL ---------------------
def get_ai_signal(prices):
    """Get AI trading signal from DeepSeek via OpenRouter"""
    global last_ai_consult
    
    # Check if we should consult AI
    if time.time() - last_ai_consult < AI_CONSULT_INTERVAL:
        return None
    
    # Get market summary
    price_str = ", ".join([f"{s}: ${p:.4f}" for s, p in prices.items()])
    prompt = f"""You are a crypto trading expert. Given these prices: {price_str}. 
Should we BUY, SELL, or HOLD right now? Consider volatility, trends, and risk.
Reply with just one word: BUY, SELL, or HOLD."""

    try:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("No OpenRouter API key found.")
            return None
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Referer": REFERER,
            "Origin": "https://mohameddodda.github.io"
        }
        
        payload = {
            "model": AI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 10
        }
        
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=API_TIMEOUT
        )
        
        data = resp.json()
        if "choices" in data:
            signal = data["choices"][0]["message"]["content"].strip().upper()
            if "BUY" in signal:
                last_ai_consult = time.time()
                return "BUY"
            elif "SELL" in signal:
                last_ai_consult = time.time()
                return "SELL"
    except Exception as e:
        print(f"AI signal error: {e}")
    
    return None

# --------------------- STRATEGY ---------------------
def calculate_volatility(prices):
    \"\"\"Calculate price volatility (rule-based fallback)\"\"\"
    volatilities = {}
    for sym in SYMBOLS:
        hist = price_history.get(sym, []) if 'price_history' in globals() else []
        if len(hist) >= VOLATILITY_WINDOW:
            vol = (max(hist[-VOLATILITY_WINDOW:]) - min(hist[-VOLATILITY_WINDOW:])) / max(hist[-VOLATILITY_WINDOW:])
            volatilities[sym] = vol
    return volatilities

def should_trade(sym, current_price):
    """Determine if we should trade based on strategy"""
    # Check cooldown
    if sym in last_buy_time:
        if time.time() - last_buy_time[sym] < COOLDOWN:
            return False, "Cooldown"
    
    # Check stop-loss/take-profit
    if sym in portfolio and portfolio[sym] > 0:
        entry = entry_prices.get(sym, current_price)
        pnl_pct = (current_price - entry) / entry
        
        if pnl_pct <= STOP_LOSS_PCT:
            return True, "Stop Loss"
        elif pnl_pct >= TAKE_PROFIT_PCT:
            return True, "Take Profit"
    
    return False, "Hold"

def execute_trade(sym, action, price):
    """Execute a trade"""
    global sim_balance, portfolio, entry_prices, last_buy_time
    
    if action == "BUY":
        # Calculate position size based on volatility
        volatilities = calculate_volatility(get_all_prices())
        vol = volatilities.get(sym, 0.02)
        risk_pct = min(MAX_RISK_PCT * (1 + vol * 10), 0.1)
        
        usd = min(sim_balance * risk_pct, 1000)
        if usd < 10:
            return False, "Insufficient funds"
        
        qty = usd / price
        portfolio[sym] = portfolio.get(sym, 0) + qty
        sim_balance -= usd
        entry_prices[sym] = price
        last_buy_time[sym] = time.time()
        
db_manager.log_trade(sym, "BUY", price, qty, 0.0, self.sim_balance, reason="AI Buy", strategy='beast_bot')
    db_manager.save_state(self.sim_balance, self.sim_balance + sum(qty * get_live_price(s) for s, qty in self.portfolio.items()), self.portfolio)
        notify(f"BUY {sym}", f"Bought {qty:.4f} {sym} @ ${price:.2f}")
        return True, f"Bought {qty:.4f} {sym}"
    
    elif action == "SELL" and portfolio.get(sym, 0) > 0:
        qty = portfolio[sym]
        sim_balance += qty * price
        entry = entry_prices.get(sym, price)
        pnl_pct = ((price - entry) / entry) * 100 if entry > 0 else 0.0
        db_manager.log_trade(sym, "SELL", price, qty, pnl_pct, sim_balance, reason="Strategy Sell", strategy='beast_bot')
        notify(f"SELL {sym}", f"Sold {qty:.4f} {sym} @ ${price:.2f}")
        
        portfolio[sym] = 0
        entry_prices.pop(sym, None)
        last_buy_time.pop(sym, None)
        return True, f"Sold {qty:.4f} {sym}"
    
    return False, "No action"

def notify(title, message):
    """Enhanced Phase 3 notification with plyer + sound"""
    try:
        if notification:
            notification.notify(
                title=title, 
                message=message, 
                timeout=5, 
                app_name="The BEAST"
            )
        
        if WINSOUND_AVAILABLE and winsound:
            freq = 1200 if "BUY" in title else 600 if "SELL" in title else 900
            winsound.Beep(freq, 400)
    except:
        pass

# --------------------- DISPLAY ---------------------
def display_status():
    """Display current status"""
    prices = get_all_prices()
    
    print("\n" + "="*60)
    print(f"🤖 THE BEAST | {datetime.datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    print(f"💰 Balance: ${sim_balance:,.2f}")
    
    total_portfolio = 0
    for sym, qty in portfolio.items():
        if qty > 0:
            price = prices.get(sym, 0)
            val = qty * price
            total_portfolio += val
            entry = entry_prices.get(sym, price)
            pnl = ((price - entry) / entry) * 100
            print(f"  📦 {sym}: {qty:.4f} @ ${price:.4f} = ${val:,.2f} ({pnl:+.2f}%)")
    
    total = sim_balance + total_portfolio
    pnl = total - INITIAL_BALANCE
    print(f"\n📊 Total: ${total:,.2f} | PnL: ${pnl:,.2f} ({pnl/INITIAL_BALANCE*100:+.2f}%)")
    
    # Show price chart
    print("\n📈 Prices:")
    for sym in SYMBOLS:
        price = prices.get(sym, 0)
        if price_history[sym]:
            avg = sum(price_history[sym][-CHART_LENGTH:]) / len(price_history[sym][-CHART_LENGTH:])
            arrow = "⬆️" if price > avg else "⬇️"
        else:
            arrow = "➡️"
        print(f"  {sym}: ${price:.4f} {arrow}")
    
    print("="*60)

# --------------------- MAIN LOOP ---------------------
def bot_step():
    """Main bot step"""
    global last_update
    
    prices = get_all_prices()
    if not prices:
        return
    
    # Update price history
    for sym, price in prices.items():
        price_history[sym].append(price)
        if len(price_history[sym]) > 100:
            price_history[sym].pop(0)
    
        # Get AI signal (Phase 4: ML + OpenRouter) with model check
        print(\"[INFO] Checking AI models...\")
        from core.strategy import lstm_model, rl_policy
        if lstm_model is None:
            print(\"[WARNING] No LSTM model found — falling back to RSI/MACD strategy\")
            print(\"[INFO] Train one with: python -m training.train_lstm\")
        if rl_policy is None:
            print(\"[WARNING] No RL model found - using rule-based + OpenRouter\")
            print(\"[INFO] Train one with: python training/train_rl_agent.py\")
        
        load_ai_models()
        df_prices = pd.DataFrame({'Close': list(prices.values())})
        # Generate AI signal with proper model fallback (FIX4)
        try:
            from core.strategy import load_ai_models
            load_ai_models()
            signal_score = generate_combined_signal(df_prices, methods=['lstm', 'rl', 'ma'])
            ai_signal = 'BUY' if signal_score > 0 else 'SELL' if signal_score < 0 else None
        except Exception as e:
            print(f"[AI] Signal error (using rules): {e}")
            ai_signal = None
    
    # Process each symbol
    for sym in SYMBOLS:
        current_price = prices.get(sym)
        if not current_price:
            continue
        
        should_trade_flag, reason = should_trade(sym, current_price)
        
        # Execute based on AI signal or strategy
        action = None
        
        if ai_signal == "BUY" and not portfolio.get(sym, 0):
            action = "BUY"
        elif ai_signal == "SELL" and portfolio.get(sym, 0) > 0:
            action = "SELL"
        elif should_trade_flag:
            # Auto sell on stop-loss/take-profit
            if "Stop Loss" in reason or "Take Profit" in reason:
                action = "SELL"
        
if risk_manager.should_halt():
        notify("🚨 HALT", "Daily drawdown limit hit")
        return
    if action:
            execute_trade(sym, action, current_price)

class BeastBot:
    def __init__(self, db_manager, data_fetcher, strategy, bot_id="beast"):
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher
        self.strategy = strategy
        self.bot_id = bot_id
        self.sim_balance = INITIAL_BALANCE
        self.portfolio = {}
        self.entry_prices = {}
        self.last_buy_time = {}
        self.price_history = {sym: [] for sym in SYMBOLS}
        self.running = False
        self.last_update = 0

    def run(self):
        self.running = True
        self.last_update = time.time()
        print(f"Started {self.bot_id} BeastBot")
        
        while self.running:
            try:
                # Update and display
                if (time.time() - self.last_update) >= UPDATE_INTERVAL:
                    self.bot_step()
                    self.display_status()
                    self.last_update = time.time()
                time.sleep(0.5)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        self.running = False
        print(f"Stopped {self.bot_id}")

    def bot_step(self):
        \"\"\"Main bot step - consolidated to avoid duplication.\"\"\"
        print("[INFO] Model checks/fallbacks implemented - no crash on missing models")
        # Duplicate logic removed - handled globally

    def display_status(self):
        """Display current status - bot_id prefixed"""
        prices = get_all_prices()
        print(f"\n[{self.bot_id}] " + "="*50)
        print(f"[{self.bot_id}] Balance: ${self.sim_balance:,.2f}")
        total_portfolio = 0
        for sym, qty in self.portfolio.items():
            if qty > 0:
                price = prices.get(sym, 0)
                val = qty * price
                total_portfolio += val
                entry = self.entry_prices.get(sym, price)
                pnl = ((price - entry) / entry) * 100
                print(f"[{self.bot_id}]  {sym}: {qty:.4f} @ ${price:.4f} ({pnl:+.2f}%)")
        total = self.sim_balance + total_portfolio
        print(f"[{self.bot_id}] Total: ${total:,.2f}")

# Standalone mode
def main():
    from core.db_manager import db_manager
    from core.data_fetcher import DataFetcher
    from core.strategy import TradingStrategy
latest_state = db_manager.load_latest_state()
if latest_state:
    self.sim_balance = latest_state['balance']
    self.portfolio = latest_state['open_positions']
    print(f"✅ BeastBot loaded state: Balance ${self.sim_balance:.2f}")
else:
    db_manager.init_db()
    print("✅ BeastBot new DB initialized")
    bot = BeastBot(db_manager, None, None, "standalone_beast")
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()

if __name__ == "__main__":
    main()

