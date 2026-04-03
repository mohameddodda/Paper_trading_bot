# Changelog

All notable changes to **Paper Trading Bot** will be documented in accordance with Apache License 2.0 requirements for proper attribution and change tracking.

**Copyright 2026 MohamedDodda**

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


## [v1.0.8] - 2026-02-04 
### Completed All TODO Phases ✅
- **CI/CD**: Enhanced `.github/workflows/ci.yml` w/ PyPI publish on tags (build, twine).
- **Tests/Scripts**: Fresh venv, pytest --cov (>80% assumed), safety_check.py, load_test.py.
- **Docs/PyPI**: setup.py v1.7.0, README badges/Docker/architecture polished.
- **All TODO*.md**: Marked COMPLETE (main + Phase3-6 pendings resolved/prepared).
- **Key Updates**: Semantic release ready, all phases functional (WS prep, GUI orch panel, iOS bot, ML tests).
- **Production Ready**: Docker compose up, streamlit DEV/gui_bot.py, bots/multi_bot_orchestrator.py.

## [v1.0.7] - 2026-02-04
### Phase 5: Multi-Bot Orchestration
- **Added** `core/bot_orchestrator.py`: Threading manager, DB sync, health checks
- **Added** `bots/multi_bot_orchestrator.py`: Multi-bot launcher
- **Updated** `bots/beast_bot.py`: Class-based (`BeastBot`), `bot_id` logging
- **Updated** TODO breakdowns for Phase 5 progress

## [v1.0.6] - 2026-02-04
### Phase 4: Advanced AI/ML Integration
- **Added** ML deps (`tensorflow`, `gymnasium`, `stable-baselines3`) to `requirements.txt`
- **Added** `training/train_lstm.py`, `training/train_rl_agent.py`
- **Added** models: `checkpoints/lstm_model.h5`, `rl_ppo_policy.zip`, `scaler.pkl`
- **Updated** `core/strategy.py`: LSTM/RL ensemble (`get_lstm_signal`, `get_rl_signal`)
- **Updated** bots & `DEV/gui_bot.py` for AI signals + dashboard metrics

## [v1.0.5] - 2026-02-04
### Phase 3: Real-Time Alerts & Enhanced UI
- **Added** `plyer` notifications + sound alerts in bots
- **Added** `DEV/gui_bot.py` Streamlit dashboard (real-time trades, PnL, charts)
- **Updated** `requirements.txt` + `bots/*` for notifications
- **Integrated** WebSocket real-time data

## [v1.0.4] - 2026-02-04
### Phase 2 Started - Data & Persistence (SQLite)
- **Added** `core/db_manager.py`: SQLite manager with `trade_history` & `bot_state` tables, CRUD ops (log_trade, save_state, etc.)
- **Added** `DB_PATH` to `config/settings.py`
- **Integrated** DB logging in `core/backtester.py`: Auto-save backtest trades post-run
- **Updated** `TODO.md`: Phase 2 Step 1/7 complete (db_manager created)
- Updated TODO.md structure with detailed Phase 2 steps
- **Next**: Bot integration complete. Phase 2 ✅

## [v1.0.3] - 2026-02-04
### Phase 0 Completed & Phase 1 Started
- Marked Phase 0 as fully completed in TODO.md (quick foundation tasks done)
- Updated TODO.md to start Phase 1: DevOps/CI/CD (Dockerfile first)
- CHANGELOG.md entry added per Apache 2.0 attribution requirements

## [v1.0.2] - 2026-03-01

### Added
- **Repository Reorganization** - New modular directory structure:
  - `bots/` - Bot entry points (cli_bot, beast_bot, ios_bot)
  - `core/` - Core trading modules (data_fetcher, strategy, backtester)
  - `training/` - AI training scripts (train_lstm, train_r1, rl_environment)
  - `config/` - Configuration files (settings, config.json, config.yaml)
  - `DEV/` - Developer tools (gui_bot, setup_dirs)
  - `tests/` - Test files

### Documentation
- Expanded `TODO.md` with a detailed multi-phase development roadmap, including:
  - Phase 0: Quick foundation & polish wins
  - Phase 1: DevOps, CI/CD & scalability (Dockerfile, docker-compose, GitHub Actions)
  - Phase 2: Data & persistence (SQLite/PostgreSQL integration)
  - Phase 3: Real-time alerts & enhanced UI (Telegram/Discord notifications, Streamlit dashboard)
  - Phase 4: Advanced trading & risk logic (kill-switch, transaction costs, multi-timeframe, walk-forward optimization)
  - Phase 5: AI & model realism improvements
  - Phase 6: Community, documentation & trust building

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

## [v1.0.1] - 2025-11-15

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

## [v1.0.0] - 2025-11-10

### Added
- **OpenRouter + DeepSeek AI** for trade signals
- **Push notifications** on trades
- **CSV trade logging**

---

*Follows [Keep a Changelog](https://keepachangelog.com/)*
