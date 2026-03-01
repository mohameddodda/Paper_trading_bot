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
config – Configuration Package
=============================

Contains all configuration settings for the Paper Trading Bot.
Supports multiple config formats: Python, JSON, YAML.

Usage:
    from config import SYMBOLS, STARTING_CASH, CRYPTO_MODE
"""

from .settings import (
    Config,
    PROJECT_ROOT,
    OPENROUTER_API_KEY,
    USE_AI,
    STOCK_MODE,
    CRYPTO_MODE,
    STOCK_SYMBOLS,
    CRYPTO_SYMBOLS,
    SYMBOLS,
    STARTING_CASH,
    UPDATE_INTERVAL,
    AI_MODEL,
    AI_TEMPERATURE,
    AI_MAX_TOKENS,
    RISK_PER_TRADE,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
    VOLATILITY_THRESHOLD,
    USE_RL,
    RL_CHECKPOINT_PATH,
    RL_TRAINING,
    BACKTEST_DAYS,
    AGGREGATE_SIZE,
    AGGREGATE_UNIT,
    LOG_LEVEL,
    LOG_FILE,
    CSV_LOG_FILE,
    PERFORMANCE_CHART,
    VOICE_ALERTS,
    PUSH_NOTIFICATIONS,
    KEYCHAIN_SERVICE,
    DEBUG_MODE,
    MOCK_AI,
)

__version__ = "1.0.0"
__all__ = [
    "Config",
    "PROJECT_ROOT",
    "OPENROUTER_API_KEY",
    "USE_AI",
    "STOCK_MODE",
    "CRYPTO_MODE",
    "STOCK_SYMBOLS",
    "CRYPTO_SYMBOLS",
    "SYMBOLS",
    "STARTING_CASH",
    "UPDATE_INTERVAL",
    "AI_MODEL",
    "AI_TEMPERATURE",
    "AI_MAX_TOKENS",
    "RISK_PER_TRADE",
    "STOP_LOSS_PCT",
    "TAKE_PROFIT_PCT",
    "VOLATILITY_THRESHOLD",
    "USE_RL",
    "RL_CHECKPOINT_PATH",
    "RL_TRAINING",
    "BACKTEST_DAYS",
    "AGGREGATE_SIZE",
    "AGGREGATE_UNIT",
    "LOG_LEVEL",
    "LOG_FILE",
    "CSV_LOG_FILE",
    "PERFORMANCE_CHART",
    "VOICE_ALERTS",
    "PUSH_NOTIFICATIONS",
    "KEYCHAIN_SERVICE",
    "DEBUG_MODE",
    "MOCK_AI",
]
