#!/usr/bin/env python3
"""
Paper Trading Bot – AI-Powered Crypto Strategy Simulator
============================================================

Author: @MohamedDodda
Version: 1.2.1
License: MIT
GitHub: https://github.com/mohameddodda/Paper_trading_bot
Live Pages: https://mohameddodda.github.io/Paper_trading_bot/

Features:
- Real-time Crypto.com prices (BTC, ETH, SOL, DOGE, SHIB, CRO, XRP, ADA)
- DeepSeek AI signals via OpenRouter (free tier)
- $1M virtual balance – zero risk
- Dynamic volatility-based risk management
- CSV trade log + push notifications + voice alerts
- Console UI with sparkline charts
- Force buy/sell commands

Runs natively in Pythonista 3 on iPhone/iPad.
"""

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
UPDATE_INTERVAL     = 10
CHART_LENGTH        = 10
VOLATILITY_WINDOW   = 10
INITIAL_BALANCE     = 1_000_000.0
API_TIMEOUT         = 10

# Coins to monitor (expanded per X discussion)
SYMBOLS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "DOGE_USDT", "SHIB_USDT", "CRO_USDT", "XRP_USDT", "ADA_USDT"]

# AI Settings
AI_MODEL            = "deepseek/deepseek-chat"
AI_CONSULT_INTERVAL = 15
REFERER_URL         = "https://mohameddodda.github.io/Paper_trading_bot/"

# Smart Strategy
COOLDOWN            = 300
MAX_RISK_PCT        = 0.03
STOP_LOSS_PCT       = -0.05
TAKE_PROFIT_PCT     = 0.10

__version__ = "1.2.1"
log_file = os.path.expanduser('~/Documents/paper_trading_log.csv')

# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
import requests
import time
import csv
import os
import datetime
import console
import notification
import threading
import queue
import json
import random
import keychain
import re
import sound  # For voice alerts
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ------------------------------------------------------------
# SESSION WITH RETRY
# ------------------------------------------------------------
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# ------------------------------------------------------------
# DATA STRUCTURES
# ------------------------------------------------------------
price_history   = {s: [] for s in SYMBOLS}
portfolio       = {}
sim_balance     = INITIAL_BALANCE
running         = True
cmd_queue       = queue.Queue()

entry_prices    = {}
last_buy_time   = {}
ai_reasons      = {s: "" for s in SYMBOLS}
ai_raw          = {s: "" for s in SYMBOLS}
ai_consult_counter = 0

# ------------------------------------------------------------
# SECURE API KEY
# ------------------------------------------------------------
def get_api_key():
    key = keychain.get_password('paperbot', 'openrouter')
    if not key:
        key = console.input_alert(
            "OpenRouter API Key Required",
            "Get free key at: https://openrouter.ai/keys",
            "", "Paste Key", "text"
        )
        if key and key.strip():
            keychain.set_password('paperbot', 'openrouter', key.strip())
            console.hud_alert("API Key Saved!", 'success', 1)
        else:
            console.hud_alert("No key → AI disabled", 'error', 2)
            return None
    return key.strip()

OPENROUTER_API_KEY = get_api_key()

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_all_prices():
    try:
        r = session.get(
            "https://api.crypto.com/exchange/v1/public/get-tickers",
            timeout=API_TIMEOUT,
            headers={'User-Agent': 'Pythonista/3'}
        )
        r.raise_for_status()
        data = r.json()
        return {item['i']: float(item['a'])
                for item in data.get("result", {}).get("data", [])
                if 'i' in item and 'a' in item}
    except Exception as e:
        console.hud_alert(f"Price fetch error: {e}", 'error', 1)
        return {}

def get_single_price(symbol):
    return fetch_all_prices().get(symbol)

# Volatility Calculation (new X feature)
def calculate_volatility(sym):
    hist = price_history[sym]
    if len(hist) < 2:
        return 0.01
    max_p = max(hist)
    min_p = min(hist)
    if min_p == 0:
        return 0.01
    vol = (max_p - min_p) / min_p
    return max(0.01, min(vol, 0.05))

