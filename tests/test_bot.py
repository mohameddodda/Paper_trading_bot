import matplotlib.pyplot as plt
import numpy as np
from config import STARTING_CASH
import json
import os

def load_portfolio_history():
    # Simulate or load from logs later
    return {"USD": STARTING_CASH, "BTC_USD": 0.1, "ETH_USD": 0.5}

def calculate_metrics(portfolio):
    # Placeholder -- expand with real history
    returns = [0.05, -0.02, 0.08, 0.03]
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if returns else 0
    return {"sharpe": round(sharpe, 2), "returns": returns}

def plot_performance():
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

if __name__ == "__main__":
    plot_performance()