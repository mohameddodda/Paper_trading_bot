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
SYMBOLS = config['symbols']
AI_MODEL = config['ai_model']
AI_CONSULT_INTERVAL = config['ai_consult_interval']
REFERER_URL = config['referer_url']
COOLDOWN = config['cooldown']
MAX_RISK_PCT = config['max_risk_pct']
STOP_LOSS_PCT = config['stop_loss_pct']
TAKE_PROFIT_PCT = config['take_profit_pct']
LOG_FILE = os.path.expanduser(config['log_file'])
PRICE_CACHE_TTL = config['price_cache_ttl']
MAX_RETRIES = config['max_retries']
RETRY_BACKOFF = config['retry_backoff']

# ------------------ Global Variables ------------------
price_history = {s: [] for s in SYMBOLS}
portfolio = {}
sim_balance = INITIAL_BALANCE
running = True
cmd_queue = queue.Queue()

entry_prices = {}
last_buy_time = {}
ai_reasons = {s: "" for s in SYMBOLS}
ai_raw = {s: "" for s in SYMBOLS}
ai_consult_counter = 0

# Price cache for performance
price_cache = {}
price_cache_timestamp = 0

# ------------------ Utility Functions ------------------
def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_all_prices():
    global price_cache, price_cache_timestamp
    current_time = time.time()
    if current_time - price_cache_timestamp < PRICE_CACHE_TTL and price_cache:
        return price_cache.copy()
    try:
        r = requests.get(
            "https://api.crypto.com/exchange/v1/public/get-tickers",
            timeout=API_TIMEOUT,
            headers={'User-Agent': 'CryptoBot/1.0'}
        )
        r.raise_for_status()
        data = r.json()
        prices = {item['i']: float(item['a']) for item in data.get("result", {}).get("data", []) if 'i' in item and 'a' in item}
        price_cache = prices.copy()
        price_cache_timestamp = current_time
        return prices
    except Exception as e:
        print(f"[{now()}] Price fetch error: {e}")
        return price_cache.copy() if price_cache else {}

def get_single_price(symbol):
    return fetch_all_prices().get(symbol)

def log_trade(sym, action, price, qty, bal, profit_pct=None, reason=""):
    try:
        exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(["Timestamp", "Coin", "Action", "Price", "Qty", "Balance", "Profit%", "Reason"])
            writer.writerow([now(), sym, action, price, qty, bal, f"{profit_pct:.2f}%" if profit_pct else "", reason])
    except Exception as e:
        print(f"[{now()}] Log error: {e}")

def notify(title, message):
    if notification:
        notification.notify(title=title, message=message, timeout=3)
    else:
        print(f"[{now()}] {title}: {message}")

def sound_alert():
    # Cross-platform sound alert
    if playsound:
        try:
            # You can specify a sound file path here
            playsound('alert.mp3')  # Ensure this file exists
        except:
            pass
    elif winsound:
        try:
            winsound.Beep(1000, 300)
        except:
            pass
    else:
        pass  # No sound module available

# ------------------ AI Interaction ------------------
def get_api_key():
    # Check environment variable first, fallback to prompt
    key = os.getenv('OPENROUTER_API_KEY')
    if key:
        return key.strip()
    key = input("Enter your OpenRouter API key: ").strip()
    return key

OPENROUTER_API_KEY = get_api_key()

