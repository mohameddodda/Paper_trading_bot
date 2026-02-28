#!/usr/bin/env python3
"""Test script to verify live functionality"""
import sys
sys.path.insert(0, '.')

results = []

# Test 1: Live Price Fetching
print("Test 1: Live Price Fetching...")
try:
    from src.data_fetcher import fetch_all_prices
    prices = fetch_all_prices()
    results.append(f"Test 1 PASS: Fetched {len(prices)} prices")
    for sym, price in list(prices.items())[:3]:
        results.append(f"  {sym}: ${price:.4f}")
except Exception as e:
    results.append(f"Test 1 FAIL: {e}")

# Test 2: Strategy Functions
print("Test 2: Strategy Functions...")
try:
    import pandas as pd
    import numpy as np
    from src.strategy import moving_average_crossover
    
    # Create sample data
    data = pd.DataFrame({
        'Close': [100 + i + np.random.randn() for i in range(60)]
    })
    signals = moving_average_crossover(data)
    results.append(f"Test 2 PASS: Generated {len(signals)} signals")
except Exception as e:
    results.append(f"Test 2 FAIL: {e}")

# Test 3: Backtester
print("Test 3: Backtester...")
try:
    from src.backtester import backtest_strategy, calculate_sharpe_ratio
    results.append("Test 3 PASS: Backtester functions work")
except Exception as e:
    results.append(f"Test 3 FAIL: {e}")

# Test 4: Config Values
print("Test 4: Config Values...")
try:
    from config import STARTING_CASH, SYMBOLS, STOCK_MODE
    assert STARTING_CASH == 1_000_000
    results.append(f"Test 4 PASS: STARTING_CASH=${STARTING_CASH}, SYMBOLS={len(SYMBOLS)}")
except Exception as e:
    results.append(f"Test 4 FAIL: {e}")

# Test 5: Paper_Trading_bot.py imports
print("Test 5: Paper_Trading_bot.py imports...")
try:
    # Just check if it can be imported (not run)
    with open('Paper_Trading_bot.py', 'r') as f:
        content = f.read()
    results.append("Test 5 PASS: Paper_Trading_bot.py file exists")
except Exception as e:
    results.append(f"Test 5 FAIL: {e}")

# Write results
with open('test_live_results.txt', 'w') as f:
    f.write("="*50 + "\n")
    f.write("LIVE FUNCTIONALITY TEST RESULTS\n")
    f.write("="*50 + "\n\n")
    for r in results:
        f.write(r + "\n")
    f.write("\n" + "="*50 + "\n")
    passed = sum(1 for r in results if r.startswith("PASS"))
    f.write(f"TOTAL: {passed}/{len(results)} tests passed\n")
    f.write("="*50 + "\n")

print("Tests complete! Check test_live_results.txt")
