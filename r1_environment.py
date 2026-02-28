"""
rl_environment.py – Reinforcement Learning Environment
======================================================

Gymnasium-compatible environment for training RL agents.
Uses public APIs (e.g., Crypto.com or Yahoo Finance) -- no keys needed.
For educational paper trading simulations only—NO REAL TRADING.

Author: @MohamedDodda
Last updated: 2025 (aligned with project)
"""

import logging
import numpy as np
import gymnasium as gym
from typing import Dict, Any, Tuple

from config import (
    SYMBOLS,
    STARTING_CASH,
    CRYPTO_MODE,
    STOCK_MODE,
)
from data_fetcher import get_live_price  # For live prices
from bot import PortfolioManager  # Use modular classes from bot.py

# === Logging ===
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# === Price Fetching (Public APIs, No Keys) ===
def _fetch_latest_price(symbol: str) -> float:
    """Fetch latest price from public APIs."""
    try:
        if CRYPTO_MODE:
            # Use Crypto.com public API
            import requests
            instrument = symbol.replace("_", "-")
            url = "https://api.crypto.com/v2/public/get-ticker"
            params = {"instrument_name": instrument}
            resp = requests.get(url, params=params, timeout=8)
            data = resp.json()
            if data.get("code") == 0 and data.get("result", {}).get("data"):
                return float(data["result"]["data"][0]["a"])  # Last ask price
        elif STOCK_MODE:
            # Use yfinance via data_fetcher.py
            return get_live_price(symbol)
        return 0.0
    except Exception as e:
        log.debug(f"Price fetch failed for {symbol}: {e}")
        return 0.0


class RLTradingEnv(gym.Env):
    """
    Gymnasium environment for RL training.
    - Observation: Last N prices (normalized to 0-1)
    - Action: 0=hold, 1=buy 3%, 2=sell 3%
    - Reward: PnL change (normalized)
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, symbol: str = SYMBOLS[0] if SYMBOLS else "BTC_USDT", window_size: int = 60):
        super().__init__()
        if symbol not in SYMBOLS:
            raise ValueError(f"Symbol {symbol} not in config.SYMBOLS")

        self.symbol = symbol
        self.window_size = window_size
        self.portfolio = PortfolioManager()  # From bot.py
        self.price_history = []

        # === Spaces ===
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(window_size,), dtype=np.float32  # Normalized
        )
        self.action_space = gym.spaces.Discrete(3)  # 0=hold, 1=buy, 2=sell

        self.current_step = 0
        self.max_steps = 1000  # Prevent infinite loops
        self.initial_cash = STARTING_CASH

    def reset(self, seed=None, options=None) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)
        self.portfolio.__init__()  # Reset portfolio
        self.price_history = []
        self.current_step = 0

        # Seed with initial prices
        base_price = _fetch_latest_price(self.symbol) or 30000.0
        self.price_history = [base_price] * self.window_size  # Start with flat history

        obs = self._get_observation()
        return obs, {}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        if action not in [0, 1, 2]:
            raise ValueError("Action must be 0, 1, or 2")

        prev_net_worth = self.portfolio.get_total_value({self.symbol: self.price_history[-1]})

        # === Execute Action ===
        current_price = self.price_history[-1]
        if action == 1:  # Buy 3%
            usd_to_buy = self.portfolio.sim_balance * 0.03
            if usd_to_buy > 0:
                coins = usd_to_buy / current_price
                self.portfolio.portfolio[self.symbol] = self.portfolio.portfolio.get(self.symbol, 0) + coins
                self.portfolio.sim_balance -= usd_to_buy
        elif action == 2:  # Sell 3%
            coins_to_sell = self.portfolio.portfolio.get(self.symbol, 0) * 0.03
            if coins_to_sell > 0:
                usd = coins_to_sell * current_price
                self.portfolio.portfolio[self.symbol] -= coins_to_sell
                self.portfolio.sim_balance += usd

        # === Update Price ===
        new_price = _fetch_latest_price(self.symbol)
        if new_price > 0:
            self.price_history.append(new_price)
            if len(self.price_history) > self.window_size:
                self.price_history.pop(0)

        # === Reward ===
        current_net_worth = self.portfolio.get_total_value({self.symbol: self.price_history[-1]})
        reward = (current_net_worth - prev_net_worth) / self.initial_cash  # Normalized

        # === Done ===
        self.current_step += 1
        done = self.current_step >= self.max_steps or self.portfolio.sim_balance <= 0

        obs = self._get_observation()
        info = {
            "net_worth": current_net_worth,
            "cash": self.portfolio.sim_balance,
            "holdings": self.portfolio.portfolio.get(self.symbol, 0),
            "price": self.price_history[-1],
        }

        return obs, reward, done, False, info

    def _get_observation(self) -> np.ndarray:
        if len(self.price_history) < self.window_size:
            prices = [self.price_history[0]] * (self.window_size - len(self.price_history)) + self.price_history
        else:
            prices = self.price_history[-self.window_size:]
        # Normalize to 0-1
        min_price = min(prices)
        max_price = max(prices)
        if max_price > min_price:
            normalized = [(p - min_price) / (max_price - min_price) for p in prices]
        else:
            normalized = [0.5] * len(prices)  # Flat if no variation
        return np.array(normalized, dtype=np.float32)

    def render(self, mode="human"):
        nw = self.portfolio.get_total_value({self.symbol: self.price_history[-1]})
        print(f"Step: {self.current_step} | Net Worth: ${nw:,.2f} | "
              f"Cash: ${self.portfolio.sim_balance:,.0f} | "
              f"{self.symbol}: {self.portfolio.portfolio.get(self.symbol, 0):.6f}")

    def close(self):
        pass