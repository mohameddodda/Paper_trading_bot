import os
from dotenv import load_dotenv

load_dotenv()

# === API & ENV ===
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "YOUR_API_KEY_HERE")
STARTING_CASH = 10_000.0

# === BOT SETTINGS ===
UPDATE_INTERVAL = 10  # seconds
SYMBOLS = ["BTC_USD", "ETH_USD", "SOL_USD", "DOGE_USD", "SHIB_USD", "CRO_USD"]
WINDOW_SIZE = 20  # for RL & indicators
USE_RL = False  # Toggle RL mode
RL_CHECKPOINT_PATH = "checkpoints/PPO/latest"

# === BACKTESTING ===
BACKTEST_DAYS = 90
AGGREGATE_SIZE = "1"
AGGREGATE_UNIT = "minute"

# === LOGGING ===
LOG_LEVEL = "INFO"