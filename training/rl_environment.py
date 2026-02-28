#!/usr/bin/env python3
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

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SYMBOLS,
    STARTING_CASH,
    CRYPTO_MODE,
    STOCK_MODE,
)
from core import get_live_price, DataFetcher

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
            # Use yfinance via core data_fetcher
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
        self.portfolio = {
            'cash': STARTING_CASH,
            'holdings': 0.0
        }
        self.price_history = []
        self.initial_cash = STARTING_CASH

        # === Spaces ===
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(window_size,), dtype=np.float32
        )
        self.action_space = gym.spaces.Discrete(3)  # 0=hold, 1=buy, 2=sell

        # === Tracking ===
        self.current_step = 0
        self.max_steps = 1000

    def reset(self, seed=None, options=None):
        """Reset the environment."""
        super().reset(seed=seed)
        
        self.portfolio = {
            'cash': self.initial_cash,
            'holdings': 0.0
        }
        self.price_history = []
        self.current_step = 0
        
        # Initialize with some prices
        for _ in range(self.window_size):
            price = _fetch_latest_price(self.symbol)
            if price > 0:
                self.price_history.append(price)
            else:
                self.price_history.append(100.0)  # Default fallback
        
        obs = self._get_observation()
        info = {}
        
        return obs, info

    def step(self, action: int):
        """Execute one step."""
        self.current_step += 1
        
        current_price = self.price_history[-1] if self.price_history else 0
        
        # Calculate net worth before action
        prev_net_worth = self.portfolio['cash'] + self.portfolio['holdings'] * current_price
        
        # === Execute Action ===
        if action == 1:  # Buy 3%
            usd_to_buy = self.portfolio['cash'] * 0.03
            if usd_to_buy > 10:
                coins = usd_to_buy / current_price
                self.portfolio['holdings'] = self.portfolio['holdings'] + coins
                self.portfolio['cash'] -= usd_to_buy
        elif action == 2:  # Sell 3%
            coins_to_sell = self.portfolio['holdings'] * 0.03
            if coins_to_sell > 0:
                usd = coins_to_sell * current_price
                self.portfolio['holdings'] -= coins_to_sell
                self.portfolio['cash'] += usd

        # === Update Price ===
        new_price = _fetch_latest_price(self.symbol)
        if new_price > 0:
            self.price_history.append(new_price)
            if len(self.price_history) > self.window_size:
                self.price_history.pop(0)

        # === Reward ===
        current_net_worth = self.portfolio['cash'] + self.portfolio['holdings'] * new_price
        reward = (current_net_worth - prev_net_worth) / self.initial_cash  # Normalized

        # === Done ===
        done = self.current_step >= self.max_steps or self.portfolio['cash'] <= 0

        obs = self._get_observation()
        info = {
            "net_worth": current_net_worth,
            "cash": self.portfolio['cash'],
            "holdings": self.portfolio['holdings'],
            "price": new_price,
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
        new_price = self.price_history[-1] if self.price_history else 0
        nw = self.portfolio['cash'] + self.portfolio['holdings'] * new_price
        print(f"Step: {self.current_step} | Net Worth: ${nw:,.2f} | "
              f"Cash: ${self.portfolio['cash']:,.0f} | "
              f"{self.symbol}: {self.portfolio['holdings']:.6f}")

    def close(self):
        pass


# === Example Usage ===
if __name__ == "__main__":
    # Create environment
    env = RLTradingEnv(symbol="BTC_USDT", window_size=60)
    
    # Run a simple episode
    obs, info = env.reset()
    print(f"Initial observation shape: {obs.shape}")
    
    total_reward = 0
    for i in range(100):
        action = env.action_space.sample()  # Random actions
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        
        if i % 20 == 0:
            env.render()
        
        if done:
            break
    
    print(f"\nEpisode complete! Total reward: {total_reward:.4f}")
    env.close()
