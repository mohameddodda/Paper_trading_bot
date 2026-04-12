# Copyright 2026 Mohamed Dodda - Updated April 2, 2026
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
core - Paper Trading Bot Core Modules
======================================

This package contains the core trading modules:
- data_fetcher: Fetch live prices for stocks and crypto
- strategy: Trading strategies and signals  
- backtester: Historical backtesting functionality
- db_manager: SQLite persistence layer

For educational paper trading simulations only.
"""

# Temporarily disabled data_fetcher import to fix test errors
# from .data_fetcher import (
#     fetch_all_prices, 
#     get_live_price, 
#     fetch_data_for_symbols,
#     clear_cache
# )

from .strategy import (
    moving_average_crossover,
    rsi_signals,
    bollinger_bands_signals,
    macd_signals,
    generate_combined_signal,
    calculate_volatility,
    calculate_momentum,
    get_trend,
    TradingSignals
)
from .backtester import (
    backtest_strategy,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_win_rate,
    calculate_profit_factor,
    generate_backtest_report,
    monte_carlo_backtest,
    BacktestResult
)
from .db_manager import db_manager

__version__ = "3.0.0"

__all__ = [
    # Data fetching
    "fetch_all_prices",
    "get_live_price", 
    "fetch_data_for_symbols",
    "clear_cache",
    # Strategy
    "moving_average_crossover",
    "rsi_signals",
    "bollinger_bands_signals",
    "macd_signals",
    "generate_combined_signal",
    "calculate_volatility",
    "calculate_momentum",
    "get_trend",
    "TradingSignals",
    # Backtesting
    "backtest_strategy",
    "calculate_sharpe_ratio",
    "calculate_sortino_ratio",
    "calculate_max_drawdown",
    "calculate_win_rate",
    "calculate_profit_factor",
    "generate_backtest_report",
    "monte_carlo_backtest",
    "BacktestResult",
    # Database
    "db_manager",
]

