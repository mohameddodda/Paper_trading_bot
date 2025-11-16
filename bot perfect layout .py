# ------------------------------------------------------------
#  PAPER TRADING BOT – Pythonista 3 (FIXED AI PARSING)
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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -------------------------
# CONFIG
# -------------------------
UPDATE_INTERVAL     = 10
CHART_LENGTH        = 10
VOLATILITY_WINDOW   = 10
INITIAL_BALANCE     = 1_000.0
API_TIMEOUT         = 10

# ---- OpenRouter API Key (Secure & Persistent) ----
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
AI_MODEL            = "mistralai/mistral-7b-instruct:free"
AI_CONSULT_INTERVAL = 15
ai_consult_counter  = 0

# ---- YOUR referer ------------------------------------------
REFERER_URL = "https://mohameddodda.github.io/Paper_trading_bot/"

# ---- Coins to watch ----------------------------------------
symbols_to_watch = ["BTC_USDT", "ETH_USDT", "SOL_USDT",
                    "DOGE_USDT", "SHIB_USDT", "CRO_USDT"]
log_file = os.path.expanduser('~/Documents/paper_trading_log.csv')

# -------------------------
# SESSION WITH RETRY
# -------------------------
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# -------------------------
# DATA STRUCTURES
# -------------------------
price_history   = {s: [] for s in symbols_to_watch}
portfolio       = {}
sim_balance     = INITIAL_BALANCE
running         = True
cmd_queue       = queue.Queue()

# Smart Strategy
entry_prices    = {}
last_buy_time   = {}
COOLDOWN        = 300
MAX_RISK_PCT    = 0.03
STOP_LOSS_PCT   = -0.05
TAKE_PROFIT_PCT = 0.10

# AI Reasons (stores short reason) and raw responses for debugging
ai_reasons = {s: "" for s in symbols_to_watch}
ai_raw = {s: "" for s in symbols_to_watch}

# -------------------------
# HELPERS
# -------------------------
def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_single_price(symbol):
    all_prices = fetch_all_prices()
    return all_prices.get(symbol)

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
        console.hud_alert(f"All-tickers error: {e}", 'error', 1)
        return {}

# ---- AI CONSULT (robust JSON extraction + fallback) ----
def consult_ai(symbol, recent_prices, drop_pct, gain_pct):
    """
    Returns: (signal, reason)
    - signal: "buy" / "sell" / "hold"
    - reason: short string (max ~40 chars) for UI/logging
    This function:
    1) Strongly instructs model to output JSON only.
    2) Attempts to extract JSON from the response via regex.
    3) If JSON parse fails, falls back to heuristic parsing (first word buy/sell/hold + reason).
    4) Saves raw response into ai_raw for debugging.
    """
    global ai_consult_counter
    if not OPENROUTER_API_KEY:
        return "hold", "no key"

    # Strict prompt forcing JSON-only output
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

    backoff = 2.0
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            r = session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=8
            )
            # Handle rate limit gracefully
            if r.status_code == 429:
                wait = backoff + random.random()
                console.hud_alert(f"AI 429 – waiting {wait:.1f}s", 'error', 1)
                time.sleep(wait)
                backoff = min(backoff * 2, 30)
                continue
            r.raise_for_status()

            # Extract content (may be noisy)
            data = r.json()
            # Defensive access
            choices = data.get("choices") or data.get("output") or []
            if not choices:
                raw_txt = json.dumps(data)[:200]
            else:
                # Support both OpenAI-style and other shapes
                msg = choices[0].get("message") or choices[0]
                raw_txt = ""
                if isinstance(msg, dict):
                    raw_txt = (msg.get("content") or msg.get("text") or "") 
                else:
                    raw_txt = str(msg)

            raw_txt = (raw_txt or "").strip()
            ai_raw[symbol] = raw_txt  # store raw for debug

            # Try to extract a JSON object using regex (find first {...})
            json_obj = None
            m = re.search(r'\{.*\}', raw_txt, flags=re.DOTALL)
            if m:
                candidate = m.group(0)
                try:
                    json_obj = json.loads(candidate)
                except Exception:
                    # attempt to "fix" common issues: single quotes -> double quotes
                    try:
                        fixed = candidate.replace("'", '"')
                        json_obj = json.loads(fixed)
                    except Exception:
                        json_obj = None

            if json_obj:
                signal = str(json_obj.get("signal", "")).strip().lower()
                reason = str(json_obj.get("reason", "")).strip()
                if signal not in ("buy", "sell", "hold"):
                    # invalid -> fallback
                    signal = "hold"
                    reason = "parse err"
                reason = reason[:60]
                return signal, reason

            # --- Fallback heuristics if no JSON found ---
            txt = raw_txt.lower()
            # Try to find a buy/sell/hold token at the start
            simple = re.search(r'\b(buy|sell|hold)\b', txt)
            if simple:
                signal = simple.group(1)
                # attempt to get trailing reason after colon or after the keyword
                reason = ""
                # after ":" pattern
                if ":" in raw_txt:
                    parts = raw_txt.split(":", 1)
                    reason = parts[1].strip()
                else:
                    # take 6-10 words after the signal word
                    tokens = txt.split()
                    try:
                        idx = tokens.index(signal)
                        reason = " ".join(tokens[idx+1:idx+7])
                    except Exception:
                        reason = ""
                reason = reason.strip()[:60] or "no reason"
                return signal, reason

            # If still nothing, return hold with truncated raw for debugging
            truncated = (raw_txt.replace("\n", " ")[:60]).strip()
            return "hold", truncated or "no response"

        except Exception as e:
            print(f"AI FULL ERROR (attempt {attempt}): {e}")
            console.hud_alert(f"AI error: {e}", 'error', 1)
            time.sleep(1 + attempt)
            continue

    # If all attempts fail
    return "hold", "error"

