#!/usr/bin/env python3
"""
ios_bot.py – Paper Trading Bot iOS Mode (Pythonista 3)
=================================================================

$1M virtual balance • Live market prices • AI Signals (optional)
For educational paper trading simulations only—NO REAL TRADING.
Runs on iPhone/iPad via Pythonista 3.

Author: @MohamedDodda
Last updated: 2025 (aligned with project)
"""

import requests
import time
import csv
import os
import datetime
import json
from threading import Thread
import pandas as pd

# Pythonista UI - mock if not available
try:
    import console  # type: ignore
except ImportError:
    # Mock console for development/testing outside Pythonista
    class MockConsole:
        def alert(self, msg):
            print(f"[ALERT] {msg}")
        def input_alert(self, msg):
            return input(f"{msg}: ")
        def clear(self):
            os.system('clear' if os.name != 'nt' else 'cls')
    console = MockConsole()  # type: ignore

# Imports from project
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SYMBOLS,
    STARTING_CASH,
    USE_AI,
    OPENROUTER_API_KEY,
    CRYPTO_MODE,
    STOCK_MODE,
    LOG_FILE,
    CSV_LOG_FILE,
)
from core import fetch_all_prices, moving_average_crossover

# iOS-specific session
session = requests.Session()
session.headers.update({'User-Agent': 'PaperTradingBot-iOS/3.0'})

# Global state
holdings = {s: 0.0 for s in SYMBOLS}
balance = STARTING_CASH
prices_cache = {}
history = {s: [] for s in SYMBOLS}
running = True

def fetch_prices():
    """Fetch live prices using core data_fetcher."""
    try:
        prices = fetch_all_prices()
        global prices_cache
        prices_cache.update(prices)
        return prices
    except Exception as e:
        print(f"Price fetch error: {e}")
        return prices_cache

def ai_signal(sym, hist):
    """Get AI signal if enabled."""
    if not USE_AI or not OPENROUTER_API_KEY:
        return 'hold', 'AI disabled'
    prompt = f"Suggest buy/sell/hold for {sym}: {hist[-5:]} (paper trading simulation)"
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 30
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        r = session.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=10)
        content = r.json()['choices'][0]['message']['content']
        signal = 'buy' if 'buy' in content.lower() else 'sell' if 'sell' in content.lower() else 'hold'
        return signal, content[:40]
    except Exception as e:
        print(f"AI error: {e}")
        return 'hold', 'API error'

def log_trade(sym, action, price, qty, reason):
    """Log trade to CSV."""
    try:
        os.makedirs(os.path.dirname(CSV_LOG_FILE), exist_ok=True)
        with open(CSV_LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.datetime.now(), sym, action, price, qty, balance, reason])
    except Exception as e:
        print(f"Log error: {e}")

def bot_loop():
    """Main bot loop for iOS."""
    global balance, running
    while running:
        prices = fetch_prices()
        for sym in SYMBOLS:
            price = prices.get(sym)
            if price and price > 0:
                history[sym].append(price)
                if len(history[sym]) > 50:
                    history[sym].pop(0)
                hist = history[sym]
                qty = holdings[sym]
                signal, reason = ai_signal(sym, hist) if USE_AI else ('hold', 'No AI')
                
                # Basic strategy fallback
                if not USE_AI:
                    signals = moving_average_crossover(pd.DataFrame({'Close': hist}))
                    if signals.empty or signals['signal'].iloc[-1] == 1:
                        signal = 'buy'
                    elif qty > 0:
                        signal = 'sell'
                    else:
                        signal = 'hold'
                    reason = 'MA Crossover'
                
                if qty > 0 and signal == 'sell':
                    balance += qty * price
                    log_trade(sym, 'SELL', price, qty, reason)
                    holdings[sym] = 0
                    console.alert(f"SOLD {sym} @ ${price:.2f}")
                elif qty == 0 and signal == 'buy':
                    usd = balance * 0.02  # 2% risk
                    if usd > 10:
                        coins = usd / price
                        holdings[sym] = coins
                        balance -= usd
                        log_trade(sym, 'BUY', price, coins, reason)
                        console.alert(f"BOUGHT {sym} @ ${price:.2f}")
        
        total = balance + sum(holdings[s] * prices.get(s, 0) for s in SYMBOLS)
        console.clear()
        print(f"Balance: ${balance:,.0f} | Total: ${total:,.0f} | Mode: {'Crypto' if CRYPTO_MODE else 'Stock'}")
        time.sleep(15)

# iOS Commands
def start():
    """Start the bot."""
    global running
    running = True
    Thread(target=bot_loop, daemon=True).start()
    console.alert("Bot Started! (Paper Trading Simulation Only)")

def stop():
    """Stop the bot."""
    global running
    running = False
    console.alert("Bot Stopped")

def reset():
    """Reset to initial state."""
    global balance, holdings, history
    balance = STARTING_CASH
    holdings = {s: 0.0 for s in SYMBOLS}
    history = {s: [] for s in SYMBOLS}
    console.alert("Bot Reset")

def status():
    """Show current status."""
    prices = fetch_prices()
    total = balance + sum(holdings[s] * prices.get(s, 0) for s in SYMBOLS)
    console.alert(f"Balance: ${balance:,.0f}\nTotal: ${total:,.0f}")

# Main iOS input loop
console.clear()
console.alert("Paper Trading Bot iOS Mode\nCommands: start, stop, reset, status")
while True:
    cmd = console.input_alert("Enter command").strip().lower()
    if cmd == "start":
        start()
    elif cmd == "stop":
        stop()
    elif cmd == "reset":
        reset()
    elif cmd == "status":
        status()
    elif cmd == "quit":
        break
    else:
        console.alert("Invalid command. Try: start, stop, reset, status")
