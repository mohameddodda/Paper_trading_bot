"""
bots – Paper Trading Bot Entry Points
=====================================

This package contains various bot entry points:
- cli_bot.py: Command-line interface bot
- beast_bot.py: The BEAST - advanced CLI bot
- gui_bot.py: Desktop GUI application
- ios_bot.py: iOS/Pythonista version

For educational paper trading simulations only.
"""

from .cli_bot import main as cli_main
from .beast_bot import main as beast_main
from .gui_bot import TradingBotGUI

__version__ = "3.0.0"

__all__ = [
    "cli_main",
    "beast_main", 
    "TradingBotGUI",
]