# AI CONSULT – Robust JSON + Fallback
def consult_ai(symbol, recent_prices, drop_pct, gain_pct):
    global ai_consult_counter
    if not OPENROUTER_API_KEY:
        return "hold", "no key"

    prompt = (
        "You are an automated trading signal generator. You MUST respond in VALID JSON ONLY.\n"
        "Return EXACTLY one JSON object with these keys: signal, reason\n"
        " - signal must be one of: \"buy\", \"sell\", \"hold\"\n"
        " - reason must be a short string (explain briefly, max 60 chars)\n"
        "Do NOT include any other text, markup, or explanation.\n\n"
        f"EXAMPLE:\n{{\"signal\":\"buy\",\"reason\":\"volatility breakout\"}}\n\n"
        f"Now analyze this coin and return the JSON object only.\n"
        f"Coin: {symbol}\n"
        f"Recent prices (most recent last): {recent_prices[-10:]}\n"
        f"Current drop %: {drop_pct:.2f}\n"
        f"Current gain %: {gain_pct:.2f}\n"
    )

    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 80,
        "temperature": 0.0
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": REFERER_URL,
        "X-Title": "Paper Trading Bot",
        "Content-Type": "application/json"
    }

    for attempt in range(3):
        try:
            r = session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=8
            )
            if r.status_code == 429:
                time.sleep(2 + random.random())
                continue
            r.raise_for_status()
            data = r.json()
            raw_txt = ""
            choices = data.get("choices") or []
            if choices:
                msg = choices[0].get("message") or choices[0]
                raw_txt = msg.get("content", "") if isinstance(msg, dict) else str(msg)
            raw_txt = raw_txt.strip()
            ai_raw[symbol] = raw_txt

            m = re.search(r'\{.*\}', raw_txt, re.DOTALL)
            if m:
                try:
                    json_obj = json.loads(m.group(0))
                except:
                    try:
                        json_obj = json.loads(m.group(0).replace("'", '"'))
                    except:
                        json_obj = None
                if json_obj:
                    signal = str(json_obj.get("signal", "")).strip().lower()
                    reason = str(json_obj.get("reason", "")).strip()[:60]
                    if signal in ("buy", "sell", "hold"):
                        return signal, reason

            # Fallback
            txt = raw_txt.lower()
            simple = re.search(r'\b(buy|sell|hold)\b', txt)
            if simple:
                signal = simple.group(1)
                reason = txt.split(":", 1)[-1].strip()[:60] if ":" in raw_txt else "no reason"
                return signal, reason

            return "hold", (raw_txt[:60] or "no response")
        except Exception as e:
            console.hud_alert(f"AI error: {e}", 'error', 1)
            time.sleep(1)
    return "hold", "error"

# Chart & Formatting
def draw_chart(prices):
    if not prices: return " " * CHART_LENGTH
    recent = prices[-CHART_LENGTH:]
    mn, mx = min(recent), max(recent)
    if mn == mx: return "▪" * len(recent)
    if mn == 0: mn = 1e-10
    chars = "▁▂▃▄▅▆▇"
    try:
        return "".join(chars[int((p-mn)/(mx-mn)*(len(chars)-1))] for p in recent).ljust(CHART_LENGTH)
    except:
        return " " * CHART_LENGTH

def format_price(p):
    if p < 0.0001: return f"{p:.8f}"
    if p < 1: return f"{p:,.6f}"
    return f"{p:,.2f}"

def format_qty(q):
    return f"{q:.3f}" if q <= 1e6 else f"{q:.2e}"

def log_trade(sym, action, price, qty, bal, profit_pct=None, reason=""):
    try:
        exists = os.path.isfile(log_file)
        with open(log_file, "a", newline="") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(["Timestamp","Coin","Action","Price","Qty","Balance","Profit%","Reason"])
            w.writerow([now(), sym, action, price, qty, bal, f"{profit_pct:.2f}%" if profit_pct else "", reason])
    except Exception as e:
        console.hud_alert(f"Log error: {e}", 'error', 1)

# Voice Alert (new X feature: iOS sound on trades)
def voice_alert(message):
    try:
        sound.play_effect('arcade:Coin_5')  # Subtle chime; Pythonista built-in
    except:
        pass  # Silent fallback

def dynamic_risk(prices):
    if len(prices) < 2: return 0.02
    changes = [abs((prices[i+1]-prices[i])/prices[i]*100) for i in range(len(prices)-1) if prices[i] != 0]
    if not changes: return 0.02
    vol = sum(changes[-VOLATILITY_WINDOW:]) / min(len(changes), VOLATILITY_WINDOW)
    return min(0.01 + (vol / 10), MAX_RISK_PCT)

def can_buy(sym):
    if portfolio.get(sym, 0) > 0: return False
    if sym in last_buy_time and time.time() - last_buy_time[sym] < COOLDOWN:
        return False
    return True

def reset_bot():
    global sim_balance, portfolio, price_history, entry_prices, last_buy_time, ai_reasons
    portfolio.clear()
    sim_balance = INITIAL_BALANCE
    price_history = {s: [] for s in SYMBOLS}
    entry_prices.clear()
    last_buy_time.clear()
    ai_reasons = {s: "" for s in SYMBOLS}
    notification.schedule("AUTO-RESET: Balance was $0", 0)

