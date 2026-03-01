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

"""
backtest.py – Historical Strategy Testing
========================================

Simulates bot performance using real historical data from Crypto.com or Yahoo Finance.
NO real trading. NO API keys used during backtest.
For educational paper trading simulations only.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SYMBOLS,
    STARTING_CASH,
    BACKTEST_DAYS,
    AGGREGATE_SIZE,
    AGGREGATE_UNIT,
    STOCK_MODE,
    CRYPTO_MODE,
    LOG_FILE,
)
from core import fetch_data_for_symbols, moving_average_crossover, backtest_strategy

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    filename=LOG_FILE,
)
log = logging.getLogger(__name__)

# === Crypto.com Public API (No Key Needed) ===
CRYPTOCOM_BASE = "https://api.crypto.com/v2/public"

def fetch_crypto_com_aggs(symbol: str, days: int = BACKTEST_DAYS) -> pd.DataFrame:
    """Fetch 1-minute candle data from Crypto.com public API."""
    try:
        import requests
        import time

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
        df = df.rename(columns={"t": "timestamp", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})
        df = df[["timestamp", "Open", "High", "Low", "Close", "Volume"]].sort_values("timestamp").reset_index(drop=True)
        time.sleep(1)  # Respect API rate limits
        return df

    except Exception as e:
        log.error(f"Failed to fetch {symbol}: {e}")
        return pd.DataFrame()

def fetch_historical_data() -> Dict[str, pd.DataFrame]:
    """Fetch historical data based on mode (crypto or stock)."""
    data = {}
    if CRYPTO_MODE:
        for sym in SYMBOLS:
            log.info(f"Fetching crypto data for {sym}...")
            df = fetch_crypto_com_aggs(sym)
            if not df.empty:
                data[sym] = df
    elif STOCK_MODE:
        # Use core data_fetcher for stocks
        data = fetch_data_for_symbols()
    return data

def run_backtest() -> None:
    """Run full backtest across all symbols using modular bot components."""
    log.info(f"Starting backtest: {BACKTEST_DAYS} days, {len(SYMBOLS)} symbols, Mode: {'Crypto' if CRYPTO_MODE else 'Stock'}")

    # Initialize components
    from bots.cli_bot import PortfolioManager, TradingStrategy, Backtester, Visualizer
    portfolio = PortfolioManager()
    strategy = TradingStrategy()
    backtester = Backtester(portfolio, strategy)
    visualizer = Visualizer(portfolio)

    # Fetch historical data
    historical_data = fetch_historical_data()
    if not historical_data:
        log.error("No data fetched. Backtest aborted.")
        return

    # Simulate trading for each symbol
    for sym, df in historical_data.items():
        if df.empty or len(df) < 50:  # Need enough data for strategy
            log.warning(f"Skipping {sym} – insufficient data")
            continue

        log.info(f"Backtesting {sym}...")

        # Apply strategy (e.g., moving average crossover)
        signals = moving_average_crossover(df)

        # Run backtest simulation
        portfolio_result = backtest_strategy(df, signals, portfolio.sim_balance)

        # Update portfolio with final value (simplified aggregation)
        final_value = portfolio_result['total'].iloc[-1] if not portfolio_result.empty else portfolio.sim_balance
        portfolio.sim_balance = final_value

    # Final results
    final_net_worth = portfolio.sim_balance
    total_return = ((final_net_worth / STARTING_CASH) - 1) * 100

    log.info("Backtest Complete!")
    log.info(f"Starting Balance: ${STARTING_CASH:,.2f}")
    log.info(f"Final Net Worth:  ${final_net_worth:,.2f}")
    log.info(f"Total Return:     {total_return:+.2f}%")

    # Generate report
    visualizer.generate_report()

    # Optional: Save snapshot
    snapshot = {
        "final_balance": final_net_worth,
        "symbols_traded": list(historical_data.keys()),
        "timestamp": datetime.now().isoformat()
    }
    with open("backtest_snapshot.json", "w") as f:
        import json
        json.dump(snapshot, f, indent=4)
    log.info("Snapshot saved to backtest_snapshot.json")

if __name__ == "__main__":
    run_backtest()
