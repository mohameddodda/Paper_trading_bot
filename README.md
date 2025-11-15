# Paper Trading Bot

**AI-Powered Crypto Strategy Simulator** – Practice before real money.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
![iOS](https://img.shields.io/badge/iOS-000000?style=flat&logo=apple&logoColor=white)

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
| Real-time price updates  | ✅Done |
| Dynamic volatility thresholds | ✅Done |
| AI trade signals         | ✅Done |
| **Auto buy/sell (AI-driven)** | ⏳Planned |
| Push notifications       | ✅Done |
| CSV trade log            | ✅Done |
| Force buy/sell commands  | ✅Done |
| Console UI with charts   | ✅Done |

—

## Coming Soon

- **Auto Buy/Sell**: Fully automated AI trading (toggle on/off)
- **PC Version (Basic)**: Simple desktop runner (Python script)

—

## Setup (iOS)

1. Install **Pythonista 3** from the App Store
2. Copy `bot.py` into Pythonista
3. Run → type `start` in console
4. Watch AI signals and simulated trades

—

## Commands

```bash
start          # Resume bot
stop           # Pause bot
reset          # Reset balance & portfolio
force buy BTC  # Buy 10% of balance
force sell BTC # Sell all holdings

-

## Tech Stack

•  Pythonista 3 (iOS)
•  Crypto.com Public API
•  OpenRouter (deepseek/deepseek-chat:free)
•  GitHub Pages (referer for OpenRouter)