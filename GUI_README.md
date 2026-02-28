# Paper Trading Bot - Desktop GUI Application

## Overview

This desktop GUI application provides a native window experience for the Paper Trading Bot on PC/Windows/Mac. It features a modern interface with real-time dashboard, trade logging, and bot controls.

## Quick Start

### Prerequisites

```
bash
# Install required dependencies
pip install -r requirements.txt

# Or just install customtkinter if you already have other deps
pip install customtkinter
```

### Running the App

```
bash
# Run the desktop GUI
python gui_app.py
```

The application will open in a native window with:
- Title bar with minimize/maximize/close controls
- Dashboard with real-time portfolio stats
- Trade log and holdings views
- Start/Stop/Reset controls

---

## Features

### Dashboard Tab
- **Balance**: Current cash balance
- **Portfolio Value**: Total value including holdings
- **P&L**: Profit/Loss from starting amount
- **Trades Today**: Count of trades executed
- **Activity Log**: Real-time bot activity feed

### Trade Log Tab
- Complete history of all trades
- Timestamp, action (BUY/SELL), price, quantity
- Profit/loss percentage per trade

### Holdings Tab
- Current positions with quantities
- Entry price vs current price
- P&L percentage per holding

### Settings Tab
- Update interval slider (5-60 seconds)
- Max risk per trade slider (1-10%)
- AI trading toggle

---

## Configuration

### Option 1: Config File (Easy - Recommended)

Edit `gui_config.json` to customize the app:

```
json
{
    "app_title": "Paper Trading Bot",
    "window_size": "1000x700",
    "theme": "dark",
    "color_theme": "blue",
    "update_interval": 10,
    "logo_text": "📈 Paper Trading Bot",
    "sidebar_width": 200,
    "show_splash": true
}
```

### Option 2: Environment Variables

```
bash
# Set custom window title
export GUI_TITLE="My Trading Bot"

# Set theme (dark/light/system)
export GUI_THEME="dark"

# Set color theme (blue/green/darkblue)
export GUI_COLOR_THEME="blue"
```

### Option 3: Code Modification

For deeper customization, edit `gui_app.py`:

**Changing the App Title:**
```
python
# Line ~50
self.title("Your Custom Title")
```

**Changing the Logo:**
```
python
# In create_sidebar() method
# Replace the logo_label with an image:
self.logo_label = ctk.CTkLabel(
    self.sidebar_frame, 
    text="",  # Remove text
    image=ctk.CTkImage(light_image=Image.open("logo.png"), size=(100, 100))
)
```

**Adding Custom Colors:**
```
python
# In __init__() method, add:
self.primary_color = "#FF6B6B"  # Custom color
self.secondary_color = "#4ECDC4"  # Custom color

# Use in buttons:
self.start_button = ctk.CTkButton(
    ..., 
    fg_color=self.primary_color
)
```

**Adding New Tabs:**
```
python
# In create_main_area() method:
self.analytics_tab = self.tabview.add("📈 Analytics")
# Then add your content
```

---

## File Structure

```
Paper_Trading_Bot/
├── gui_app.py           # Main GUI application
├── gui_config.json     # GUI configuration file
├── GUI_README.md       # This file
├── bot.py              # Core bot logic
├── config.py           # Bot configuration
├── requirements.txt    # Dependencies
└── src/                # Bot modules
    ├── data_fetcher.py
    ├── strategy.py
    └── backtester.py
```

---

## Customization Guide for Developers

### Adding Your Own Logo

1. Place your logo file in the project root (PNG/JPG)
2. Add import at top of `gui_app.py`:
   
```
python
   from PIL import Image
   
```
3. Modify the sidebar:
   
```
python
   # Find self.logo_label and replace with:
   self.logo_label = ctk.CTkLabel(
       self.sidebar_frame, 
       text="",
       image=ctk.CTkImage(
           light_image=Image.open("your_logo.png"),
           dark_image=Image.open("your_logo.png"),
           size=(120, 120)
       )
   )
   
```

### Adding Custom Themes

CustomTkinter supports custom colors. Create a theme file:

```
python
# In gui_app.py
ctk.set_default_color_theme("custom_theme.json")
```

### Adding New Features

1. **New Tab**: Add in `create_main_area()`
2. **New Button**: Add in `create_sidebar()`
3. **New Stats**: Add in `create_dashboard_tab()`

### Connecting to Your Own Bot Logic

The GUI imports from `bot.py`. To use different logic:

```
python
# In gui_app.py, modify imports:
# from bot import portfolio, data_fetcher, strategy, bot_step

# Replace with your own:
# from my_custom_bot import my_portfolio, my_fetcher, my_step
```

---

## Troubleshooting

### "Module not found: customtkinter"
```
bash
pip install customtkinter
```

### "Module not found: PIL"
```
bash
pip install Pillow
```

### Window too small/large
Edit `gui_config.json`:
```
json
{
    "window_size": "1200x800"
}
```

### Bot not starting
- Check that `bot.py` has no errors: `python -m py_compile bot.py`
- Verify API keys in `.env` file

---

## Support

- Original bot repo: https://github.com/mohameddodda/Paper_trading_bot
- CustomTkinter docs: https://customtkinter.tomschimansky.com/

---

**Disclaimer**: This is for paper trading simulations only. No real money involved.
