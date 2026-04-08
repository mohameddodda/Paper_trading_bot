# TODO — Fix List for Paper Trading Bot
# Last Updated: April 2026
# Status: 68% Complete — Bot does NOT run yet
# Goal: Make the bot fully runnable end-to-end
# Priority: Work top to bottom — do not skip steps

—

## HOW TO USE THIS FILE
- Work through each task in order (1 → 12)
- Mark tasks done by changing [ ] to [x]
- Do not leave empty function bodies — use NotImplementedError instead
- Test after EVERY fix before moving to the next one
- Run: python scripts/check_setup.py after all fixes to verify

—

## FIX 1 — Create root-level bot.py launcher
Priority: CRITICAL — Bot cannot start without this
File to create: bot.py (in root directory)

[ ] Create bot.py in the project root
[ ] Import and launch bots/cli_bot.py as the default entry point
[ ] Add —mode argument support: cli, beast, gui
    - python bot.py           → launches cli_bot
    - python bot.py —mode beast  → launches beast_bot
    - python bot.py —mode gui    → launches gui_bot
[ ] Call scripts/check_setup.py first before launching any bot
[ ] Print a welcome banner showing bot name, version, virtual balance
[ ] Load .env using python-dotenv at the top of this file

Example structure:
    from dotenv import load_dotenv
    load_dotenv()
    import argparse
    from scripts.check_setup import run_checks
    run_checks()
    parser = argparse.ArgumentParser()
    parser.add_argument(“—mode”, choices=[“cli”,”beast”,”gui”], default=“cli”)
    args = parser.parse_args()
    if args.mode == “cli”:
        from bots.cli_bot import main
        main()
    elif args.mode == “beast”:
        from bots.beast_bot import main
        main()
    elif args.mode == “gui”:
        from bots.gui_bot import main
        main()

—

## FIX 2 — Create missing data/ directory
Priority: CRITICAL — Any write operation will crash without this
Files to create: data/.gitkeep, data/README.md

[ ] Create data/.gitkeep (empty file so Git tracks the folder)
[ ] Create data/README.md explaining what is stored here:
    - data/trades.db → SQLite database for trade history
    - data/logs/     → Bot activity logs
    - data/history/  → Price history CSV files
    - data/exports/  → Performance report exports
[ ] Update scripts/setup_dirs.py to auto-create these folders at startup:
    - data/
    - data/logs/
    - data/history/
    - data/exports/
    - checkpoints/
[ ] Add this to setup_dirs.py:
    import os
    REQUIRED_DIRS = [“data”,”data/logs”,”data/history”,”data/exports”,”checkpoints”]
    for d in REQUIRED_DIRS:
        os.makedirs(d, exist_ok=True)

—

## FIX 3 — Fix and complete .env.example
Priority: CRITICAL — Bot will silently fail or crash with missing env vars
File to fix: .env.example

[ ] Replace current .env.example with this complete version:

    # ── AI / OpenRouter ──────────────────────────────
    OPENROUTER_API_KEY=your_openrouter_key_here
    OPENROUTER_MODEL_PRIMARY=mistralai/mistral-7b-instruct
    OPENROUTER_MODEL_SECONDARY=deepseek/deepseek-chat

    # ── Crypto.com API ───────────────────────────────
    CRYPTO_API_BASE=https://api.crypto.com/v2

    # ── Trading Settings ─────────────────────────────
    STARTING_CASH=1000000
    UPDATE_INTERVAL=15
    RISK_PER_TRADE=0.03
    STOP_LOSS_PCT=0.05
    TAKE_PROFIT_PCT=0.10
    STOCK_MODE=False

    # ── Database & Storage ───────────────────────────
    DB_PATH=data/trades.db

    # ── Logging ──────────────────────────────────────
    LOG_LEVEL=INFO

    # ── Streamlit Dashboard (optional) ───────────────
    STREAMLIT_PORT=8501

[ ] Verify every os.getenv() call in the codebase has a matching entry here
[ ] Add a comment at the top: “Copy this file to .env and fill in your values”

—

## FIX 4 — Add model file existence checks
Priority: CRITICAL — Bot crashes on startup if checkpoints are missing
Files to fix: bots/beast_bot.py, training/train_lstm.py, any file that loads models

[ ] In beast_bot.py, before loading LSTM or RL models, add:
    import os
    LSTM_PATH = “checkpoints/lstm_model.h5”
    RL_PATH = “checkpoints/rl_ppo_policy.zip”

    if os.path.exists(LSTM_PATH):
        model = load_model(LSTM_PATH)
        print(“[AI] LSTM model loaded”)
    else:
        model = None
        print(“[WARNING] No LSTM model found — falling back to RSI/MACD strategy”)
        print(“[INFO] Train one with: python -m training.train_lstm”)