def clear():
    try: os.system('clear')
    except: print("\n" * 50)

# ------------------------------------------------------------
# BOT STEP
# ------------------------------------------------------------
def bot_step():
    global sim_balance, ai_consult_counter
    if sim_balance <= 0:
        reset_bot()
        return

    all_prices = fetch_all_prices()
    ai_consult_counter += 1

    for sym in SYMBOLS:
        price = all_prices.get(sym)
        if not price or price <= 0: continue

        price_history[sym].append(price)
        if len(price_history[sym]) > 100:
            price_history[sym].pop(0)

        hist = price_history[sym]
        qty = portfolio.get(sym, 0)
        entry = entry_prices.get(sym, price)

        # Volatility Adjustment (enhanced per X)
        vol = calculate_volatility(sym)

        # AI Signal
        ai_signal, ai_reason = None, ""
        if ai_consult_counter % AI_CONSULT_INTERVAL == 0 and len(hist) > 2:
            max_r = max(hist[:-1] or [price])
            min_r = min(hist[:-1] or [price])
            drop = (price - max_r) / max_r * 100 if max_r != 0 else 0
            gain = (price - min_r) / min_r * 100 if min_r != 0 else 0
            ai_signal, ai_reason = consult_ai(sym, hist, drop, gain)
            if ai_signal in ("buy", "sell", "hold"):
                ai_reasons[sym] = ai_reason

        # SELL Logic
        if qty > 0 and entry != 0:
            profit_loss = (price - entry) / entry
            vol_risk = dynamic_risk(hist)
            dyn_sl = STOP_LOSS_PCT * (1 + vol)  # Wider SL on high vol
            dyn_tp = TAKE_PROFIT_PCT * (1 - vol / 2)  # Tighter TP on high vol

            sold = False
            if profit_loss <= dyn_sl:
                sim_balance += qty * price
                log_trade(sym, "SELL", price, qty, sim_balance, profit_loss*100, "Stop-Loss")
                notification.schedule(f"STOP-LOSS {sym} @ ${price:.2f}", 0)
                voice_alert(f"Sold {sym}")
                sold = True
            elif profit_loss >= dyn_tp:
                sim_balance += qty * price
                log_trade(sym, "SELL", price, qty, sim_balance, profit_loss*100, "Take-Profit")
                notification.schedule(f"TAKE-PROFIT {sym} @ ${price:.2f}", 0)
                voice_alert(f"Sold {sym}")
                sold = True
            elif ai_signal == "sell":
                sell_qty = qty * 0.5
                sim_balance += sell_qty * price
                log_trade(sym, "SELL", price, sell_qty, sim_balance, reason=ai_reason)
                notification.schedule(f"AI SELL {sym} @ ${price:.2f}", 0)
                voice_alert(f"Sold {sym}")
                portfolio[sym] -= sell_qty
                sold = True

            if sold and ai_signal != "sell":
                portfolio[sym] = 0
                entry_prices.pop(sym, None)
                last_buy_time.pop(sym, None)

        # BUY Logic
        if can_buy(sym) and len(hist) > 2:
            max_r = max(hist[:-1])
            drop = (price - max_r) / max_r * 100 if max_r != 0 else 0
            buy_threshold = -0.02 * (1 + vol)  # Dynamic: deeper drop needed on high vol
            if drop <= buy_threshold and (ai_signal == "buy" or ai_signal is None):
                risk_pct = dynamic_risk(hist)
                usd = sim_balance * risk_pct
                if usd > 10:
                    coins = usd / price
                    portfolio[sym] = coins
                    sim_balance -= usd
                    entry_prices[sym] = price
                    last_buy_time[sym] = time.time()
                    log_trade(sym, "BUY", price, coins, sim_balance, reason=ai_reason)
                    notification.schedule(f"BUY {sym} @ ${price:.2f}", 0)
                    voice_alert(f"Bought {sym}")

