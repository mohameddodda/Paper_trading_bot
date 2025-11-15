# Paper Trading Bot

**AI-Powered Crypto Strategy Simulator** – Practice before real money.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
![iOS](https://img.shields.io/badge/iOS-000000?style=flat&logo=apple&logoColor=white)
![Security](https://img.shields.io/badge/security-API_key_local-green)
![Safe](https://img.shields.io/badge/safe-no_real_money-blue)
![Simulation](https://img.shields.io/badge/simulation-only-orange)

> **Pythonista 3** • **OpenRouter** • **Crypto.com API**

—

## What It Does

- Monitors live Crypto.com prices (BTC, ETH, SOL, DOGE, SHIB, CRO)
- Uses **DeepSeek AI** (via OpenRouter) to suggest **BUY / SELL / HOLD**
- **Auto-executes AI signals** (optional in future)
- Simulates trades with **$1,000,000 virtual balance**
- Logs every trade to CSV
- Runs **natively on iPhone/iPad** in **Pythonista 3**

**Zero risk – No real money is ever used.**

—

## Features

| Feature                  | Status  |
|—————————|———|
| Real-time price updates  | Done |
| Dynamic volatility thresholds | Done |
| AI trade signals         | Done |
| **Auto buy/sell (AI-driven)** | Planned |
| Push notifications       | Done |
| CSV trade log            | Done |
| Force buy/sell commands  | Done |
| Console UI with charts   | Done |

—

## Coming Soon

- **Auto Buy/Sell**: Fully automated AI trading (toggle on/off)
- **PC Version (Basic)**: Simple desktop runner (Python script)

—

## Setup (iOS)

> **API KEY REQUIRED**  
> You need a **free OpenRouter API key** to get AI trade signals.  
> → Get it at: [openrouter.ai/keys](https://openrouter.ai/keys)

1. Install **Pythonista 3** from the App Store
2. Tap `+` → `Import from GitHub`
3. Enter: `mohameddodda/Paper_trading_bot`
4. Tap **Import**
5. Open `config.py` → paste your OpenRouter API key
6. Run `bot.py` → type `start`

—

## Commands

```bash
start    # Resume bot
stop     # Pause bot
reset    # Reset balance & portfolio
force buy BTC   # Buy 10% of balance
force sell BTC  # Sell all holdings