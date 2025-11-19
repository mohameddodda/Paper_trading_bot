"""
config.py – Paper Trading Bot Configuration
==========================================

WARNING: This file contains defaults only.
         NEVER commit real API keys!

All secrets are loaded from .env (gitignored)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    API_KEY = os.getenv('YAHOO_API_KEY', 'default_key')
    DEFAULT_SYMBOL = 'AAPL'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# === PROJECT ROOT (for checkpoints, logs, etc.) ===
PROJECT_ROOT = Path(__file__).parent.resolve()

# === API KEYS & SECRETS ===
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("sk-or-"):
    raise ValueError(
        "OPENROUTER_API_KEY is missing or invalid! "
        "Get it from https://openrouter.ai/keys and add to .env"
    )

# === SIMULATION SETTINGS ===
STARTING_CASH = 1_000_000.0  # $1M virtual balance
UPDATE_INTERVAL = 10  # seconds between market checks

# === CRYPTO.COM SYMBOLS (8 major pairs) ===
SYMBOLS = [
    "BTC_USDT",
    "ETH_USDT",
    "SOL_USDT",
    "DOGE_USDT",
    "SHIB_USDT",
    "CRO_USDT",
    "XRP_USDT",  # New
    "ADA_USDT",  # New
]

# === AI & SIGNAL SETTINGS ===
AI_MODEL = "deepseek/deepseek-chat"
AI_TEMPERATURE = 0.3
AI_MAX_TOKENS = 300

# === RISK & TRADING LOGIC ===
RISK_PER_TRADE = 0.03  # 3% of balance per trade
STOP_LOSS_PCT = 0.05   # 5% stop-loss
TAKE_PROFIT_PCT = 0.10 # 10% take-profit
VOLATILITY_THRESHOLD = 0.02  # 2% price move triggers AI re-evaluation

# === REINFORCEMENT LEARNING (Optional) ===
USE_RL = False
RL_CHECKPOINT_PATH = PROJECT_ROOT / "checkpoints" / "PPO" / "latest"
RL_TRAINING = False

# === BACKTESTING ===
BACKTEST_DAYS = 90
AGGREGATE_SIZE = "1"
AGGREGATE_UNIT = "minute"

# === LOGGING & OUTPUT ===
LOG_LEVEL = "INFO"
LOG_FILE = PROJECT_ROOT / "paper_trading.log"
CSV_LOG_FILE = PROJECT_ROOT / "trades.csv"
PERFORMANCE_CHART = PROJECT_ROOT / "performance.png"

# === iOS / Pythonista Compatibility ===
VOICE_ALERTS = True  # Uses `speech` module
PUSH_NOTIFICATIONS = True  # Uses `notification` module
KEYCHAIN_SERVICE = "PaperTradingBot"  # Stores API key securely

# === DEBUG & DEV ===
DEBUG_MODE = False
MOCK_AI = False  # For testing without API calls

# === FINAL CHECK ===
if DEBUG_MODE:
    print(f"[CONFIG] Loaded {len(SYMBOLS)} symbols, starting with ${STARTING_CASH:,.0f}")