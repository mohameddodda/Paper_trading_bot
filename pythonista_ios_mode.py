#!/usr/bin/env python3
"""
Paper Trading Bot – Pro iOS Mode (Pythonista 3)
$1M virtual balance • Live Crypto.com • AI Signals
MIT Licensed – Simulation Only
"""

import requests
import time
import csv
import os
import datetime
import json
import console  # Pythonista UI
from threading import Thread

# Config (iOS-friendly)
SYMBOLS = ['BTC_USDT', 'ETH_USDT', 'SOL_USDT', 'DOGE_USDT', 'SHIB_USDT', 'CRO_USDT']
BALANCE = 1000000.0
API_KEY = 'sk-or-v1-your-key-here'  # Paste in config.py

session = requests.Session()
session.headers.update({'User-Agent': 'PaperTradingBot-iOS/3.0'})

holdings = {s: 0 for s in SYMBOLS}
prices_cache = {}
history = {s: [] for s in SYMBOLS}

def fetch_prices():
    try:
        r = session.get("https://api.crypto.com/exchange/v1/public/get-tickers", timeout=10)
        data = r.json().get("result", {}).get("data", [])
        return {item['i']: float(item['a']) for item in data if item['i'] in SYMBOLS}
    except:
        return prices_cache

def ai_signal(sym, hist):
    if not API_KEY or API_KEY == 'sk-or-v1-your-key-here':
        return 'hold', 'Set API key'
    prompt = f"Suggest buy/sell/hold for {sym}: {hist[-5:]}"
    payload = {"model": "mistralai/mistral-7b-instruct:free", "messages": [{"role": "user", "content": prompt}], "max_tokens": 30}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        r = session.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        content = r.json()['choices'][0]['message']['content']
        return 'buy' if 'buy' in content.lower() else 'sell' if 'sell' in content.lower() else 'hold', content[:40]
    except:
        return 'hold', 'API error'

def log_trade(sym, action, price, qty, reason):
    path = os.path.join('trades.csv')
    with open(path, 'a') as f:
        f.write(f"{datetime.datetime.now()},{sym},{action},{price},{qty},{reason}\n")

def bot_loop():
    global balance
    balance = BALANCE
    while True:
        prices = fetch_prices()
        for sym in SYMBOLS:
            price = prices.get(sym)
            if price:
                history[sym].append(price)
                if len(history[sym]) > 50:
                    history[sym].pop(0)
                hist = history[sym]
                qty = holdings[sym]
                signal, reason = ai_signal(sym, hist)
                if qty > 0 and signal == 'sell':
                    balance += qty * price
                    log_trade(sym, 'SELL', price, qty, reason)
                    holdings[sym] = 0
                    console.alert(f"SOLD {sym} @ ${price}")
                elif qty == 0 and signal == 'buy':
                    usd = balance * 0.02  # 2% risk
                    coins = usd / price
                    holdings[sym] = coins
                    balance -= usd
                    log_trade(sym, 'BUY', price, coins, reason)
                    console.alert(f"BOUGHT {sym} @ ${price}")
        total = balance + sum(holdings[s] * prices.get(s, 0) for s in SYMBOLS)
        console.clear()
        print(f"Balance: ${balance:.0f} | Total: ${total:.0f}")
        time.sleep(15)

# iOS Commands
def start():
    Thread(target=bot_loop).start()
    console.alert("Bot Started!")

def stop():
    global running
    running = False

running = True
console.input_alert("Commands: start, stop, reset")