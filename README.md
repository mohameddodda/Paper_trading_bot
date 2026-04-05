# Paper Trading Bot - AI-Powered Crypto/Stock Simulator

<p align="center">
  <img src="assets/bot-running.png" alt="Paper Trading Bot" width="600"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/paper-trading-bot/">
    <img src="https://img.shields.io/pypi/v/paper-trading-bot.svg" alt="PyPI"/>
  </a>
  <a href="https://github.com/MohamedDodda/Paper_Trading_Bot/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow-status/MohamedDodda/Paper_Trading_Bot/ci.yml?branch=main" alt="CI"/>
  </a>
  <a href="https://codecov.io/gh/MohamedDodda/Paper_Trading_Bot">
    <img src="https://img.shields.io/codecov/c/github/MohamedDodda/Paper_Trading_Bot/main.svg" alt="Coverage"/>
  </a>
  <a href="https://pypi.org/project/paper-trading-bot/">
    <img src="https://img.shields.io/pypi/pyversions/paper-trading-bot" alt="Python Versions"/>
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

## 📁 Project Structure (Updated for New Organization)

```
Paper_Trading_Bot/
├── .github/                 # GitHub workflows & templates
│   └── workflows/
├── assets/                  # Images & media (bot-running.png, iphone-mockup.png)
├── bots/                    # Bot implementations
│   ├── __init__.py
│   ├── beast_bot.py
│   ├── cli_bot.py
│   ├── gui_bot.py
│   ├── ios_bot.py
│   └── multi_bot_orchestrator.py
├── build/                   # Build artifacts
├── checkpoints/             # Model checkpoints (lstm_model.h5, rl_ppo_policy.zip)
├── config/                  # All configurations
│   ├── __init__.py
│   ├── config.json
│   ├── config.yaml
│   ├── gui_config.json
│   └── settings.py
├── core/                    # Core logic
│   ├── __init__.py
│   ├── backtester.py
│   ├── bot_orchestrator.py
│   ├── data_fetcher.py
│   ├── db_manager.py
│   └── strategy.py
├── data/                    # Data storage
├── docker/                  # Docker configs
│   ├── docker-compose.prod.yml
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── Dockerfile.prod
├── scripts/                 # Utility scripts
│   ├── load_test.py
│   ├── safety_check.py
│   └── setup_dirs.py
├── tests/                   # Unit tests
│   ├── test_bot.py
│   ├── test_db.py
│   └── test_orchestration.py
├── training/                # Training scripts
│   ├── __init__.py
│   ├── backtest.py
│   ├── rl_environment.py
│   ├── test_live.py
│   ├── train_lstm.py
│   ├── train_r1.py
│   └── train_rl_agent.py
├── setup.py                 # Package installation
├── requirements.txt         # Dependencies
├── README.md               # This file
├── TODO_ORGANIZATION.md    # Reorg tracking
└── index.html              # Web entry (if applicable)
```


---

## 🚀 Quick Start

### Installation

```
bash
# Clone the repository
git clone https://github.com/MohamedDodda/Paper_Trading_Bot.git
cd Paper_Trading_Bot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or 
venv\Scripts\activate      # Windows

# Install in editable mode (recommended for development)
pip install -r requirements.txt
pip install -e .
```

### Running the Bots

**CLI Bot:**
```bash
python -m bots.cli_bot
```

**The BEAST (Advanced CLI):**
```bash
python -m bots.beast_bot
```

**GUI Bot:**
```bash
python -m bots.gui_bot
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
- `scripts/` - Utility scripts
- `docker/` - Containerization

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
- Instagram: [@MohamedDodda_](https://instagram.com/MohamedDodda_)

---

## 🙏 Acknowledgments

- OpenRouter for AI signals
- Crypto.com for market data
- Yahoo Finance for stock data
- Contributors and testers
