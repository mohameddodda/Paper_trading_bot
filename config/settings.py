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
settings.py – Paper Trading Bot Configuration
==========================================

WARNING: This file contains defaults only.
         NEVER commit real API keys or secrets!
         This bot is for PAPER TRADING SIMULATIONS ONLY.
         Do not use for real financial transactions or live trading.

All secrets are loaded from .env (gitignored).
If .env is missing, defaults are used (but AI features may be disabled).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    """
    Centralized configuration class for easy access.
    """
    API_KEY = os.getenv('YAHOO_API_KEY', 'default_key')  # For yfinance if needed
    DEFAULT_SYMBOL = 'AAPL'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # For AI signals

# === PROJECT ROOT (for checkpoints, logs, etc.) ===
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# === API KEYS & SECRETS ===
# OpenRouter API key for AI-powered signals (optional)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("sk-or-"):
    print("Warning: OPENROUTER_API_KEY is missing or invalid. AI features disabled. Get it from https://openrouter.ai/keys and add to .env")
    USE_AI = False
else:
    USE_AI = True

# === TRADING MODE (Toggle between stocks and crypto) ===
STOCK_MODE = True  # Set to True for stocks (yfinance), False for crypto
CRYPTO_MODE = not STOCK_MODE  # Automatically toggles

# === STOCK SYMBOLS (if STOCK_MODE is True) ===
STOCK_SYMBOLS = [
    "AAPL",      # Apple
    "GOOGL",     # Google
    "MSFT",      # Microsoft
    "TSLA",      # Tesla
]

# === CRYPTO SYMBOLS (if CRYPTO_MODE is True, e.g., for Crypto.com API) ===
CRYPTO_SYMBOLS = [
    "BTC_USDT",
    "ETH_USDT",
    "SOL_USDT",
    "DOGE_USDT",
    "SHIB_USDT",
    "CRO_USDT",
    "XRP_USDT",  # New
    "ADA_USDT",  # New
]

# Use the appropriate symbols based on mode
SYMBOLS = STOCK_SYMBOLS if STOCK_MODE else CRYPTO_SYMBOLS

# WebSocket real-time streaming (Phase 3)
USE_WEBSOCKET = os.getenv('USE_WEBSOCKET', 'false').lower() == 'true'

# === SIMULATION SETTINGS ===
STARTING_CASH = 1_000_000.0  # $1M virtual balance (paper trading only)
UPDATE_INTERVAL = 10  # seconds between market checks

# === AI & SIGNAL SETTINGS (Only if USE_AI is True) ===
AI_MODEL = "deepseek/deepseek-chat"
AI_TEMPERATURE = 0.3
AI_MAX_TOKENS = 300

# === RISK & TRADING LOGIC ===
RISK_PER_TRADE = 0.03  # 3% of balance per trade (e.g., position size)
STOP_LOSS_PCT = 0.05   # 5% stop-loss (sell if price drops 5%)
TAKE_PROFIT_PCT = 0.10 # 10% take-profit (sell if price rises 10%)
VOLATILITY_THRESHOLD = 0.02  # 2% price move triggers AI re-evaluation (if enabled)

# === REINFORCEMENT LEARNING (Optional) ===
USE_RL = False
RL_CHECKPOINT_PATH = PROJECT_ROOT / "checkpoints" / "PPO" / "latest"
RL_TRAINING = False

# === BACKTESTING ===
BACKTEST_DAYS = 90
AGGREGATE_SIZE = "1"
AGGREGATE_UNIT = "minute"  # Ensure this matches data source (e.g., yfinance for stocks)

# === LOGGING & OUTPUT ===
LOG_LEVEL = "INFO"
LOG_FILE = PROJECT_ROOT / "paper_trading.log"
CSV_LOG_FILE = PROJECT_ROOT / "trades.csv"
PERFORMANCE_CHART = PROJECT_ROOT / "performance.png"

# Ensure log directories exist
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# === iOS / Pythonista Compatibility (Optional, platform-aware) ===
VOICE_ALERTS = True  # Uses `speech` module (iOS only; disable on other platforms)
PUSH_NOTIFICATIONS = True  # Uses `notification` module (iOS only)
KEYCHAIN_SERVICE = "PaperTradingBot"  # Stores API key securely (iOS)

# Auto-disable iOS features if not on iOS
import platform
if platform.system() != "iOS":
    VOICE_ALERTS = False
    PUSH_NOTIFICATIONS = False

# === DEBUG & DEV ===
DEBUG_MODE = False
MOCK_AI = False  # For testing without API calls

# === DATABASE ===
DB_PATH = PROJECT_ROOT / "paper_trading.db"

# === FINAL CHECK ===
if DEBUG_MODE:
    print(f"[CONFIG] Loaded {len(SYMBOLS)} symbols in {'Stock' if STOCK_MODE else 'Crypto'} mode, starting with ${STARTING_CASH:,.0f}")
    print(f"[CONFIG] Database: {DB_PATH}")
    if USE_AI:
        print("[CONFIG] AI features enabled.")
    else:
        print("[CONFIG] AI features disabled (no valid API key).")
