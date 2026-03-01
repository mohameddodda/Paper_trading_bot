# Paper Trading Bot - AI-Powered Crypto/Stock Simulator

<p align="center">
  <img src="assets/bot-running.png" alt="Paper Trading Bot" width="600"/>
</p>

<p align="center">
  <a href="https://github.com/MohamedDodda/Paper_trading_bot/actions/workflows/pages.yml/badge.svg">
    <img src="https://github.com/MohamedDodda/Paper_trading_bot/actions/workflows/pages.yml/badge.svg" alt="Deployment"/>
  </a>
  <a href="https://pypi.org/project/paper-trading-bot/">
    <img src="https://img.shields.io/pypi/v/paper-trading-bot.svg" alt="PyPI"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"/>
  </a>
</p>

## ⚠️ Important Disclaimer

**THIS IS A PAPER TRADING SIMULATOR FOR EDUCATIONAL PURPOSES ONLY.**

- No real money is involved
- No real trades are executed
- This is NOT financial advice
- Use at your own risk
- The authors assume no liability for any financial losses

**For detailed legal information, please see:**
- [DISCLAIMER.md](DISCLAIMER.md) - General disclaimer
- [RISK_DISCLOSURE.md](RISK_DISCLOSURE.md) - Risk disclosures
- [THIRD_PARTY.md](THIRD_PARTY.md) - Third-party API compliance

---

## 📁 Project Structure

```
paper_trading_bot/
├── bots/                    # Bot entry points (production)
│   ├── __init__.py
│   ├── cli_bot.py          # CLI bot
│   ├── beast_bot.py        # The BEAST - Advanced CLI
│   └── ios_bot.py          # iOS/Pythonista version
│
├── core/                    # Core trading modules
│   ├── __init__.py
│   ├── data_fetcher.py     # Market data fetching
│   ├── strategy.py         # Trading strategies
│   └── backtester.py       # Backtesting engine
│
├── training/                # AI Training scripts
│   ├── __init__.py
│   ├── train_lstm.py       # LSTM model training
│   ├── train_r1.py        # R1 RL training
│   ├── rl_environment.py   # Gymnasium environment
│   ├── backtest.py        # Backtesting script
│   └── test_live.py       # Live testing
│
├── config/                  # Configuration files
│   ├── __init__.py
│   ├── settings.py        # Python configuration
│   ├── config.json        # JSON config
│   ├── config.yaml       # YAML config
│   └── gui_config.json   # GUI settings
│
├── DEV/                     # Developer tools (for development)
│   ├── setup_dirs.py      # Directory setup script
│   └── gui_bot.py        # GUI application
│
├── tests/                   # Test files
│   └── test_bot.py
│
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── assets/                  # Images and media
├── .github/                # GitHub workflows
│
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
└── README.md              # This file
```

---

## 🚀 Quick Start

### Installation

```
bash
# Clone the repository
git clone https://github.com/MohamedDodda/Paper_trading_bot.git
cd paper_trading_bot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Bots

**CLI Bot:**
```bash
python -m bots.cli_bot
```

**The BEAST (Advanced CLI):**
```
bash
python -m bots.beast_bot
```

### Commands

```
start    # Begin trading simulation
stop     # Pause bot
reset    # Reset to $1M virtual balance
report   # Generate performance report
status   # Show current status
help     # Show commands
exit     # Exit the bot
```

---

## 🤖 AI Features

The bot supports AI-powered trading signals via OpenRouter:

1. **LSTM Training** - Train your own LSTM model:
   
```
bash
python -m training.train_lstm
```

2. **Reinforcement Learning** - R1 agent training:

```
bash
python -m training.train_r1
```

Set your API key in `.env`:
```
OPENROUTER_API_KEY=your_key_here
```

---

## 📊 Backtesting

Run historical backtests:
```
bash
python -m training.backtest
```

---

## 🧪 Testing

```
bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

---

## 📝 Configuration

Configuration can be set via:
- `config/settings.py` - Python configuration
- `config/config.json` - JSON configuration
- `config/config.yaml` - YAML configuration
- Environment variables (`.env`)

### Key Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `STOCK_MODE` | Use stocks instead of crypto | `True` |
| `SYMBOLS` | Trading symbols | `['AAPL', 'GOOGL', ...]` |
| `STARTING_CASH` | Virtual balance | `$1,000,000` |
| `UPDATE_INTERVAL` | Update frequency (seconds) | `10` |
| `RISK_PER_TRADE` | Risk per trade | `3%` |
| `STOP_LOSS_PCT` | Stop loss percentage | `5%` |
| `TAKE_PROFIT_PCT` | Take profit percentage | `10%` |

---

## 🔧 Development

### Package Structure

- `core/` - Core trading logic (data fetching, strategies, backtesting)
- `bots/` - Different bot interfaces (CLI, iOS)
- `training/` - AI model training scripts
- `config/` - Configuration management
- `DEV/` - Developer tools and GUI

### Adding New Strategies

1. Add strategy to `core/strategy.py`
2. Import in `core/__init__.py`
3. Use in bots

---

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

---

## ⚡ Tech Stack

- **Python 3.8+**
- **Data**: yfinance, Crypto.com API
- **AI/ML**: TensorFlow, Stable Baselines3, Gymnasium
- **GUI**: CustomTkinter, Streamlit
- **Analysis**: Pandas, NumPy, QuantStats

---

## 👤 Author

**Mohamed Dodda**
- GitHub: [@MohamedDodda](https://github.com/MohamedDodda)
- Twitter: [@MohamedDodda](https://x.com/MohamedDodda)

---

## 🙏 Acknowledgments

- OpenRouter for AI signals
- Crypto.com for market data
- Yahoo Finance for stock data
- Contributors and testers