[ ] Do the same check for rl_ppo_policy.zip
[ ] Bot must NOT crash if these files are missing
[ ] If both models are missing, fall back to rule-based strategy (MA/RSI/MACD)
[ ] Add a status line in the startup banner showing which AI mode is active:
    - “AI Mode: LSTM + RL” if both files exist
    - “AI Mode: OpenRouter only” if API key set but no local models
    - “AI Mode: Rule-based only” if nothing is available

—

## FIX 5 — Fix requirements.txt with pinned compatible versions
Priority: HIGH — Dependency conflicts will prevent installation
File to fix: requirements.txt

[ ] Add this comment block at the top:
    # Python 3.9 or 3.10 recommended
    # Python 3.11+ may have TensorFlow compatibility issues
    # Install with: pip install -r requirements.txt
    # For GPU support, replace tensorflow with tensorflow-gpu==2.13.0

[ ] Use these exact pinned versions (known to work together):
    numpy==1.24.3
    pandas==2.0.3
    tensorflow==2.13.0
    torch==2.0.1
    stable-baselines3==2.1.0
    gymnasium==0.29.1
    streamlit==1.28.0
    customtkinter==5.2.1
    quantstats==0.0.62
    yfinance==0.2.31
    requests==2.31.0
    python-dotenv==1.0.0
    rich==13.6.0
    ta==0.10.2
    websocket-client==1.6.4
    aiohttp==3.9.0

[ ] After editing, test on a clean virtual environment:
    python -m venv test_env
    source test_env/bin/activate   (Mac/Linux)
    test_env\Scripts\activate      (Windows)
    pip install -r requirements.txt
    python -c “import tensorflow, stable_baselines3, gymnasium, streamlit”

—

## FIX 6 — Fix setup.py to read from requirements.txt
Priority: HIGH — Duplicate dependency lists cause conflicts
File to fix: setup.py

