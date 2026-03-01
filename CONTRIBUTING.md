# Contributing to Paper Trading Bot

**Thank you** for your interest in improving **Paper Trading Bot**!  
Your contributions help make this a better tool for learning and simulation.

—

## How to Contribute

1. **Fork** the repository  
   → Click **"Fork"** on [GitHub](https://github.com/mohameddodda/Paper_trading_bot)

2. **Clone** your fork  
   
```
bash
   git clone https://github.com/YOUR-USERNAME/Paper_trading_bot.git
   cd Paper_trading_bot
   
```

3. **Create a branch** for your feature or fix  
   
```
bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   
```

4. **Make your changes**  
   - Follow the project structure:
     - `core/` - Core trading logic
     - `bots/` - Bot entry points
     - `training/` - AI training scripts
     - `config/` - Configuration
     - `DEV/` - Developer tools
     - `tests/` - Test files

5. **Test your changes**  
   
```
bash
   # Run tests
   pytest tests/
   
   # Run specific bot
   python -m bots.cli_bot
   
```

6. **Commit** with a clear message  
   
```
bash
   git add .
   git commit -m "Add: description of your changes"
   
```

7. **Push** to your fork  
   
```
bash
   git push origin feature/your-feature-name
   
```

8. **Open a Pull Request**  
   → Go to the original repo and click **"New Pull Request"**

—

## Project Structure

```
paper_trading_bot/
├── bots/                    # Bot entry points
│   ├── cli_bot.py          # CLI bot
│   ├── beast_bot.py        # The BEAST CLI
│   └── ios_bot.py          # iOS version
├── core/                    # Core trading modules
│   ├── data_fetcher.py    # Market data fetching
│   ├── strategy.py        # Trading strategies
│   └── backtester.py      # Backtesting engine
├── training/               # AI Training scripts
│   ├── train_lstm.py      # LSTM model training
│   ├── train_r1.py        # R1 RL training
│   └── rl_environment.py  # Gymnasium environment
├── config/                 # Configuration files
│   ├── settings.py        # Python configuration
│   └── config.json        # JSON config
├── DEV/                   # Developer tools
│   └── gui_bot.py        # GUI application
└── tests/                 # Test files
    └── test_bot.py
```

—

## Coding Standards

- **Python 3.8+** - Use type hints where possible
- **PEP 8** - Follow style guidelines
- **Docstrings** - Document all public functions and classes
- **Modular** - Keep functions small and focused

### Example Function

```
python
def calculate_position_size(balance: float, risk_per_trade: float) -> float:
    """
    Calculate the position size based on account balance and risk tolerance.
    
    Args:
        balance: Total account balance
        risk_per_trade: Risk percentage per trade (e.g., 0.03 for 3%)
    
    Returns:
        Position size in currency units
    """
    return balance * risk_per_trade
```

—

## Testing

All new features should include tests:

```
python
# tests/test_bot.py
def test_calculate_position_size():
    """Test position size calculation."""
    result = calculate_position_size(100000, 0.03)
    assert result == 3000
```

Run tests:
```
bash
pytest tests/ -v
```

—

## Pre-submission checks

Before submitting a PR, ensure:

- [ ] Code follows PEP 8
- [ ] Tests pass (`pytest tests/`)
- [ ] New features have docstrings
- [ ] No debug prints or commented-out code
- [ ] README.md updated (if needed)

—

## Issues and Feature Requests

- **Bugs**: Open an issue with clear steps to reproduce
- **Features**: Describe the desired feature and use case
- **Questions**: Use GitHub Discussions

—

## Review process

1. Maintainers will review your PR
2. Address any feedback promptly
3. Once approved, your PR will be merged

—

## License

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**.

—

## Code of conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

—

*Thank you for contributing to Paper Trading Bot!*
