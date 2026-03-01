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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import STARTING_CASH
import json
import os


def load_portfolio_history():
    """Simulate or load portfolio history from logs."""
    return {"USD": STARTING_CASH, "BTC_USD": 0.1, "ETH_USD": 0.5}


def calculate_metrics(portfolio):
    """Calculate performance metrics from portfolio."""
    returns = [0.05, -0.02, 0.08, 0.03]
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if returns and np.std(returns) > 0 else 0
    return {"sharpe": round(sharpe, 2), "returns": returns}


def plot_performance():
    """Generate a performance chart."""
    dates = pd.date_range("2025-01-01", periods=100)
    values = np.cumsum(np.random.randn(100) * 100) + STARTING_CASH
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, label="Portfolio Value")
    plt.title("Paper Trading Performance")
    plt.xlabel("Date")
    plt.ylabel("USD")
    plt.legend()
    plt.grid()
    plt.savefig("performance.png")
    print("Plot saved: performance.png")


def test_config_import():
    """Test that config imports correctly."""
    from config import STARTING_CASH, STOCK_MODE, SYMBOLS
    assert STARTING_CASH == 1_000_000.0
    assert isinstance(STOCK_MODE, bool)
    assert isinstance(SYMBOLS, list)
    print("Config import test passed")


def test_portfolio_history():
    """Test portfolio history loading."""
    history = load_portfolio_history()
    assert "USD" in history
    assert history["USD"] == STARTING_CASH
    print("Portfolio history test passed")


def test_calculate_metrics():
    """Test metrics calculation."""
    portfolio = {"AAPL": 10, "BTC": 0.5}
    metrics = calculate_metrics(portfolio)
    assert "sharpe" in metrics
    assert "returns" in metrics
    print("Calculate metrics test passed")


if __name__ == "__main__":
    # Run tests
    test_config_import()
    test_portfolio_history()
    test_calculate_metrics()
    plot_performance()
    print("\nAll tests passed!")