[ ] Replace install_requires hardcoded list with dynamic reader:
    with open(“requirements.txt”) as f:
        requirements = [
            line.strip() for line in f
            if line.strip() and not line.startswith(“#”)
        ]

[ ] Full setup.py should look like:
    from setuptools import setup, find_packages

    with open(“requirements.txt”) as f:
        requirements = [
            line.strip() for line in f
            if line.strip() and not line.startswith(“#”)
        ]

    with open(“README.md”, encoding=“utf-8”) as f:
        long_description = f.read()

    setup(
        name=“paper-trading-bot”,
        version=“0.6.8”,
        author=“Mohamed Dodda”,
        description=“AI-Powered Crypto Paper Trading Bot”,
        long_description=long_description,
        long_description_content_type=“text/markdown”,
        packages=find_packages(),
        install_requires=requirements,
        python_requires=“>=3.9”,
        entry_points={
            “console_scripts”: [
                “paperbot=bots.cli_bot:main”,
            ]
        }
    )

—

## FIX 7 — Fix core/data_fetcher.py for Crypto.com API
Priority: HIGH — No live data means the bot cannot trade
File to fix: core/data_fetcher.py

[ ] Use the correct Crypto.com API endpoint format:
    https://api.crypto.com/v2/public/get-ticker?instrument_name=BTC_USDT

[ ] Support all 8 trading pairs in this format:
    BTC_USDT, ETH_USDT, SOL_USDT, DOGE_USDT,
    SHIB_USDT, CRO_USDT, XRP_USDT, ADA_USDT

[ ] Parse the response correctly:
    response[“result”][“data”][“a”]  → ask price (what you pay to buy)
    response[“result”][“data”][“b”]  → bid price (what you get when selling)
    response[“result”][“data”][“k”]  → timestamp

[ ] Add retry logic — if API call fails, retry 3 times with 2 second delay:
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=5)
            break
        except Exception:
            time.sleep(2)

[ ] Add yfinance fallback if Crypto.com is unreachable:
    import yfinance as yf
    ticker = yf.Ticker(“BTC-USD”)
    price = ticker.fast_info[‘last_price’]

[ ] Cache prices locally for 10 seconds to avoid rate limiting:
    Use a dict: _price_cache = {} with timestamps

[ ] Load base URL from environment:
    BASE_URL = os.getenv(“CRYPTO_API_BASE”, “https://api.crypto.com/v2”)

[ ] Wrap every API call in try/except and log failures with rich

—

## FIX 8 — Add missing __init__.py files
Priority: MEDIUM — pytest and imports may fail without these
Files to create: tests/__init__.py, scripts/__init__.py

[ ] Create empty tests/__init__.py
[ ] Create empty scripts/__init__.py
[ ] Verify these directories already have __init__.py (they should):
    - bots/__init__.py        ✓
    - core/__init__.py        ✓
    - config/__init__.py      ✓
    - training/__init__.py    ✓

—

## FIX 9 — Create pythonista_ios_mode.py in root
Priority: MEDIUM — iOS users will fail immediately without this
File to create: pythonista_ios_mode.py (in root directory)

[ ] Create pythonista_ios_mode.py with this logic:
    try:
        import console   # This module only exists in Pythonista 3 on iOS
        IS_PYTHONISTA = True
    except ImportError:
        IS_PYTHONISTA = False

    if IS_PYTHONISTA:
        from bots.ios_bot import main
        main()
    else:
        print(“This file is for Pythonista 3 on iOS.”)
        print(“On PC/Mac/Linux, run: python bot.py”)

[ ] Add a welcome message before launching on iOS
[ ] Add error handling if ios_bot.py fails to import

—

## FIX 10 — Fix incomplete stubs in multi_bot_orchestrator.py
Priority: MEDIUM — Empty stubs cause silent failures on import
File to fix: bots/multi_bot_orchestrator.py

[ ] Find every empty method (ones with just “pass”) and replace with:
    def start_streamlit_dashboard(self):
        raise NotImplementedError(
            “Streamlit dashboard not yet implemented. “
            “Coming in v1.0. Run ‘python bot.py’ for CLI mode.”
        )

[ ] Find every incomplete method and add a TODO comment explaining
    exactly what it needs to do when implemented

[ ] Make sure the file can be imported without crashing:
    python -c “from bots.multi_bot_orchestrator import MultiBotOrchestrator”
    This must not raise any errors.

—

## FIX 11 — Remove git merge artifact and update .gitignore
Priority: LOW — Cleanup only, won’t affect running the bot
Files: delete TODO.md~HEAD, fix .gitignore

[ ] Delete the file called: TODO.md~HEAD
    (This is a leftover from a git merge conflict — it is not a real file)

[ ] Add these lines to .gitignore:
    # Git merge artifacts
    *.orig
    *.md~*
    *~HEAD
    *.bak
    *.pyc
    __pycache__/
    .env
    *.h5
    *.zip
    data/trades.db
    data/logs/
    data/history/
    data/exports/

—

## FIX 12 — Create scripts/check_setup.py validation script
Priority: HIGH — Users need a way to verify their setup works
File to create: scripts/check_setup.py

[ ] Create check_setup.py that runs 12 checks and prints results:

    CHECK 1:  Python version is 3.9 or 3.10
    CHECK 2:  numpy is importable
    CHECK 3:  tensorflow is importable
    CHECK 4:  stable_baselines3 is importable
    CHECK 5:  requests is importable
    CHECK 6:  rich is importable
    CHECK 7:  OPENROUTER_API_KEY is set and not empty
    CHECK 8:  data/ directory exists
    CHECK 9:  checkpoints/ directory exists
    CHECK 10: Crypto.com API is reachable (test BTC_USDT price fetch)
    CHECK 11: .env file exists in project root
    CHECK 12: config/settings.py is importable

[ ] Use rich library to print colored output:
    ✅ green checkmark for each passing check
    ❌ red X with explanation for each failing check

[ ] At the end print a summary:
    “12/12 checks passed — Bot is ready! Run: python bot.py”
    OR
    “8/12 checks passed — Fix the items marked ❌ above before running”

[ ] The function must be callable from bot.py like this:
    from scripts.check_setup import run_checks
    run_checks()

—

## GENERAL RULES — APPLY TO EVERY FILE YOU TOUCH

[ ] Every entry point file must start with:
    from dotenv import load_dotenv
    load_dotenv()

[ ] Every function must have a docstring

[ ] All API calls must be in try/except blocks with meaningful error messages

[ ] Never hardcode API keys, file paths, or URLs — use os.getenv()

[ ] Use the rich library for all terminal output (no plain print in main files)

[ ] Never leave empty function bodies — use NotImplementedError with a message

[ ] After every fix, run this to confirm no import errors:
    python -c “from bots.cli_bot import main”
    python -c “from core.data_fetcher import DataFetcher”
    python -c “from core.strategy import Strategy”

—

## DONE CRITERIA — Bot is fixed when ALL of these work:

[ ] git clone https://github.com/MohamedDodda/Paper_trading_bot.git
[ ] cd Paper_trading_bot
[ ] pip install -r requirements.txt        ← no errors
[ ] cp .env.example .env                   ← then add OpenRouter API key
[ ] python scripts/check_setup.py          ← all checks pass
[ ] python bot.py                          ← bot starts, shows live prices
[ ] python bot.py —mode beast             ← beast mode starts
[ ] pytest tests/                          ← tests run without import errors
[ ] python -m training.backtest            ← backtester runs without crashing

—

## VERSION TARGET: v1.1.0 — “First Runnable Release”
## Author: Mohamed Dodda
## Repo: https://github.com/MohamedDodda/Paper_trading_bot
