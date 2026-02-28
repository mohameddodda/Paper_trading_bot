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

## Pro Edition Launched — Updated for 2024

| Feature                            | PC / Mac / Linux | iPhone / iPad (Pythonista 3) |
|------------------------------------|------------------|------------------------------|
| Live Crypto.com prices (8+ pairs)  | Yes              | Yes                          |
| AI signals (OpenRouter)            | Yes              | Yes                          |
| Dynamic risk & volatility sizing   | Yes              | Yes                          |
| LSTM + Reinforcement Learning      | Yes (ready)      | No (PC only)                 |
| QuantStats HTML reports            | Yes              | No (PC only)                 |
| Live Streamlit dashboard           | Yes              | No (PC only)                 |
| Professional CSV logging           | Yes              | Yes                          |
| Backtesting & Monte Carlo          | Yes              | No (PC only)                 |
| Push + voice alerts                | Yes              | Yes                          |
| Auto-trading (toggle)              | Yes              | Planned                      |

## Supported Assets

# Stocks (Yahoo Finance)
AAPL • GOOGL • MSFT • TSLA

# Crypto (Crypto.com API)
BTC_USDT • ETH_USDT • SOL_USDT • DOGE_USDT • SHIB_USDT • CRO_USDT • XRP_USDT • ADA_USDT

> **100% simulation. Zero real money. Zero risk.**

## Table of Contents
Quick Start
Installation
Usage
Configuration
Testing
Contributing
Troubleshooting
Legal & Compliance

## Quick Start

1. Clone the repo: git clone https://github.com/mohameddodda/Paper_trading_bot.git
2. Install dependencies: pip install -r requirements.txt
3. Set up environment: Copy .env.example to .env and add your OpenRouter API key.
4. Run the bot: python src/bot.py (or python bot.py if in root).

## Installation
1. Clone: git clone https://github.com/mohameddodda/Paper_trading_bot.git
2. Navigate: cd Paper_trading_bot
3. Virtual Environment: python -m venv venv then activate (venv\Scripts\activate on Windows, source venv/bin/activate on Mac/Linux).
4. Install: pip install -r requirements.txt
5. Environment: Create .env file with your API keys (see .env.example).

## Dependencies
Core: pandas, numpy, matplotlib, yfinance, requests
AI: python-dotenv
Dev: pytest, black, etc. (see requirements.txt)

## Usage
Run: python src/bot.py
Commands (in interactive mode):
    start → Begin/resume trading
    stop → Pause bot
    reset → Reset to $1,000,000
    report → Generate QuantStats report (PC only)
Output: Logs to bot_logs/, CSV to trades.csv, chart to performance.png.


### PC / Mac / Linux (Recommended – Full Pro Power)
```bash
git clone https://github.com/mohameddodda/Paper_trading_bot.git
cd Paper_trading_bot
pip install -r requirements.txt
# Set API key:
# Windows: set OPENROUTER_API_KEY=sk-or-v1-...
# Mac/Linux: export OPENROUTER_API_KEY=sk-or-v1-...
python src/bot.py
```

## iPhone / iPad (Pythonista 3 – Lightweight Mode)
Open Pythonista → + → Import from GitHub
Enter: mohameddodda/Paper_trading_bot
Run pythonista_ios_mode.py → type start

Both versions use the same $1M virtual balance and live market data.

## Configuration
Edit config.py or config.yaml for settings:

    Toggle STOCK_MODE or stock_mode for stocks vs. crypto.
    Adjust risk params (e.g., RISK_PER_TRADE).
    Enable/disable AI with USE_AI. See files for full options.

## Testing
Run tests: python -m pytest tests/ Add tests for new features in tests/.

## Contributing
1. Fork the repo.
2. Create a branch: git checkout -b feature-name
3. Commit changes: git commit -m "Add feature"
4. Push and PR.

## Troubleshooting
API Errors: Check .env for valid keys.
Import Errors: Ensure venv is activated and deps installed.
Platform Issues: iOS features (voice/push) may not work on non-iOS.
Performance: For large backtests, use PC/Mac.
Open an issue on GitHub for help.

## Legal & Compliance
100% Paper Trading Simulation: No real money, trades, or financial risk. For educational purposes only.
Not Financial Advice: This bot does not provide investment recommendations. Past performance does not predict future results.
No Affiliations: Not affiliated with Yahoo Finance, Crypto.com, OpenRouter, or any exchanges.
Open-Source: Licensed under MIT. Free to use, modify, and distribute.
Compliance: Uses public APIs responsibly. No data scraping or unauthorized access.

## Author
Made with ❤️ by @MohamedDodda
Pro Edition Updated: 2024
GitHub: https://github.com/mohameddodda/Paper_trading_bot
Live Site: https://mohameddodda.github.io/Paper_trading_bot/ (if deployed)