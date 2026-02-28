# Desktop App Conversion Plan

## Task: Convert CLI bot to desktop app with native window experience

### Steps:
1. [x] Create `gui_app.py` - Desktop GUI using customtkinter
2. [x] Modify `bot.py` - Add GUI mode with thread communication
3. [x] Update `requirements.txt` - Add customtkinter dependency
4. [ ] Test the desktop app

### Details:
- gui_app.py: Modern CTk window with portfolio dashboard, trade log, controls
- bot.py: Add --gui flag, run in background thread, queue-based updates
- requirements.txt: Add customtkinter>=5.2.0
