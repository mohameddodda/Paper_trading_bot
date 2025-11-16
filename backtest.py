"""
backtest.py – Historical Strategy Testing
========================================

Simulates bot performance using real historical data from Crypto.com.
NO real trading. NO API keys used during backtest.
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

from config import (
    SYMBOLS,
    STARTING_CASH,
    BACKTEST_DAYS,
    AGGREGATE_SIZE,
    AGGREGATE_UNIT,
)
from bot import PaperTradingBot

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# === Crypto.com Public API (No Key Needed) ===
CRYPTOCOM_BASE = "https://api.crypto.com/v2/public"

def fetch_crypto_com_aggs(symbol: str, days: int = BACKTEST_DAYS) -> pd.DataFrame:
    """Fetch 1-minute candle data from Crypto.com public API."""
    try:
        import requests

        # Convert symbol: BTC_USDT → BTC-USDT
        instrument = symbol.replace("_", "-")
        limit = min(1440 * days, 2000)  # Max 2000 per request
        url = f"{CRYPTOCOM_BASE}/get-candlestick"
        params = {
            "instrument_name": instrument,
            "timeframe": "1m",
            "count": limit,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0 or not data.get("result", {}).get("data"):
            log.warning(f"No data for {symbol}")
            return pd.DataFrame()

        df = pd.DataFrame(data["result"]["data"])
        df["t"] = pd.to_datetime(df["t"], unit="s", utc=True)
        df = df.rename(columns={"t": "timestamp", "c": "close"})
        df = df[["timestamp", "close"]].sort_values("timestamp").reset_index(drop=True)
        return df

    except Exception as e:
        log.error(f"Failed to fetch {symbol}: {e}")
        return pd.DataFrame()


def run_backtest() -> None:
    """Run full backtest across all symbols."""
    log.info(f"Starting backtest: {BACKTEST_DAYS} days, {len(SYMBOLS)} symbols")

    bot = PaperTradingBot()
    bot.portfolio = {sym: 0.0 for sym in SYMBOLS}
    bot.portfolio["USD"] = STARTING_CASH
    bot.history: Dict[str, List[dict]] = {}

    # === Fetch Historical Data ===
    for sym in SYMBOLS:
        log.info(f"Fetching {sym}...")
        df = fetch_crypto_com_aggs(sym)
        if df.empty:
            log.warning(f"Skipping {sym} – no data")
            continue
        bot.history[sym] = df.to_dict("records")

    if not bot.history:
        log.error("No data fetched. Backtest aborted.")
        return

    # === Simulate Tick-by-Tick ===
    all_timestamps = sorted(
        {rec["timestamp"] for sym in bot.history for rec in bot.history[sym]}
    )
    log.info(f"Simulating {len(all_timestamps)} ticks...")

    for current_time in all_timestamps:
        # Update live history up to current time
        for sym in SYMBOLS:
            if sym in bot.history:
                bot.history[sym] = [
                    rec for rec in bot.history[sym] if rec["timestamp"] <= current_time
                ]

        # Decision per symbol
        for sym in SYMBOLS:
            if sym not in bot.history or len(bot.history[sym]) < 20:
                continue

            action = bot.rule_based_decision(sym)
            if action != "hold":
                # Micro-trade for simulation
                bot.execute_trade(sym, action, amount_usd=STARTING_CASH * 0.001)  # 0.1%

    # === Final Portfolio Value ===
    final_usd = bot.portfolio["USD"]
    for sym in SYMBOLS:
        if sym in bot.history and bot.history[sym]:
            last_price = bot.history[sym][-1]["price"]
            final_usd += bot.portfolio[sym] * last_price

    log.info(f"Backtest Complete!")
    log.info(f"Starting Balance: ${STARTING_CASH:,.2f}")
    log.info(f"Final Net Worth:  ${final_usd:,.2f}")
    log.info(f"Total Return:     {((final_usd / STARTING_CASH) - 1) * 100:+.2f}%")

    # Optional: Save results
    bot.save_portfolio_snapshot("backtest_final.json")
    bot.plot_performance(title="Backtest Performance", save_path="backtest_chart.png")


if __name__ == "__main__":
    run_backtest()