def consult_ai(symbol, recent_prices, drop_pct, gain_pct):
    if not OPENROUTER_API_KEY:
        return "hold", "no key"
    prompt = (
        "You are an automated trading signal generator. You MUST respond in VALID JSON ONLY.\n"
        "Return EXACTLY one JSON object with these keys: signal, reason\n"
        " - signal must be one of: \"buy\", \"sell\", \"hold\"\n"
        " - reason must be a short string (max 60 chars)\n"
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
        "X-Title": "CryptoPaperBot",
        "Content-Type": "application/json"
    }

    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=8
            )
            if r.status_code == 429:
                print(f"[{now()}] AI rate limited, retrying...")
                time.sleep(RETRY_BACKOFF ** attempt + random.random())
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

            # Extract JSON using regex
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
            # Fallback heuristics
            txt = raw_txt.lower()
            simple = re.search(r'\b(buy|sell|hold)\b', txt)
            if simple:
                signal = simple.group(1)
                reason = txt.split(":", 1)[-1].strip()[:60]
                return signal, reason
            return "hold", raw_txt[:60] or "no response"
        except Exception as e:
            print(f"[{now()}] AI error on attempt {attempt+1}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF ** attempt)
    return "hold", "error"

# ------------------ Core Logic ------------------
def calculate_volatility(sym):
    global price_history
    hist = price_history[sym]
    if len(hist) < 2:
        return 0.01
    max_p = max(hist)
    min_p = min(hist)
    if min_p == 0:
        return 0.01
    return max(0.01, min((max_p - min_p) / min_p, 0.05))

def dynamic_risk(prices):
    global MAX_RISK_PCT
    if len(prices) < 2:
        return 0.02
    changes = [abs((prices[i+1] - prices[i]) / prices[i]) for i in range(len(prices)-1) if prices[i] != 0]
    if not changes:
        return 0.02
    vol = sum(changes[-VOLATILITY_WINDOW:]) / min(len(changes), VOLATILITY_WINDOW)
    risk = 0.01 + (vol / 10)
    return min(risk, MAX_RISK_PCT)

def can_buy(sym):
    global last_buy_time, portfolio
    if portfolio.get(sym, 0) > 0:
        return False
    if sym in last_buy_time and (time.time() - last_buy_time[sym]) < COOLDOWN:
        return False
    return True

def reset_bot():
    global sim_balance, portfolio, price_history, entry_prices, last_buy_time, ai_reasons
    print(f"[{now()}] Resetting bot and portfolio.")
    portfolio.clear()
    sim_balance = INITIAL_BALANCE
    for s in SYMBOLS:
        price_history[s] = []
    entry_prices.clear()
    last_buy_time.clear()
    for s in SYMBOLS:
        ai_reasons[s] = ""
    notify("Auto-Reset", "Portfolio and balance reset.")

# ------------------ Main Bot Step ------------------
def bot_step():
    global ai_consult_counter, price_history, portfolio, entry_prices, last_buy_time, sim_balance
    if sim_balance <= 0:
        reset_bot()
        return

    all_prices = fetch_all_prices()
    ai_consult_counter += 1

    for sym in SYMBOLS:
        price = all_prices.get(sym)
        if not price or price <= 0:
            continue

        # Update price history
        price_history[sym].append(price)
        if len(price_history[sym]) > 100:
            price_history[sym].pop(0)

        hist = price_history[sym]
        qty = portfolio.get(sym, 0)
        entry_price = entry_prices.get(sym, price)

        # AI Signal
        ai_signal, ai_reason = None, ""
        if ai_consult_counter % AI_CONSULT_INTERVAL == 0 and len(hist) > 2:
            max_r = max(hist[:-1]) if len(hist) > 1 else price
            min_r = min(hist[:-1]) if len(hist) > 1 else price
            drop = (price - max_r) / max_r * 100 if max_r != 0 else 0
            gain = (price - min_r) / min_r * 100 if min_r != 0 else 0
            ai_signal, ai_reason = consult_ai(sym, hist, drop, gain)
            ai_reasons[sym] = ai_reason

        # --- SELL Logic ---
        if qty > 0 and entry_price != 0:
            profit_loss = (price - entry_price) / entry_price
            vol_risk = dynamic_risk(hist)
            dyn_sl = STOP_LOSS_PCT * (1 + vol_risk)
            dyn_tp = TAKE_PROFIT_PCT * (1 - vol_risk/2)
            sold = False

            if profit_loss <= dyn_sl:
                # Stop loss
                usd = qty * price
                sim_balance += usd
                log_trade(sym, "SELL", price, qty, sim_balance, profit_loss*100, "Stop-Loss")
                notify(f"Stop Loss {sym}", f"Sold {sym} @ ${price:.2f}")
                sound_alert()
                portfolio[sym] = 0
                entry_prices.pop(sym, None)
                last_buy_time.pop(sym, None)
                sold = True
            elif profit_loss >= dyn_tp:
                # Take profit
                usd = qty * price
                sim_balance += usd
                log_trade(sym, "SELL", price, qty, sim_balance, profit_loss*100, "Take-Profit")
                notify(f"Take Profit {sym}", f"Sold {sym} @ ${price:.2f}")
                sound_alert()
                portfolio[sym] = 0
                entry_prices.pop(sym, None)
                last_buy_time.pop(sym, None)
                sold = True
            elif ai_signal == "sell":
                # AI sell signal
                sell_qty = qty * 0.5
                usd = sell_qty * price
                sim_balance += usd
                log_trade(sym, "SELL", price, sell_qty, sim_balance, reason=ai_reason)
                notify(f"AI Sell {sym}", f"Sold {sell_qty:.4f} {sym} @ ${price:.2f}")
                sound_alert()
                portfolio[sym] -= sell_qty
                if portfolio[sym] <= 0:
                    portfolio[sym] = 0
                entry_prices.pop(sym, None)
                last_buy_time.pop(sym, None)
                sold = True

        # --- BUY Logic ---
        if can_buy(sym) and len(hist) > 2:
            max_r = max(hist[:-1]) if len(hist) > 1 else price
            drop = (price - max_r) / max_r * 100 if max_r != 0 else 0
            buy_threshold = -0.02 * (1 + calculate_volatility(sym))
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
                    notify(f"Buy {sym}", f"Bought {coins:.4f} {sym} @ ${price:.2f}")
                    sound_alert()

# ------------------ Display Function ------------------
def display_status():
    global sim_balance
    print("\n" + "="*60)
    print(f"[{now()}] PAPER TRADING SIMULATION")
    print(f"Status: {'RUNNING' if running else 'PAUSED'}")
    total_holdings_value = sum(portfolio.get(s, 0) * (price_history[s][-1] if price_history[s] else 0) for s in SYMBOLS)
    total_portfolio = sim_balance + total_holdings_value
    profit_pct = (total_portfolio - INITIAL_BALANCE) / INITIAL_BALANCE * 100

    print(f"Balance: ${sim_balance:,.2f}")
    print(f"Total Portfolio Value: ${total_portfolio:,.2f}")
    print(f"Profit: {profit_pct:+.2f}%")
    print("-"*60)
    print(f"{'Coin':<8}{'Price':>12}{'Chg%':>8}{'Qty':>12}{'Reason':<15}")
    for sym in sorted(SYMBOLS):
        h = price_history.get(sym, [])
        p = h[-1] if h else 0
        prev = h[-2] if len(h) > 1 else p
        chg = (p - prev) / prev * 100 if prev != 0 else 0
        qty = portfolio.get(sym, 0)
        reason = ai_reasons.get(sym, "").lower()
        print(f"{sym:<8}${p:>11.2f}{chg:>8.2f}%{qty:>12.4f} {reason:<15}")
    print("="*60)

# ------------------ Command Thread ------------------
def input_thread():
    global running
    while True:
        cmd = input("Command> ").strip().lower()
        if cmd:
            cmd_queue.put(cmd)

threading.Thread(target=input_thread, daemon=True).start()

# ------------------ Main Loop ------------------
def main():
    global running, sim_balance, ai_reasons, ai_raw, ai_consult_counter
    print("Crypto Paper Trading Bot - AI-Powered v1.2.1")
    notify("Crypto Bot", "Started")
    print("Type 'start', 'stop', 'reset', 'exit' or 'help' for commands.")

    last_update = 0
    while True:
        # Process commands
        try:
            cmd = cmd_queue.get_nowait()
            if cmd == "start":
                running = True
                notify("Bot", "Started")
            elif cmd == "stop":
                running = False
                notify("Bot", "Paused")
            elif cmd == "reset":
                reset_bot()
            elif cmd == "exit":
                print("Exiting...")
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