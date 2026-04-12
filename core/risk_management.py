import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional
from core.db_manager import db_manager
from config.settings import MAX_DAILY_LOSS_PCT
import logging

log = logging.getLogger(__name__)

class RiskManager:
    """Portfolio kill-switch and risk management."""
    
    def __init__(self):
        self.daily_start_balance = 0
        self.reset_daily_balance()

    def reset_daily_balance(self):
        """Reset daily tracking at market open."""
        self.daily_start_balance = db_manager.get_trade_stats(days=1)['balance'] or 1000000.0
        
    def current_drawdown_pct(self) -> float:
        """Get current daily drawdown percentage."""
        stats = db_manager.get_trade_stats(days=1)
        current_balance = stats['balance']
        return (current_balance - self.daily_start_balance) / self.daily_start_balance

    def should_halt(self) -> bool:
        """Check if trading should halt due to risk limits."""
        drawdown = self.current_drawdown_pct()
        if drawdown <= -MAX_DAILY_LOSS_PCT:
            log.warning(f"🚨 DAILY DRAWDOWN LIMIT HIT ({drawdown:.1%}) — Trading halted")
            return True
        return False

# Global instance
risk_manager = RiskManager()

if __name__ == "__main__":
    print(f"Daily start balance: ${risk_manager.daily_start_balance:.2f}")

