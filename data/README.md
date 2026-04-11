# Data Directory Structure
This directory stores all persistent bot data.

## Files/Folders:
- `trades.db` → SQLite database for trade history
- `logs/`     → Bot activity logs (rotated daily)
- `history/`  → Price history CSV files (hourly snapshots)
- `exports/`  → Performance report exports (PDF/CSV charts)

**Auto-created by `scripts/setup_dirs.py` on startup.**

