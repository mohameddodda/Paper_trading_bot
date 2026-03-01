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

#!/usr/bin/env python3
"""
test_live.py – Live Trading Testing Script
========================================

Tests live trading functionality without real money.
For educational paper trading simulations only.
Uses public APIs - no real money involved.

Author: @MohamedDodda
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SYMBOLS, STARTING_CASH, UPDATE_INTERVAL, CRYPTO_MODE, STOCK_MODE
from core import fetch_all_prices, get_live_price

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)

def test_price_fetching():
    """Test fetching live prices."""
    print("\n" + "="*50)
    print("TEST 1: Price Fetching")
    print("="*50)
    
    prices = fetch_all_prices()
    
    if prices:
        print(f"✅ Successfully fetched {len(prices)} prices:")
        for sym, price in prices.items():
            print(f"   {sym}: ${price:,.4f}")
    else:
        print("❌ Failed to fetch prices")
    
    return bool(prices)

def test_single_symbol(symbol: str):
    """Test fetching price for a single symbol."""
    print(f"\nTesting single symbol: {symbol}")
    price = get_live_price(symbol)
    
    if price:
        print(f"✅ {symbol}: ${price:,.4f}")
        return True
    else:
        print(f"❌ Failed to fetch {symbol}")
        return False

def test_portfolio_simulation():
    """Test portfolio simulation logic."""
    print("\n" + "="*50)
    print("TEST 2: Portfolio Simulation")
    print("="*50)
    
    # Simulate portfolio
    portfolio = {
        'BTC_USDT': 0.5,
        'ETH_USDT': 2.0,
    }
    balance = 100000.0
    
    prices = fetch_all_prices()
    if not prices:
        print("❌ Cannot test portfolio - no prices")
        return False
    
    total_value = balance
    for sym, qty in portfolio.items():
        price = prices.get(sym, 0)
        value = qty * price
        total_value += value
        print(f"   {sym}: {qty} @ ${price:,.2f} = ${value:,.2f}")
    
    print(f"\n💰 Total Portfolio Value: ${total_value:,.2f}")
    print(f"   Cash: ${balance:,.2f}")
    print(f"   Assets: ${total_value - balance:,.2f}")
    
    return True

def test_trading_signals():
    """Test trading signal generation."""
    print("\n" + "="*50)
    print("TEST 3: Trading Signals")
    print("="*50)
    
    from core import moving_average_crossover
    import pandas as pd
    
    # Create sample price data
    prices = [100 + i + (i % 10) for i in range(50)]
    df = pd.DataFrame({'Close': prices})
    
    signals = moving_average_crossover(df)
    
    print(f"Generated {len(signals)} signals")
    print(f"Last signal: {signals.iloc[-1] if not signals.empty else 'N/A'}")
    
    return True

def test_backtest_compatibility():
    """Test backtest compatibility."""
    print("\n" + "="*50)
    print("TEST 4: Backtest Compatibility")
    print("="*50)
    
    from core import backtest_strategy
    import pandas as pd
    import numpy as np
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'Close': 100 + np.cumsum(np.random.randn(100) * 2)
    }, index=dates)
    df['Open'] = df['Close'] * 0.99
    df['High'] = df['Close'] * 1.02
    df['Low'] = df['Close'] * 0.98
    df['Volume'] = 1000000
    
    # Simple signal
    signals = pd.DataFrame({
        'signal': [0] * 50 + [1] * 50
    }, index=df.index[:100])
    
    result = backtest_strategy(df, signals, 100000)
    
    if not result.empty:
        print(f"✅ Backtest completed: {len(result)} periods")
        print(f"   Final value: ${result['total'].iloc[-1]:,.2f}")
        return True
    else:
        print("❌ Backtest failed")
        return False

def run_live_tests():
    """Run all live tests."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         Paper Trading Bot - Live Tests                   ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Testing live functionality with paper trading           ║
    ║  WARNING: Paper trading simulation only!                   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Test 1: Price fetching
    results['price_fetch'] = test_price_fetching()
    
    # Test 2: Single symbol
    if SYMBOLS:
        results['single_symbol'] = test_single_symbol(SYMBOLS[0])
    
    # Test 3: Portfolio simulation
    results['portfolio'] = test_portfolio_simulation()
    
    # Test 4: Trading signals
    results['signals'] = test_trading_signals()
    
    # Test 5: Backtest compatibility
    results['backtest'] = test_backtest_compatibility()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = run_live_tests()
    sys.exit(0 if success else 1)
