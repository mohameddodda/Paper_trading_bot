# Copyright 2026 Mohamed Dodda
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
