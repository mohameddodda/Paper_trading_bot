"""
backtester.py – Backtesting Module
==================================

Backtest trading strategies using historical data.
Calculates performance metrics and generates reports.

For educational paper trading simulations only.
"""

import logging
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    STARTING_CASH,
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


def backtest_strategy(
    data: pd.DataFrame,
    signals: pd.Series,
    initial_balance: float = STARTING_CASH,
    position_size: float = 0.1,
    stop_loss: float = 0.05,
    take_profit: float = 0.10
) -> pd.DataFrame:
    """
    Backtest a trading strategy.
    
    Args:
        data: DataFrame with OHLC price data
        signals: Series with trading signals (1=buy, -1=sell, 0=hold)
        initial_balance: Starting capital
        position_size: Fraction of balance per trade (default 10%)
        stop_loss: Stop loss percentage (default 5%)
        take_profit: Take profit percentage (default 10%)
    
    Returns:
        DataFrame with portfolio value over time
    """
    if 'Close' not in data.columns:
        log.error("DataFrame must contain 'Close' column")
        return pd.DataFrame()
    
    if len(signals) != len(data):
        log.error("Signals length must match data length")
        return pd.DataFrame()
    
    # Initialize tracking variables
    balance = initial_balance
    position = 0  # Number of shares/coins held
    entry_price = 0
    trades = []
    
    # Results tracking
    results = []
    
    for i in range(len(data)):
        current_price = data['Close'].iloc[i]
        signal = signals.iloc[i] if i < len(signals) else 0
        
        # Calculate current portfolio value
        portfolio_value = balance + (position * current_price)
        
        # Check stop loss / take profit for existing position
        if position > 0 and entry_price > 0:
            pnl_pct = (current_price - entry_price) / entry_price
            
            if pnl_pct <= -stop_loss:
                # Stop loss triggered
                balance += position * current_price
                trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'qty': position,
                    'pnl_pct': pnl_pct * 100,
                    'reason': 'stop_loss'
                })
                position = 0
                entry_price = 0
                
            elif pnl_pct >= take_profit:
                # Take profit triggered
                balance += position * current_price
                trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'qty': position,
                    'pnl_pct': pnl_pct * 100,
                    'reason': 'take_profit'
                })
                position = 0
                entry_price = 0
        
        # Execute new trades based on signals
        if signal == 1 and position == 0 and balance > 0:
            # Buy signal - enter position
            trade_amount = balance * position_size
            if trade_amount > 0:
                position = trade_amount / current_price
                balance -= trade_amount
                entry_price = current_price
                trades.append({
                    'type': 'BUY',
                    'price': current_price,
                    'qty': position,
                    'pnl_pct': 0,
                    'reason': 'signal'
                })
                
        elif signal == -1 and position > 0:
            # Sell signal - exit position
            balance += position * current_price
            pnl_pct = (current_price - entry_price) / entry_price if entry_price > 0 else 0
            trades.append({
                'type': 'SELL',
                'price': current_price,
                'qty': position,
                'pnl_pct': pnl_pct * 100,
                'reason': 'signal'
            })
            position = 0
            entry_price = 0
        
        # Record portfolio value
        results.append({
            'timestamp': data.index[i] if hasattr(data.index[i], 'strftime') else i,
            'price': current_price,
            'balance': balance,
            'position': position,
            'portfolio_value': balance + (position * current_price)
        })
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Log summary
    if trades:
        buy_trades = [t for t in trades if t['type'] == 'BUY']
        sell_trades = [t for t in trades if t['type'] == 'SELL']
        log.info(f"Backtest complete: {len(buy_trades)} buys, {len(sell_trades)} sells")
        log.info(f"Final balance: ${balance:.2f}")
        log.info(f"Total return: {((balance - initial_balance) / initial_balance * 100):.2f}%")
    
    return results_df


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02
) -> float:
    """
    Calculate Sharpe ratio.
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
    
    Returns:
        Sharpe ratio
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0
    
    # Annualize the return and std
    trading_days = 252
    excess_returns = returns - (risk_free_rate / trading_days)
    
    sharpe = np.sqrt(trading_days) * excess_returns.mean() / returns.std()
    return float(sharpe)


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02
) -> float:
    """
    Calculate Sortino ratio (uses downside deviation).
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
    
    Returns:
        Sortino ratio
    """
    if len(returns) == 0:
        return 0.0
    
    trading_days = 252
    excess_returns = returns - (risk_free_rate / trading_days)
    
    # Downside deviation (only negative returns)
    downside_returns = returns[returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    
    sortino = np.sqrt(trading_days) * excess_returns.mean() / downside_returns.std()
    return float(sortino)


def calculate_max_drawdown(
    equity_curve: pd.Series
) -> float:
    """
    Calculate maximum drawdown.
    
    Args:
        equity_curve: Series of portfolio values
    
    Returns:
        Maximum drawdown as decimal
    """
    if len(equity_curve) == 0:
        return 0.0
    
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    
    return float(abs(drawdown.min()))


def calculate_win_rate(trades: list) -> float:
    """
    Calculate win rate from trades.
    
    Args:
        trades: List of trade dictionaries
    
    Returns:
        Win rate as decimal
    """
    if not trades:
        return 0.0
    
    sell_trades = [t for t in trades if t['type'] == 'SELL' and 'pnl_pct' in t]
    
    if not sell_trades:
        return 0.0
    
    wins = sum(1 for t in sell_trades if t['pnl_pct'] > 0)
    
    return wins / len(sell_trades)


def calculate_profit_factor(trades: list) -> float:
    """
    Calculate profit factor (gross profit / gross loss).
    
    Args:
        trades: List of trade dictionaries
    
    Returns:
        Profit factor
    """
    if not trades:
        return 0.0
    
    sell_trades = [t for t in trades if t['type'] == 'SELL' and 'pnl_pct' in t]
    
    if not sell_trades:
        return 0.0
    
    gross_profit = sum(t['pnl_pct'] for t in sell_trades if t['pnl_pct'] > 0)
    gross_loss = abs(sum(t['pnl_pct'] for t in sell_trades if t['pnl_pct'] < 0))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


def generate_backtest_report(
    results_df: pd.DataFrame,
    trades: list
) -> Dict:
    """
    Generate comprehensive backtest report.
    
    Args:
        results_df: DataFrame from backtest_strategy
        trades: List of trade dictionaries
    
    Returns:
        Dictionary with performance metrics
    """
    if results_df.empty:
        return {}
    
    # Calculate returns
    equity_curve = results_df['portfolio_value']
    returns = equity_curve.pct_change().dropna()
    
    # Calculate metrics
    total_return = (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0]
    sharpe = calculate_sharpe_ratio(returns)
    sortino = calculate_sortino_ratio(returns)
    max_dd = calculate_max_drawdown(equity_curve)
    win_rate = calculate_win_rate(trades)
    profit_factor = calculate_profit_factor(trades)
    
    # Calculate average trade metrics
    sell_trades = [t for t in trades if t['type'] == 'SELL']
    if sell_trades:
        avg_pnl = np.mean([t['pnl_pct'] for t in sell_trades])
    else:
        avg_pnl = 0
    
    report = {
        'initial_balance': STARTING_CASH,
        'final_balance': float(equity_curve.iloc[-1]),
        'total_return_pct': float(total_return * 100),
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown_pct': float(max_dd * 100),
        'win_rate_pct': float(win_rate * 100),
        'profit_factor': profit_factor,
        'total_trades': len(trades),
        'avg_pnl_pct': float(avg_pnl),
    }
    
    return report


def monte_carlo_backtest(
    data: pd.DataFrame,
    signals: pd.Series,
    num_simulations: int = 1000,
    initial_balance: float = STARTING_CASH
) -> Dict:
    """
    Run Monte Carlo simulation for robustness testing.
    
    Args:
        data: DataFrame with price data
        signals: Trading signals
        num_simulations: Number of simulations to run
        initial_balance: Starting capital
    
    Returns:
        Dictionary with simulation results
    """
    results = []
    
    for _ in range(num_simulations):
        # Add random noise to simulate different scenarios
        noise = np.random.normal(0, 0.01, len(data))
        simulated_data = data.copy()
        if 'Close' in simulated_data.columns:
            simulated_returns = simulated_data['Close'].pct_change().fillna(0)
            simulated_data['Close'] = simulated_data['Close'] * (1 + noise)
        
        # Run backtest
        result = backtest_strategy(
            simulated_data,
            signals,
            initial_balance,
            position_size=0.1
        )
        
        if not result.empty:
            final_value = result['portfolio_value'].iloc[-1]
            results.append(final_value)
    
    if not results:
        return {}
    
    results_array = np.array(results)
    
    return {
        'mean_final_value': float(np.mean(results_array)),
        'median_final_value': float(np.median(results_array)),
        'std_final_value': float(np.std(results_array)),
        'min_final_value': float(np.min(results_array)),
        'max_final_value': float(np.max(results_array)),
        'percentile_5': float(np.percentile(results_array, 5)),
        'percentile_95': float(np.percentile(results_array, 95)),
    }


# BacktestResult class for compatibility
class BacktestResult:
    """Container for backtest results."""
    
    def __init__(self, results_df: pd.DataFrame = None, trades: list = None):
        self.results_df = results_df or pd.DataFrame()
        self.trades = trades or []
        self.metrics = {}
        
        if not self.results_df.empty:
            self.metrics = generate_backtest_report(self.results_df, self.trades)
    
    def summary(self) -> str:
        """Get summary string."""
        if not self.metrics:
            return "No results"
        
        return f"""
Backtest Results:
- Total Return: {self.metrics.get('total_return_pct', 0):.2f}%
- Sharpe Ratio: {self.metrics.get('sharpe_ratio', 0):.2f}
- Max Drawdown: {self.metrics.get('max_drawdown_pct', 0):.2f}%
- Win Rate: {self.metrics.get('win_rate_pct', 0):.2f}%
- Total Trades: {self.metrics.get('total_trades', 0)}
"""
