#!/usr/bin/env python3
\"\"\"Pythonista iOS Mode Launcher.
For Pythonista 3 on iOS devices.\"\"\"
try:
    import console  # Only exists in Pythonista 3 on iOS
    IS_PYTHONISTA = True
    print(\"🤖 Paper Trading Bot - iOS/Pythonista Mode\")
except ImportError:
    IS_PYTHONISTA = False
    print(\"This file is for Pythonista 3 on iOS.\")
    print(\"On PC/Mac/Linux, run: python bot.py\")
    exit(1)

if IS_PYTHONISTA:
    try:
        from bots.ios_bot import main
        main()
    except ImportError:
        print(\"ios_bot.py not found. Install bots/ios_bot.py for iOS support.\")
else:
    print(\"Not running in Pythonista environment.\")

