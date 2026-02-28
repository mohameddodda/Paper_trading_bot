"""
core - Paper Trading Bot Core Modules
======================================

This package contains the core trading modules:
- data_fetcher: Fetch live prices for stocks and crypto
- strategy: Trading strategies and signals  
- backtester: Historical backtesting functionality

For educational paper trading simulations only.
"""

from .data_fetcher import (
    fetch_all_prices, 
    get_live_price, 
    fetch_data_for_symbols,
    clear_cache
)
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
]
