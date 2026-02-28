"""
train_rl.py – Lightweight RL Training for AI Signals
=====================================================

Trains a PPO agent using Stable-Baselines3 (lightweight, CPU-compatible).
Uses public APIs (e.g., Crypto.com) -- no keys needed.
For educational paper trading simulations only—NO REAL TRADING.

Author: @MohamedDodda
Last updated: 2025 (aligned with project)
"""

import os
import logging
from datetime import datetime
from pathlib import Path
import numpy as np

# Optional imports (for advanced features)
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.callbacks import BaseCallback
    RL_AVAILABLE = True
except ImportError:
    RL_AVAILABLE = False
    print("Stable-Baselines3 not installed. RL training disabled. Install with: pip install stable-baselines3")

from config import (
    SYMBOLS,
    RL_CHECKPOINT_PATH,
    STARTING_CASH,
    CRYPTO_MODE,
    STOCK_MODE,
)
# Assumes rl_environment.py exists (create if missing)
try:
    from rl_environment import RLTradingEnv
    ENV_AVAILABLE = True
except ImportError:
    ENV_AVAILABLE = False
    print("rl_environment.py not found. Create it or disable RL features.")

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
    symbol: str = SYMBOLS[0] if SYMBOLS else "BTC_USDT",
    total_timesteps: int = 50_000,
    window_size: int = 60,  # Default if not in config
) -> None:
    """Train PPO agent on data (crypto or stock mode)."""
    if not RL_AVAILABLE or not ENV_AVAILABLE:
        log.error("RL dependencies not available. Skipping training.")
        return

    if symbol not in SYMBOLS:
        raise ValueError(f"Symbol {symbol} not in config.SYMBOLS")

    log.info(f"Starting RL training: {symbol}, {total_timesteps:,} timesteps, Mode: {'Crypto' if CRYPTO_MODE else 'Stock'}")

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
        device="cpu",  # CPU-only for iOS compatibility
    )

    # === Callback ===
    callback = SaveBestCallback()

    # === Train ===
    try:
        model.learn(total_timesteps=total_timesteps, callback=callback)
        log.info("RL training completed successfully.")
    except Exception as e:
        log.error(f"RL training failed: {e}")
        return

    # === Save Final ===
    final_path = CHECKPOINT_DIR / "latest"
    model.save(final_path)
    log.info(f"Final model saved: {final_path}")
    print("💡 Load in bot.py's TradingStrategy for RL-enhanced signals!")


if __name__ == "__main__":
    # Use first symbol by default
    if SYMBOLS:
        train_rl_agent(symbol=SYMBOLS[0], total_timesteps=50_000)
    else:
        log.error("No symbols in config.SYMBOLS. Check config.py.")