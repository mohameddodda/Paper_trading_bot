#!/usr/bin/env python3
"""
Full setup validation script with 12 checks. Uses rich for output.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import tensorflow as tf

load_dotenv()
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
console = Console()

def check_python_version():
    if sys.version_info < (3, 9):
        return False, f"Python {sys.version} - needs 3.9+"
    return True, f"Python {sys.version.split()[0]} ✓"

def check_numpy():
    try:
        import numpy
        return True, "numpy ✓"
    except:
        return False, "numpy missing"

def check_tensorflow():
    try:
        import tensorflow
        return True, f"tensorflow {tensorflow.__version__} ✓"
    except:
        return False, "tensorflow missing"

def check_stable_baselines3():
    try:
        import stable_baselines3
        return True, "stable_baselines3 ✓"
    except:
        return False, "stable_baselines3 missing"

def check_requests():
    try:
        import requests
        return True, "requests ✓"
    except:
        return False, "requests missing"

def check_rich():
    try:
        import rich
        return True, "rich ✓"
    except:
        return False, "rich missing"

def check_openrouter_key():
    key = os.getenv("OPENROUTER_API_KEY")
    if key and len(key) > 10:
        return True, "OPENROUTER_API_KEY set ✓"
    return False, "OPENROUTER_API_KEY missing/empty"

def check_data_dir():
    if (PROJECT_ROOT / "data").exists():
        return True, "data/ ✓"
    return False, "data/ missing"

def check_checkpoints_dir():
    if (PROJECT_ROOT / "checkpoints").exists():
        return True, "checkpoints/ ✓"
    return False, "checkpoints/ missing"

def check_crypto_api():
    try:
        resp = requests.get("https://api.crypto.com/exchange/v1/public/get-ticker?instrument_name=BTC_USDT", timeout=5)
        if resp.status_code == 200 and resp.json().get("code") == 0:
            return True, "Crypto.com API ✓"
        return False, f"Crypto API failed: {resp.status_code}"
    except:
        return False, "Crypto API unreachable"

def check_env_file():
    if PROJECT_ROOT.joinpath(".env").exists():
        return True, ".env exists ✓"
    return False, ".env missing (copy .env.example)"

def check_settings():
    try:
        import config.settings
        return True, "config/settings.py ✓"
    except:
        return False, "config/settings.py import failed"

CHECKS = [
    ("1. Python version", check_python_version),
    ("2. numpy", check_numpy),
    ("3. tensorflow", check_tensorflow),
    ("4. stable_baselines3", check_stable_baselines3),
    ("5. requests", check_requests),
    ("6. rich", check_rich),
    ("7. OPENROUTER_API_KEY", check_openrouter_key),
    ("8. data/ directory", check_data_dir),
    ("9. checkpoints/ directory", check_checkpoints_dir),
    ("10. Crypto.com API", check_crypto_api),
    ("11. .env file", check_env_file),
    ("12. config/settings.py", check_settings),
]

def run_checks():
    console.print("[bold cyan]🤖 Paper Trading Bot - Setup Validation[/bold cyan]")
    console.print("=" * 60)
    
    passed = 0
    table = Table(title="Setup Checks", show_header=True, header_style="bold magenta")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    
    for name, check_func in CHECKS:
        ok, msg = check_func()
        status = "[green]✅[/green]" if ok else "[red]❌[/red]"
        table.add_row(name, f"{status} {msg}")
        if ok:
            passed += 1
    
    console.print(table)
    
    console.print()
    if passed == 12:
        rprint("[bold green]🎉 ALL 12/12 CHECKS PASSED - Bot is READY![/bold green]")
        rprint("[bold green]Run:[/bold green] python bot.py")
    else:
        rprint(f"[bold yellow]{passed}/12 checks passed[/bold yellow]")
        rprint("[bold yellow]Fix ❌ items above then re-run[/bold yellow]")

if __name__ == "__main__":
    run_checks()

