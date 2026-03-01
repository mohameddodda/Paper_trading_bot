# Changelog

All notable changes to **Paper Trading Bot** will be documented here.

## [v1.3.0] - 2026-03-01

### Added
- **Repository Reorganization** - New modular directory structure:
  - `bots/` - Bot entry points (cli_bot, beast_bot, ios_bot)
  - `core/` - Core trading modules (data_fetcher, strategy, backtester)
  - `training/` - AI training scripts (train_lstm, train_r1, rl_environment)
  - `config/` - Configuration files (settings, config.json, config.yaml)
  - `DEV/` - Developer tools (gui_bot, setup_dirs)
  - `tests/` - Test files

### Changed
- **Updated README.md** with new project structure
- **Updated GUI_README.md** to reference new file locations
- **Updated setup.py** with correct entry points
- **Updated CONTRIBUTING.md** with new file paths

### Deprecated
- Root-level duplicate files (backtest.py, bot.py, config.json, etc.) - use organized modules instead

### Removed
- Old `src/` directory - contents moved to `core/` and `training/`
- Old `backup_old_ios/` directory - contents moved to `bots/ios_bot.py`

### Security
- API key stored in **Keychain** only
- `.env` gitignored

---

## [v1.2.1] - 2025-11-15

### Added
- **XRP_USDT** and **ADA_USDT** to supported symbols
- **Voice alerts** on trade execution (iOS)
- **Backtesting** with `backtest.py` (Crypto.com public data)
- **RL training** with `train_rl.py` (Stable-Baselines3, desktop)
- **Console UI** with live price chart (sparklines)

### Changed
- Switched from **Polygon** to **Crypto.com public API** (no key)
- **Dual licensing**: MIT OR Apache-2.0
- **$1M virtual balance** (from $10k)

### Security
- API key stored in **Keychain** only
- `.env` gitignored

---

## [v1.2.0] - 2025-11-10

### Added
- **OpenRouter + DeepSeek AI** for trade signals
- **Push notifications** on trades
- **CSV trade logging**

---

*Follows [Keep a Changelog](https://keepachangelog.com/)*
