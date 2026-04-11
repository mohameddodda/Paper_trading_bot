#!/usr/bin/env python3
"""Paper Trading Bot Launcher.
Unified entry point for all bot modes."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse
from core.strategy import LSTM_MODEL_PATH, RL_POLICY_PATH

# Load environment variables first
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

PROJECT_ROOT = Path(__file__).parent.resolve()
VERSION = "0.6.8"

def get_ai_status():
    \"\"\"Determine current AI mode status.\"\"\"
    has_lstm = LSTM_MODEL_PATH.exists()
    has_rl = RL_POLICY_PATH.exists()
    has_api = bool(os.getenv('OPENROUTER_API_KEY'))
    
    if has_lstm and has_rl:
        return '🧠 LSTM + RL (Full AI)'
    elif has_api:
        return '🌐 OpenRouter API only'
    else:
        return '📊 Rule-based only'

def print_banner(mode):
    ai_status = get_ai_status()
    print(\"\\n\" + \"=\"*70)
    print(f\"🤖 Paper Trading Bot v{VERSION} | Mohamed Dodda\")
    print(f\"🚀 Mode: {mode.upper()} | {ai_status}\")
    print(f\"💰 Virtual Balance: $1,000,000\")
    print(f\"📁 Project: {PROJECT_ROOT}\")
    print(\"=\"*70 + \"\\n\")

def main():
    # Run setup checks first
    try:
        from scripts.check_setup import run_checks
        run_checks()
    except ImportError as e:
        print(f\"⚠️  Setup check failed: {e}\")
        print(\"Continue anyway...\")

    parser = argparse.ArgumentParser(description=\"Paper Trading Bot Launcher\")
    parser.add_argument(\"--mode\", choices=[\"cli\", \"beast\", \"gui\"], default=\"cli\",
                        help=\"Bot mode: cli (default), beast, gui\")
    args = parser.parse_args()

    print_banner(args.mode)

    if args.mode == \"cli\":
        from bots.cli_bot import main as cli_main
        cli_main()
    elif args.mode == \"beast\":
        from bots.beast_bot import main as beast_main
        beast_main()
    elif args.mode == \"gui\":
        from bots.gui_bot import main as gui_main
        gui_main()

if __name__ == \"__main__\":
    main()