# ------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------
def display_status():
    clear()
    console.set_color(0,1,1)
    print("+-----------------------------------------------------------+")
    print("| PAPER TRADING BOT                     |")
    status = "RUNNING" if running else "STOPPED"
    console.set_color(1,1,1)
    if not running: console.set_color(1,0,0)
    print(f"| Status: {status:<43}|")
    console.set_color(0,1,1)

    total_holdings = sum(portfolio.get(s, 0) * (price_history.get(s, [0])[-1] or 0) for s in SYMBOLS)
    total_port = sim_balance + total_holdings

    print(f"| Simulated Balance: ${sim_balance:,.2f} ")
    has_pos = any(portfolio.get(s, 0) > 0 for s in SYMBOLS)
    print(f"| Total Portfolio: ${total_port:,.2f} |" if has_pos else "| Total Portfolio: N/A |")
    profit_pct = (total_port - INITIAL_BALANCE) / INITIAL_BALANCE * 100
    console.set_color(0,1,0) if profit_pct >= 0 else console.set_color(1,0,0)
    print(f"| Profit: {profit_pct:+.2f}%{' ':<6}|")
    console.set_color(0,1,1)
    print(f"| {now():<57}|")
    print("+-----------------------------------------------------------+")
    print("| Coin   | Price        | Chg%  | Tr      |")
    print("|--------|--------------|-------|---------|")

    for sym in sorted(SYMBOLS):
        h = price_history.get(sym, [])
        p = h[-1] if h else 0
        prev = h[-2] if len(h) > 1 else p
        chg = (p - prev) / prev * 100 if prev != 0 else 0
        qty = portfolio.get(sym, 0)
        reason = ai_reasons.get(sym, "").lower()
        chart = draw_chart(h)

        # Colors
        coin_color = (0,1,0) if chg > 0.1 else (1,0,0) if chg < -0.1 else (1,1,1)
        tr = "Up" if chg > 0.1 else "Down" if chg < -0.1 else "Neutral"
        qty_color = (0,1,0) if qty > 0 else (0.6,0.6,0.6)
        ai_color = (0,1,0) if "buy" in reason else (1,0,0) if "sell" in reason else (1,1,0)

        console.set_color(*coin_color)
        print(f"| {sym:<6} | ${format_price(p):>11} | {chg:+5.2f}% | {tr} |")
        console.set_color(*qty_color)
        print(f"| Qty: {format_qty(qty):<8}", end="")
        console.set_color(*ai_color)
        print(f"AI: {reason.ljust(12)[:12]} | {chart} |", end="")
        console.set_color(1,1,1)
        print("")

    console.set_color(0,1,1)
    print("+-----------------------------------------------------------+")
    print("| Cmd: start | stop | reset | force buy/sell <coin>          |")
    print("+-----------------------------------------------------------+")

# ------------------------------------------------------------
# INPUT & MAIN LOOP
# ------------------------------------------------------------
def input_thread():
    while True:
        try:
            cmd = input("Command> ").strip().lower()
            if cmd: cmd_queue.put(cmd)
        except EOFError:
            continue

threading.Thread(target=input_thread, daemon=True).start()

notification.schedule("Paper Trading Bot STARTED", 0)
print("Bot started – type commands in console.")
last_update = 0

while True:
    now_ts = time.time()
    if running and now_ts - last_update >= UPDATE_INTERVAL:
        bot_step()
        display_status()
        last_update = now_ts

    try:
        cmd = cmd_queue.get_nowait()
        parts = cmd.split()
        if cmd == "start":
            running = True
            notification.schedule("Bot STARTED", 0)
        elif cmd == "stop":
            running = False
            notification.schedule("Bot STOPPED", 0)
        elif cmd == "reset":
            reset_bot()
            notification.schedule("Reset complete", 0)
        elif len(parts) >= 3 and parts[0] == "force":
            action, coin = parts[1], parts[2].upper()
            full = coin if "_" in coin else f"{coin}_USDT"
            if full not in SYMBOLS:
                console.hud_alert(f"{full} not watched", 'error', 1)
            else:
                price = get_single_price(full)
                if not price:
                    console.hud_alert("Price fetch failed", 'error', 1)
                elif action == "buy" and sim_balance > 10:
                    usd = min(sim_balance * 0.03, 1000)
                    qty = usd / price
                    portfolio[full] = qty
                    sim_balance -= usd
                    entry_prices[full] = price
                    last_buy_time[full] = time.time()
                    log_trade(full, "BUY", price, qty, sim_balance)
                    notification.schedule(f"FORCED BUY {qty:.6f} {full}", 0)
                    voice_alert(f"Bought {full}")
                elif action == "sell" and portfolio.get(full, 0) > 0:
                    qty = portfolio[full]
                    sim_balance += qty * price
                    log_trade(full, "SELL", price, qty, sim_balance)
                    portfolio[full] = 0
                    entry_prices.pop(full, None)
                    last_buy_time.pop(full, None)
                    notification.schedule(f"FORCED SELL {qty:.6f} {full}", 0)
                    voice_alert(f"Sold {full}")
        display_status()
    except queue.Empty:
        pass
    time.sleep(0.1)