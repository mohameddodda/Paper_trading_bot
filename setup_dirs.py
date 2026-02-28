#!/usr/bin/env python3
"""Script to verify and organize the project structure"""

import os
import shutil

base = "d:/playground/Paper_Trading_Bot"

# List of directories to create
dirs = ["core", "bots", "training", "config", "docs", "scripts"]

# Files to move/copy
moves = [
    # Core modules
    ("src/data_fetcher.py", "core/data_fetcher.py"),
    ("src/strategy.py", "core/strategy.py"),
    ("src/backtester.py", "core/backtester.py"),
    # Bots
    ("bot.py", "bots/cli_bot.py"),
    ("Paper_Trading_bot.py", "bots/beast_bot.py"),
    ("gui_app.py", "bots/gui_app.py"),
    ("pythonista_ios_mode.py", "bots/ios_bot.py"),
    # Training
    ("train_ai.py", "training/train_lstm.py"),
    ("train_r1.py", "training/train_r1.py"),
    ("r1_environment.py", "training/rl_environment.py"),
    ("backtest.py", "training/backtest.py"),
    ("test_live.py", "training/test_live.py"),
    # Config
    ("config.py", "config/settings.py"),
    ("config.json", "config/config.json"),
    ("config.yaml", "config/config.yaml"),
    ("gui_config.json", "config/gui_config.json"),
]

print("Creating directories...")
for d in dirs:
    path = os.path.join(base, d)
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"  Created: {d}")
    else:
        print(f"  Exists: {d}")

print("\nCopying files...")
for src, dst in moves:
    src_path = os.path.join(base, src)
    dst_path = os.path.join(base, dst)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"  Copied: {src} -> {dst}")
    else:
        print(f"  NOT FOUND: {src}")

print("\nDone! Structure created.")
