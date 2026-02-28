"""
strategy.py – Trading Strategies Module
=======================================

Implements various trading strategies and signal generation:
- Moving Average Crossover
- RSI-based signals
- Bollinger Bands
- Custom AI-driven signals

For educational paper trading simulations only.
"""

import logging
from typing import List, Optional, Tuple
import pandas as pd
import numpy as np

from config import (
    SYMBOLS,
    STOCK_MODE,
    CRYPTO_MODE,
    LOG_FILE,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    filename=LOG_FILE,
)
log = logging.getLogger(__name__)


def moving_average_crossover(
    data: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 50
) -> pd.Series:
    """
    Generate trading signals using moving average crossover.
    
    Args:
        data: DataFrame with 'Close' price column
        short_window: Short MA period (default 20)
        long_window: Long MA period (default 50)
    
    Returns:
        Series with signals: 1 (buy), -1 (sell), 0 (hold)
    """
    if 'Close' not in data.columns:
        log.error("DataFrame must contain 'Close' column")
        return pd.Series([0] * len(data), index=data.index)
    
    # Calculate moving averages
    short_ma = data['Close'].rolling(window=short_window).mean()
    long_ma = data['Close'].rolling(window=long_window).mean()
    
    # Generate signals
    signals = pd.Series(0, index=data.index)
    signals[short_ma > long_ma] = 1   # Buy signal
    signals[short_ma < long_ma] = -1  # Sell signal
    
    # Signal changes (crossovers)
    signals = signals.diff()
    # First crossover is actual signal
    signals.iloc[0] = 0
    
    return signals


def rsi_signals(
    data: pd.DataFrame,
    period: int = 14,
    overbought: float = 70,
    oversold: float = 30
) -> pd.Series:
    """
    Generate trading signals using RSI (Relative Strength Index).
    
    Args:
        data: DataFrame with 'Close' price column
        period: RSI period (default 14)
        overbought: Overbought threshold (default 70)
        oversold: Oversold threshold (default 30)
    
    Returns:
        Series with signals: 1 (buy), -1 (sell), 0 (hold)
    """
    if 'Close' not in data.columns:
        log.error("DataFrame must contain 'Close' column")
        return pd.Series([0] * len(data), index=data.index)
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Generate signals
    signals = pd.Series(0, index=data.index)
    signals[rsi < oversold] = 1   # Buy when oversold
    signals[rsi > overbought] = -1  # Sell when overbought
    
    return signals


def bollinger_bands_signals(
    data: pd.DataFrame,
    window: int = 20,
    num_std: float = 2.0
) -> pd.Series:
    """
    Generate trading signals using Bollinger Bands.
    
    Args:
        data: DataFrame with 'Close' price column
        window: Moving average window (default 20)
        num_std: Number of standard deviations (default 2.0)
    
    Returns:
        Series with signals: 1 (buy), -1 (sell), 0 (hold)
    """
    if 'Close' not in data.columns:
        log.error("DataFrame must contain 'Close' column")
        return pd.Series([0] * len(data), index=data.index)
    
    # Calculate Bollinger Bands
    middle_band = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    # Generate signals
    signals = pd.Series(0, index=data.index)
    signals[data['Close'] < lower_band] = 1   # Buy at lower band
    signals[data['Close'] > upper_band] = -1   # Sell at upper band
    
    return signals


def macd_signals(
    data: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> pd.Series:
    """
    Generate trading signals using MACD (Moving Average Convergence Divergence).
    
    Args:
        data: DataFrame with 'Close' price column
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line period (default 9)
    
    Returns:
        Series with signals: 1 (buy), -1 (sell), 0 (hold)
    """
    if 'Close' not in data.columns:
        log.error("DataFrame must contain 'Close' column")
        return pd.Series([0] * len(data), index=data.index)
    
    # Calculate MACD
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    
    # Generate signals
    signals = pd.Series(0, index=data.index)
    signals[macd > signal_line] = 1   # Buy when MACD crosses above signal
    signals[macd < signal_line] = -1  # Sell when MACD crosses below signal
    
    return signals


def generate_combined_signal(
    data: pd.DataFrame,
    methods: List[str] = ["ma", "rsi", "bb", "macd"]
) -> int:
    """
    Generate a combined trading signal from multiple strategies.
    
    Args:
        data: DataFrame with OHLC data
        methods: List of methods to use ['ma', 'rsi', 'bb', 'macd']
    
    Returns:
        Final signal: 1 (buy), -1 (sell), 0 (hold)
    """
    signals = []
    weights = []
    
    if "ma" in methods:
        ma_signal = moving_average_crossover(data).iloc[-1] if len(data) > 50 else 0
        signals.append(ma_signal)
        weights.append(0.3)
    
    if "rsi" in methods:
        rsi_signal = rsi_signals(data).iloc[-1]
        signals.append(rsi_signal)
        weights.append(0.25)
    
    if "bb" in methods:
        bb_signal = bollinger_bands_signals(data).iloc[-1]
        signals.append(bb_signal)
        weights.append(0.25)
    
    if "macd" in methods:
        macd_signal = macd_signals(data).iloc[-1]
        signals.append(macd_signal)
        weights.append(0.2)
    
    if not signals:
        return 0
    
    # Weighted average
    weights = np.array(weights[:len(signals)])
    weights = weights / weights.sum()
    
    weighted_signal = sum(s * w for s, w in zip(signals, weights))
    
    # Threshold for final decision
    if weighted_signal > 0.3:
        return 1
    elif weighted_signal < -0.3:
        return -1
    else:
        return 0


def calculate_volatility(
    prices: List[float],
    window: int = 20
) -> float:
    """
    Calculate price volatility.
    
    Args:
        prices: List of historical prices
        window: Window for calculation
    
    Returns:
        Volatility as a decimal
    """
    if len(prices) < 2:
        return 0.01
    
    prices_array = np.array(prices[-window:])
    returns = np.diff(prices_array) / prices_array[:-1]
    
    if len(returns) == 0:
        return 0.01
    
    return float(np.std(returns))


def calculate_momentum(
    prices: List[float],
    period: int = 10
) -> float:
    """
    Calculate price momentum.
    
    Args:
        prices: List of historical prices
        period: Period for momentum calculation
    
    Returns:
        Momentum as percentage
    """
    if len(prices) < period:
        return 0.0
    
    current_price = prices[-1]
    past_price = prices[-period]
    
    if past_price == 0:
        return 0.0
    
    return float((current_price - past_price) / past_price * 100)


def get_trend(
    prices: List[float],
    short_period: int = 10,
    long_period: int = 30
) -> str:
    """
    Determine price trend.
    
    Args:
        prices: List of historical prices
        short_period: Short period for trend
        long_period: Long period for trend
    
    Returns:
        Trend direction: 'up', 'down', or 'sideways'
    """
    if len(prices) < long_period:
        return 'sideways'
    
    short_ma = np.mean(prices[-short_period:])
    long_ma = np.mean(prices[-long_period:])
    
    diff_pct = (short_ma - long_ma) / long_ma * 100
    
    if diff_pct > 1:
        return 'up'
    elif diff_pct < -1:
        return 'down'
    else:
        return 'sideways'