# ---- Chart & formatting ------------------------------------
def draw_chart(prices):
    if not prices: return " " * CHART_LENGTH
    recent = prices[-CHART_LENGTH:]
    mn, mx = min(recent), max(recent)
    if mn == mx: return "▪" * len(recent)
    if mn == 0: mn = 1e-10  # Avoid div by zero
    chars = "▁▂▃▄▅▆▇"
    try:
        return "".join(chars[int((p-mn)/(mx-mn)*(len(chars)-1))] for p in recent).ljust(CHART_LENGTH)
    except Exception:
        return " " * CHART_LENGTH

def format_price(p):
    if p < 0.0001: return f"{p:.8f}"
    if p < 1:      return f"{p:,.6f}"
    return f"{p:,.2f}"

def format_qty(q):
    if q > 1e6:
        return f"{q:.2e}"
    else:
        return f"{q:.3f}"

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

def dynamic_risk(prices):
    if len(prices) < 2: return 0.02
    changes = []
    for i in range(len(prices)-1):
        if prices[i] == 0: continue
        changes.append(abs((prices[i+1]-prices[i])/prices[i]*100))
    if not changes: return 0.02
    vol = sum(changes[-VOLATILITY_WINDOW:]) / min(len(changes), VOLATILITY_WINDOW)
    risk = 0.01 + (vol / 10)
    return min(risk, MAX_RISK_PCT)

def can_buy(sym):
    if portfolio.get(sym, 0) > 0: return False
    if sym in last_buy_time:
        if time.time() - last_buy_time[sym] < COOLDOWN:
            return False
    return True

def reset_bot():
    global sim_balance, portfolio, price_history, entry_prices, last_buy_time, ai_reasons
    portfolio.clear()
    sim_balance = INITIAL_BALANCE
    price_history = {s: [] for s in symbols_to_watch}
    entry_prices.clear()
    last_buy_time.clear()
    ai_reasons = {s: "" for s in symbols_to_watch}
    notification.schedule("AUTO-RESET: Balance was $0", 0)

def clear():
    try: os.system('clear')
    except: print("\n"*50)

