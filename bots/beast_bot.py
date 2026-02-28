#!/usr/bin/env python3
"""
**The BEAST** - AI-Powered Crypto Strategy Simulator (Desktop-Ready Version)
============================================================

Author: @MohamedDodda  
Version: 1.2.1  
License: MIT / Apache-2.0  
GitHub: https://github.com/mohameddodda/Paper_trading_bot  
Live Demo: https://mohameddodda.github.io/Paper_trading_bot/

**Features:**
- Real-time crypto prices (8 pairs)
- DeepSeek AI signals via OpenRouter
- $1,000,000 virtual balance
- Dynamic volatility risk management
- CSV trade logs, desktop notifications, sound alerts
- Command-line control + live console UI
- Cross-platform (Windows/Linux/Mac)

**Note:**  
- Runs on PC/Desktop environment.  
- Uses `plyer` for notifications, `playsound`/`winsound` for sound alerts.  
- No real trading, purely simulation.  
"""

import requests
import time
import csv
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
except ImportError:
    winsound = None
try:
    from playsound import playsound
except ImportError:
    playsound = None

# --------------------- CONFIG ---------------------
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
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
            "log_file": "~/paper_trading_log.csv",
            "price_cache_ttl": 10,
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
    prices = {}
    for sym in SYMBOLS:
        price = get_crypto_price(sym)
        if price:
            prices[sym] = price
        time.sleep(0.1)  # Rate limit
    return prices

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
    """Calculate price volatility"""
    volatilities = {}
    for sym in SYMBOLS:
        if len(price_history[sym]) >= VOLATILITY_WINDOW:
            hist = price_history[sym][-VOLATILITY_WINDOW:]
            vol = (max(hist) - min(hist)) / max(hist)
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
        
        log_trade(sym, "BUY", price, qty, sim_balance)
        notify(f"BUY {sym}", f"Bought {qty:.4f} {sym} @ ${price:.2f}")
        return True, f"Bought {qty:.4f} {sym}"
    
    elif action == "SELL" and portfolio.get(sym, 0) > 0:
        qty = portfolio[sym]
        sim_balance += qty * price
        log_trade(sym, "SELL", price, qty, sim_balance)
        notify(f"SELL {sym}", f"Sold {qty:.4f} {sym} @ ${price:.2f}")
        
        portfolio[sym] = 0
        entry_prices.pop(sym, None)
        last_buy_time.pop(sym, None)
        return True, f"Sold {qty:.4f} {sym}"
    
    return False, "No action"

# --------------------- LOGGING ---------------------
def log_trade(symbol, action, price, qty, balance):
    """Log trade to CSV"""
    log_file = "paper_trading_log.csv"
    row = [datetime.datetime.now().isoformat(), symbol, action, price, qty, balance]
    
    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "symbol", "action", "price", "qty", "balance"])
        writer.writerow(row)

def notify(title, message):
    """Send notification"""
    try:
        if notification:
            notification.notify(title=title, message=message, timeout=5)
        if winsound:
            winsound.Beep(800, 300)
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
    
    # Get AI signal
    ai_signal = get_ai_signal(prices)
    
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
        
        if action:
            execute_trade(sym, action, current_price)

def main():
    """Main entry point"""
    global running, last_update
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          🤖 THE BEAST - Paper Trading Bot v1.2.1          ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Features:                                               ║
    ║  • 8 Crypto Pairs with Real-time Prices                  ║
    ║  • DeepSeek AI Trading Signals                           ║
    ║  • $1,000,000 Virtual Balance                            ║
    ║  • Dynamic Risk Management                               ║
    ║  • Desktop Notifications & Sound Alerts                 ║
    ║                                                           ║
    ║  Commands: start | stop | reset | exit                   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    notify("The BEAST", "Paper Trading Bot Started!")
    
    # Input thread for commands
    def input_loop():
        while True:
            try:
                cmd = input().strip().lower()
                cmd_queue.put(cmd)
            except:
                break
    
    cmd_queue = queue.Queue()
    threading.Thread(target=input_loop, daemon=True).start()
    
    running = True
    last_update = time.time()
    
    while True:
        try:
            if not cmd_queue.empty():
                cmd = cmd_queue.get_nowait()
                
                if cmd == "start":
                    running = True
                    print("▶ Bot started")
                elif cmd == "stop":
                    running = False
                    print("⏸ Bot paused")
                elif cmd == "reset":
                    global sim_balance, portfolio, entry_prices, last_buy_time
                    sim_balance = INITIAL_BALANCE
                    portfolio = {}
                    entry_prices = {}
                    last_buy_time = {}
                    price_history = {sym: [] for sym in SYMBOLS}
                    print("🔄 Bot reset to $1,000,000")
                    notify("Bot Reset", "Balance restored to $1,000,000")
                elif cmd == "exit":
                    print("👋 Exiting...")
                    running = False
                    sys.exit(0)
                elif cmd == "help":
                    print("Commands: start | stop | reset | exit")
                else:
                    # Force buy/sell commands
                    parts = cmd.split()
                    if len(parts) >= 3 and parts[0] == "force":
                        cmd_type, coin = parts[1], parts[2]
                        coin_full = coin if "_" in coin else f"{coin}_USDT"
                        if coin_full not in SYMBOLS:
                            print(f"Symbol {coin_full} not recognized.")
                        else:
                            price = get_single_price(coin_full)
                            if not price:
                                print("Price fetch failed.")
                            else:
                                sym = coin_full
                                if cmd_type == "buy" and running:
                                    usd = min(sim_balance * 0.03, 1000)
                                    qty = usd / price
                                    portfolio[sym] = qty
                                    sim_balance -= usd
                                    entry_prices[sym] = price
                                    last_buy_time[sym] = time.time()
                                    log_trade(sym, "BUY", price, qty, sim_balance, reason="Forced")
                                    notify(f"Forced BUY {sym}", f"Bought {qty:.4f} {sym} @ ${price:.2f}")
                                elif cmd_type == "sell" and portfolio.get(sym, 0) > 0:
                                    qty = portfolio[sym]
                                    sim_balance += qty * price
                                    log_trade(sym, "SELL", price, qty, sim_balance, reason="Forced")
                                    portfolio[sym] = 0
                                    entry_prices.pop(sym, None)
                                    last_buy_time.pop(sym, None)
                                    notify(f"Forced SELL {sym}", f"Sold {qty:.4f} {sym} @ ${price:.2f}")
                                else:
                                    print("Invalid force command or conditions not met.")
                    else:
                        print("Unknown command. Type 'help' for commands.")
        except queue.Empty:
            pass

        # Update and display
        if running and (time.time() - last_update) >= UPDATE_INTERVAL:
            bot_step()
            display_status()
            last_update = time.time()

        time.sleep(0.5)

if __name__ == "__main__":
    main()
