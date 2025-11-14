# Paper Trading Bot

A **paper trading bot** for iOS (Pythonista 3) that monitors crypto prices from **Crypto.com**, makes simulated buys/sells, and uses **AI (DeepSeek via OpenRouter)** for trade signals.

---

## Features
- Real-time price tracking (BTC, ETH, SOL, DOGE, SHIB, CRO)
- Paper trading with $1,000,000 virtual balance
- Dynamic buy/sell thresholds based on volatility
- AI-powered trade suggestions (BUY/SELL/HOLD)
- CSV trade logging
- Console UI with price charts
- Push notifications on trades
- Manual force buy/sell via commands

---

## Tech Stack
- **Pythonista 3** (iOS)
- **Crypto.com Public API**
- **OpenRouter AI** (`deepseek/deepseek-chat:free`)
- **GitHub Pages** (for OpenRouter referer)

---

## Commands
| Command | Action |
|--------|--------|
| `start` | Resume bot |
| `stop`  | Pause bot |
| `reset` | Reset balance & portfolio |
| `force buy BTC` | Buy 10% of balance |
| `force sell BTC` | Sell all holdings |

---

## Setup
1. Run in **Pythonista 3**
2. Enable **GitHub Pages** on this repo
3. Use URL: `https://mohameddodda.github.io/Paper_trading_bot/`

---

> **Note**: This is a simulation — no real money is traded.