# -------------------------
# BOT STEP
# -------------------------
def bot_step():
    global sim_balance, ai_consult_counter
    if sim_balance <= 0:
        reset_bot()
        return

    all_prices = fetch_all_prices()
    ai_consult_counter += 1

    for sym in symbols_to_watch:
        price = all_prices.get(sym)
        if price is None or price <= 0: continue

        price_history[sym].append(price)
        if len(price_history[sym]) > 100:
            price_history[sym].pop(0)

        hist = price_history[sym]
        qty = portfolio.get(sym, 0)
        entry = entry_prices.get(sym, price)

        # --- AI Consult ---
        ai_signal = None
        ai_reason = ""
        if ai_consult_counter % AI_CONSULT_INTERVAL == 0 and len(hist) > 2:
            max_r = max(hist[:-1] or [price])
            min_r = min(hist[:-1] or [price])
            drop = (price - max_r)/max_r*100 if max_r != 0 else 0
            gain = (price - min_r)/min_r*100 if min_r != 0 else 0
            ai_signal, ai_reason = consult_ai(sym, hist, drop, gain)
            # Ensure safe defaults
            if ai_signal not in ("buy", "sell", "hold"):
                ai_signal = "hold"
            ai_reasons[sym] = (ai_reason or "").strip()
        
        # --- SELL: Stop-Loss / Take-Profit / AI ---
        if qty > 0:
            if entry == 0: continue
            profit_loss = (price - entry) / entry
            sold = False

            # Dynamic SL/TP based on volatility
            vol_risk = dynamic_risk(hist)
            dyn_sl = STOP_LOSS_PCT - vol_risk
            dyn_tp = TAKE_PROFIT_PCT + vol_risk

            if profit_loss <= dyn_sl:
                usd = qty * price
                sim_balance += usd
                log_trade(sym, "SELL", price, qty, sim_balance, profit_loss*100, "Stop-Loss")
                notification.schedule(f"STOP-LOSS {sym} @ ${price:.2f}", 0)
                sold = True
            elif profit_loss >= dyn_tp:
                usd = qty * price
                sim_balance += usd
                log_trade(sym, "SELL", price, qty, sim_balance, profit_loss*100, "Take-Profit")
                notification.schedule(f"TAKE-PROFIT {sym} @ ${price:.2f}", 0)
                sold = True
            elif ai_signal == "sell":
                sell_qty = qty * 0.5
                usd = sell_qty * price
                sim_balance += usd
                portfolio[sym] -= sell_qty
                log_trade(sym, "SELL", price, sell_qty, sim_balance, reason=ai_reason)
                notification.schedule(f"AI SELL {sym} @ ${price:.2f}", 0)
                sold = True

            if sold and ai_signal != "sell":
                portfolio[sym] = 0
                entry_prices.pop(sym, None)
                last_buy_time.pop(sym, None)

        # --- BUY ---
        if can_buy(sym) and len(hist) > 2:
            max_r = max(hist[:-1])
            drop = (price - max_r)/max_r*100 if max_r != 0 else 0
            if drop <= -0.5 and (ai_signal == "buy" or ai_signal is None):
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

