# Paper Trading Bot – Pro Edition

![Deploy: Ready](https://img.shields.io/badge/Deploy-Ready-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellowgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platforms](https://img.shields.io/badge/Platforms-PC%20•%20Mac%20•%20Linux%20•%20iOS-success)
![Status](https://img.shields.io/badge/Status-PRO%20LIVE-00d4aa)
![Simulation Only](https://img.shields.io/badge/Simulation-Only-red)

**AI-Powered Paper Trading Platform**  
**$1,000,000 virtual balance** • Live market prices (Stocks or Crypto) • Zero financial risk

Runs natively on **PC / Mac / Linux** (full power) **and** **iPhone / iPad** (Pythonista 3) — from the same repo.

**Pythonista 3** • **OpenRouter** • **Yahoo Finance / Crypto.com APIs** • **Mistral + DeepSeek AI**

## Pro Edition Launched — 2026

| Feature                            | PC / Mac / Linux | iPhone / iPad (Pythonista 3) |
|------------------------------------|------------------|------------------------------|
| Live Crypto.com prices (8+ pairs)  | Yes              | Yes                          |
| Live Stock prices (Yahoo Finance)   | Yes              | Yes                          |
| AI signals (OpenRouter)            | Yes              | Yes                          |
| Dynamic risk & volatility sizing   | Yes              | Yes                          |
| LSTM + Reinforcement Learning      | Yes (ready)      | No (PC only)                 |
| QuantStats HTML reports            | Yes              | No (PC only)                 |
| Live Streamlit dashboard           | Yes              | No (PC only)                 |
| Professional CSV logging           | Yes              | Yes                          |
| Backtesting & Monte Carlo          | Yes              | No (PC only)                 |
| Push + voice alerts                | Yes              | Yes (iOS native)             |
| Auto-trading (toggle)              | Yes              | Planned                      |

## Supported Assets

### Stocks (Yahoo Finance)
AAPL • GOOGL • MSFT • TSLA

### Crypto (Crypto.com API)
BTC_USDT • ETH_USDT • SOL_USDT • DOGE_USDT • SHIB_USDT • CRO_USDT • XRP_USDT • ADA_USDT

> **100% simulation. Zero real money. Zero risk.**

## Quick Start

1. Clone the repo: `git clone https://github.com/mohameddodda/Paper_trading_bot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment: Copy `.env.example` to `.env` and add your OpenRouter API key.
4. Run the bot: `python bot.py`

## Installation

```
bash
# Clone the repository
git clone https://github.com/mohameddodda/Paper_trading_bot.git
cd Paper_trading_bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key (optional - for AI signals)
# Windows:
set OPENROUTER_API_KEY=sk-or-v1-...
# Mac/Linux:
export OPENROUTER_API_KEY=sk-or-v1-...
```

## Usage

### PC / Mac / Linux - Modular Version (Recommended)
```
bash
python bot.py
```

### PC / Mac / Linux - Standalone Version
```
bash
python Paper_Trading_bot.py
```

### iPhone / iPad (Pythonista 3)
1. Open Pythonista 3 on your iOS device
2. Tap + → Import from GitHub
3. Enter: `mohameddodda/Paper_trading_bot`
4. Run `pythonista_ios_mode.py`

### Commands
- `start` → Begin/resume trading
- `stop` → Pause bot
- `reset` → Reset to $1,000,000
- `status` → Show current balance
- `report` → Generate QuantStats report (PC only)
- `exit` → Exit the bot

## Project Structure

```
Paper_Trading_Bot/
├── bot.py                      # Main modular version (recommended)
├── Paper_Trading_bot.py        # Standalone version
├── pythonista_ios_mode.py      # iOS/Pythonista version
├── backtest.py                 # Historical backtesting
├── config.py                   # Configuration settings
├── src/                        # Core modules
│   ├── __init__.py
│   ├── data_fetcher.py        # Market data fetching
│   ├── strategy.py            # Trading strategies
│   └── backtester.py          # Backtesting engine
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Configuration

Edit `config.py` for settings:

```
python
STOCK_MODE = True       # Set to True for stocks, False for crypto
USE_AI = True          # Enable AI signals via OpenRouter
STARTING_CASH = 1_000_000  # Virtual balance
RISK_PER_TRADE = 0.03  # 3% risk per trade
STOP_LOSS_PCT = 0.05   # 5% stop loss
TAKE_PROFIT_PCT = 0.10 # 10% take profit
```

## Features

### Trading Strategies
- Moving Average Crossover
- RSI (Relative Strength Index)
- Bollinger Bands
- MACD (Moving Average Convergence Divergence)
- AI-powered signals (DeepSeek via OpenRouter)

### Risk Management
- Dynamic position sizing based on volatility
- Stop-loss and take-profit orders
- Maximum drawdown protection
- Cooldown between trades

### Reporting
- CSV trade logging
- QuantStats HTML performance reports
- Real-time portfolio tracking

## Testing

```
bash
# Run tests
python -m pytest tests/

# Run specific test
python tests/test_bot.py
```

## Dependencies

### Core
- pandas, numpy, matplotlib
- yfinance (stock prices)
- requests (API calls)
- quantstats (reporting)

### Optional (for advanced features)
- tensorflow (LSTM AI)
- stable-baselines3 (RL trading)
- streamlit (dashboard)
- websocket-client (real-time)

See `requirements.txt` for full list.

## Troubleshooting

- **API Errors**: Check `.env` for valid OpenRouter API key
- **Import Errors**: Ensure virtual environment is activated
- **iOS Issues**: Use Pythonista 3 for iOS, not regular Python
- **Performance**: For large backtests, use PC/Mac

## Legal & Compliance

⚠️ **Important Disclaimers:**
- **100% Paper Trading Simulation**: No real money, trades, or financial risk
- **Not Financial Advice**: This bot does not provide investment recommendations
- **No Affiliations**: Not affiliated with Yahoo Finance, Crypto.com, OpenRouter, or any exchanges
- **Educational Purpose Only**: For learning and research

## Author

Made with ❤️ by [@MohamedDodda](https://mohameddodda.github.io/)  
Pro Edition Updated: 2025  
GitHub: https://github.com/mohameddodda/Paper_trading_bot
