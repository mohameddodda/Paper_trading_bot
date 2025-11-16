"""
train_rl.py – Lightweight RL Training (No Ray, No GPU)
======================================================

Trains a PPO agent using **Stable-Baselines3** (lightweight, iOS-compatible).
Uses **Crypto.com public API** -- no key needed.
Designed for **educational simulation only**.

Author: @MohamedDodda
Last updated: November 15, 2025
"""

import os
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

from config import (
    SYMBOLS,
    WINDOW_SIZE,
    RL_CHECKPOINT_PATH,
    STARTING_CASH,
)
from rl_environment import RLTradingEnv

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# === Paths ===
CHECKPOINT_DIR = Path(RL_CHECKPOINT_PATH).parent
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


class SaveBestCallback(BaseCallback):
    """Save model on best reward."""
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.best_reward = -np.inf

    def _on_step(self) -> bool:
        if self.num_timesteps % 10_000 == 0:
            mean_reward = np.mean([ep['r'] for ep in self.model.ep_info_buffer])
            if mean_reward > self.best_reward:
                self.best_reward = mean_reward
                path = CHECKPOINT_DIR / "best_model"
                self.model.save(path)
                log.info(f"New best model saved: {mean_reward:+.2f} reward")
        return True


def train_rl_agent(
    symbol: str = "BTC_USDT",
    total_timesteps: int = 50_000,
    window_size: int = WINDOW_SIZE,
) -> PPO:
    """Train PPO agent on live Crypto.com data."""
    if symbol not in SYMBOLS:
        raise ValueError(f"Symbol {symbol} not in config.SYMBOLS")

    log.info(f"Starting RL training: {symbol}, {total_timesteps:,} timesteps")

    # === Environment ===
    env = RLTradingEnv(symbol=symbol, window_size=window_size)

    # === Model ===
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=128,
        batch_size=64,
        n_epochs=4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        tensorboard_log="./tb_logs/",
        device="cpu",  # iOS only
    )

    # === Callback ===
    callback = SaveBestCallback()

    # === Train ===
    model.learn(total_timesteps=total_timesteps, callback=callback)

    # === Save Final ===
    final_path = CHECKPOINT_DIR / "latest"
    model.save(final_path)
    log.info(f"Final model saved: {final_path}")

    return model


if __name__ == "__main__":
    # Use first symbol by default
    train_rl_agent(symbol=SYMBOLS[0], total_timesteps=50_000)