# -------------------------
# DISPLAY – PERFECT 2-LINE LAYOUT + FULL COLOR
# -------------------------
def display_status():
    clear()
    console.set_color(0,1,1)  # cyan border
    print("+-----------------------------------------------------------+")
    print("|🧪 PAPER TRADING BOT                     |")
    status = "RUNNING" if running else "STOPPED"
    console.set_color(1,1,1)
    if not running: console.set_color(1,0,0)
    print(f"| Status: {status:<43}|")
    console.set_color(0,1,1)

    # Calculate total portfolio value
    total_holdings = 0
    for sym in symbols_to_watch:
        qty = portfolio.get(sym, 0)
        p = price_history.get(sym, [0])[-1]
        total_holdings += qty * p
    total_port = sim_balance + total_holdings

    # Show balance
    print(f"| Simulated Balance: ${sim_balance:,.2f} ") 

    # Show total portfolio only if holdings exist
    has_positions = any(portfolio.get(s, 0) > 0 for s in symbols_to_watch)
    if has_positions:
        print(f"| Total Portfolio: ${total_port:,.2f} |")
    else:
        print(f"| Total Portfolio: N/A (no positions) |")

    # Profit % based on total portfolio
    profit_pct = (total_port - INITIAL_BALANCE) / INITIAL_BALANCE * 100
    profit_str = f"{profit_pct:+.2f}%"
    console.set_color(0,1,0) if profit_pct >= 0 else console.set_color(1,0,0)
    print(f"| Profit: {profit_str:<8}|")
    console.set_color(0,1,1)
    print(f"| {now():<57}|")
    print("+-----------------------------------------------------------+")
    print("| Coin   | Price        | Chg%  | Tr      |")
    print("|--------|--------------|-------|---------|")

    for sym in sorted(symbols_to_watch):
        h = price_history.get(sym, [])
        p = h[-1] if h else 0
        prev = h[-2] if len(h)>1 else p
        chg = (p-prev)/prev*100 if prev != 0 else 0
        qty = portfolio.get(sym, 0)
        reason = ai_reasons.get(sym, "").strip().lower()
        chart = draw_chart(h)

        # --- COIN NAME COLOR (UP/DOWN) ---
        if chg > 0.1:
            coin_color = (0,1,0)      # GREEN
        elif chg < -0.1:
            coin_color = (1,0,0)      # RED
        else:
            coin_color = (1,1,1)      # WHITE

        # --- TREND EMOJI ---
        if chg > 0.1:
            console.set_color(0,1,0); tr = "🎄"
        elif chg < -0.1:
            console.set_color(1,0,0); tr = "🛑"
        else:
            console.set_color(1,1,0); tr = "⚠️"

        # --- QTY COLOR ---
        qty_str = format_qty(qty).ljust(8)
        if qty > 0:
            qty_color = (0,1,0)       # GREEN
        else:
            qty_color = (0.6,0.6,0.6) # GRAY

        # --- AI TEXT COLOR ---
        if "buy" in reason:
            ai_color = (0,1,0)
        elif "sell" in reason:
            ai_color = (1,0,0)
        elif "hold" in reason or not reason:
            ai_color = (1,1,0)
        else:
            ai_color = (0.7,0.7,0.7)

        # --- LINE 1: Coin (colored) ---
        console.set_color(*coin_color)
        print(f"| {sym:<6}", end="")
        console.set_color(1,1,1)
        print(f" | ${format_price(p):>11} | {chg:+5.2f}% | {tr} |")

        # --- LINE 2: Qty + AI + Chart (same line) ---
        console.set_color(*qty_color)
        print(f"| Qty: {qty_str}", end="")
        console.set_color(*ai_color)
        # show reason (12 chars) and also indicate if raw exists (for debug)
        debug_suffix = ""
        if ai_raw.get(sym):
            debug_suffix = " *"
        print(f"AI: {reason.ljust(12)[:12]}{debug_suffix}", end="")
        console.set_color(1,1,1)
        print(f" | {chart} |")

    console.set_color(0,1,1)
    print("+-----------------------------------------------------------+")
    print("| Cmd: start | stop | reset | force buy/sell <coin>          |")
    print("+-----------------------------------------------------------+")

# -------------------------
# INPUT THREAD
# -------------------------
def input_thread():
    while True:
        try:
            cmd = input("Command> ").strip().lower()
            if cmd: cmd_queue.put(cmd)
        except EOFError:
            continue

threading.Thread(target=input_thread, daemon=True).start()

# -------------------------
# MAIN LOOP
# -------------------------
notification.schedule("🧪 Paper Trading Bot STARTED", 0)
print("Bot started – type commands in the console.")
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
            notification.schedule("🧪 Bot STARTED", 0)
        elif cmd == "stop":
            running = False
            notification.schedule("🛑 Bot STOPPED", 0)
        elif cmd == "reset":
            reset_bot()
            notification.schedule("Reset complete", 0)
        elif len(parts) >= 3 and parts[0] == "force":
            action, coin = parts[1], parts[2].upper()
            full = coin if "_" in coin else f"{coin}_USDT"
            if full not in symbols_to_watch:
                console.hud_alert(f"{full} not watched", 'error', 1)
            else:
                price = get_single_price(full)
                if not price or price <= 0:
                    console.hud_alert("Price fetch failed", 'error', 1)
                else:
                    if action == "buy" and sim_balance > 10:
                        usd = min(sim_balance * 0.03, 1000)
                        qty = usd / price
                        portfolio[full] = qty
                        sim_balance -= usd
                        entry_prices[full] = price
                        last_buy_time[full] = time.time()
                        log_trade(full, "BUY", price, qty, sim_balance)
                        notification.schedule(f"FORCED BUY {qty:.6f} {full}", 0)
                    elif action == "sell":
                        qty = portfolio.get(full, 0)
                        if qty > 0:
                            sim_balance += qty * price
                            log_trade(full, "SELL", price, qty, sim_balance)
                            portfolio[full] = 0
                            entry_prices.pop(full, None)
                            last_buy_time.pop(full, None)
                            notification.schedule(f"FORCED SELL {qty:.6f} {full}", 0)
        display_status()
    except queue.Empty:
        pass

    time.sleep(0.1)