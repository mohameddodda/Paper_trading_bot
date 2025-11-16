"""
rl_environment.py – Reinforcement Learning Environment
======================================================

Gymnasium-compatible environment for training RL agents.
Uses **Crypto.com public API** (no key needed).
Designed for **simulation only** -- no real trading.

Author: @MohamedDodda
Last updated: November 15, 2025
"""

import logging
import numpy as np
import gymnasium as gym
from typing import Dict, Any, Tuple

from config import (
    SYMBOLS,
    STARTING_CASH,
    WINDOW_SIZE,
)
from bot import PaperTradingBot

# === Logging ===
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# === Crypto.com Public API (No Key) ===
CRYPTOCOM_BASE = "https://api.crypto.com/v2/public"

def _fetch_latest_price(symbol: str) -> float:
    """Fetch latest price from Crypto.com (no API key)."""
    try:
        import requests
        instrument = symbol.replace("_", "-")
        url = f"{CRYPTOCOM_BASE}/get-ticker"
        params = {"instrument_name": instrument}
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        if data.get("code") == 0 and data.get("result", {}).get("data"):
            return float(data["result"]["data"][0]["a"])  # last ask price
        return 0.0
    except Exception as e:
        log.debug(f"Price fetch failed for {symbol}: {e}")
        return 0.0


class RLTradingEnv(gym.Env):
    """
    Gymnasium environment for RL training.
    - Observation: Last N prices (normalized)
    - Action: 0=hold, 1=buy 3%, 2=sell 3%
    - Reward: PnL change
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, symbol: str = "BTC_USDT", window_size: int = WINDOW_SIZE):
        super().__init__()
        if symbol not in SYMBOLS:
            raise ValueError(f"Symbol {symbol} not in config.SYMBOLS")

        self.symbol = symbol
        self.window_size = window_size
        self.bot = PaperTradingBot()
        self.bot.portfolio = {s: 0.0 for s in SYMBOLS}
        self.bot.portfolio["USD"] = STARTING_CASH
        self.bot.history = {s: [] for s in SYMBOLS}

        # === Spaces ===
        self.observation_space = gym.spaces.Box(
            low=0, high=1e10, shape=(window_size,), dtype=np.float32
        )
        self.action_space = gym.spaces.Discrete(3)  # 0=hold, 1=buy, 2=sell

        self.current_step = 0
        self.max_steps = 1000  # Prevent infinite loops
        self.initial_cash = STARTING_CASH

    def reset(self, seed=None, options=None) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)
        self.bot.reset()
        self.current_step = 0

        # Seed with ~20 fake prices
        base_price = _fetch_latest_price(self.symbol) or 30000.0
        prices = np.linspace(base_price * 0.9, base_price * 1.1, self.window_size)
        self.bot.history[self.symbol] = [
            {"timestamp": i, "price": p} for i, p in enumerate(prices)
        ]

        obs = self._get_observation()
        return obs, {}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        if action not in [0, 1, 2]:
            raise ValueError("Action must be 0, 1, or 2")

        prev_net_worth = self.bot.get_net_worth()

        # === Execute Action ===
        if action == 1:  # Buy 3%
            self.bot.execute_trade(self.symbol, "buy", amount_usd=STARTING_CASH * 0.03)
        elif action == 2:  # Sell 3%
            self.bot.execute_trade(self.symbol, "sell", amount_usd=STARTING_CASH * 0.03)

        # === Update Price (Live) ===
        price = _fetch_latest_price(self.symbol)
        if price > 0:
            self.bot.history[self.symbol].append(
                {"timestamp": self.current_step, "price": price}
            )
            # Keep history size
            if len(self.bot.history[self.symbol]) > self.window_size:
                self.bot.history[self.symbol] = self.bot.history[self.symbol][-self.window_size:]

        # === Reward ===
        current_net_worth = self.bot.get_net_worth()
        reward = current_net_worth - prev_net_worth

        # === Done ===
        self.current_step += 1
        done = self.current_step >= self.max_steps or current_net_worth <= 0

        obs = self._get_observation()
        info = {
            "net_worth": current_net_worth,
            "cash": self.bot.portfolio["USD"],
            "holdings": self.bot.portfolio[self.symbol],
            "price": price,
        }

        return obs, reward, done, False, info

    def _get_observation(self) -> np.ndarray:
        prices = [h["price"] for h in self.bot.history[self.symbol]]
        if len(prices) < self.window_size:
            pad = [prices[0]] * (self.window_size - len(prices))
            prices = pad + prices
        else:
            prices = prices[-self.window_size:]
        return np.array(prices, dtype=np.float32)

    def render(self, mode="human"):
        nw = self.bot.get_net_worth()
        print(f"Step: {self.current_step} | Net Worth: ${nw:,.2f} | "
              f"Cash: ${self.bot.portfolio['USD']:,.0f} | "
              f"{self.symbol}: {self.bot.portfolio[self.symbol]:.6f}")

    def close(self):
        pass