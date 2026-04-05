# Copyright 2026 Mohamed Dodda - Updated April 2, 2026
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
db_manager.py - SQLite Database Manager
=======================================

Provides persistent storage for:
- trade_history: All executed trades
- bot_state: Balance snapshots, equity curves, open positions

Thread-safe singleton pattern. Uses WAL mode for concurrency.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import os

try:
    from config.settings import DB_PATH
except ImportError:
    DB_PATH = 'paper_trading.db'

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _lock = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.conn = None
        self._initialized = True

    @contextmanager
    def get_connection(self):
        """Context manager for thread-safe DB connections."""
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        conn.execute('PRAGMA cache_size=10000;')
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """Initialize database tables if they don't exist."""
        with self.get_connection() as conn:
            # Trade history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trade_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('BUY', 'SELL')),
                    price REAL NOT NULL,
                    qty REAL NOT NULL,
                    pnl_pct REAL DEFAULT 0,
                    balance_after REAL NOT NULL,
                    reason TEXT,
                    strategy TEXT DEFAULT 'unknown'
                )
            ''')

            # Bot state snapshots
            conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    balance REAL NOT NULL,
                    equity REAL NOT NULL,
                    open_positions TEXT,  -- JSON: {symbol: qty}
                    total_trades INTEGER DEFAULT 0,
                    config_hash TEXT
                )
            ''')

            # Index for faster queries
            conn.execute('CREATE INDEX IF NOT EXISTS idx_trades_symbol_time ON trade_history(symbol, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_state_time ON bot_state(timestamp)')

        log.info(f"Database initialized at {DB_PATH}")

    def log_trade(self, symbol: str, trade_type: str, price: float, qty: float, 
                  pnl_pct: float = 0.0, balance_after: float = 0.0, 
                  reason: str = '', strategy: str = 'unknown'):
        """Log a completed trade."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO trade_history (symbol, type, price, qty, pnl_pct, balance_after, reason, strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, trade_type, price, qty, pnl_pct, balance_after, reason, strategy))
        log.info(f"Logged {trade_type} {qty:.4f} {symbol} @ ${price:.4f} (PnL: {pnl_pct:.2f}%)")

    def save_state(self, balance: float, equity: float, open_positions: Dict[str, float] = None,
                   total_trades: int = 0, config_hash: str = ''):
        """Save bot state snapshot."""
        open_pos_json = json.dumps(open_positions or {})
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO bot_state (balance, equity, open_positions, total_trades, config_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (balance, equity, open_pos_json, total_trades, config_hash))
        log.info(f"Saved state: Balance ${balance:.2f}, Equity ${equity:.2f}")

    def load_latest_state(self) -> Optional[Dict[str, Any]]:
        """Load most recent bot state."""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM bot_state ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            if row:
                return {
                    'balance': row[2],
                    'equity': row[3],
                    'open_positions': json.loads(row[4]) if row[4] else {},
                    'total_trades': row[5],
                    'config_hash': row[6]
                }
        return None

    def get_trades(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades, optionally filtered by symbol."""
        query = 'SELECT * FROM trade_history ORDER BY id DESC LIMIT ?'
        params = [limit]
        if symbol:
            query = 'SELECT * FROM trade_history WHERE symbol = ? ORDER BY id DESC LIMIT ?'
            params = [symbol, limit]
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_trade_stats(self, symbol: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for trades."""
        cutoff = datetime.now().strftime('%Y-%m-%d')
        where_clause = f"timestamp > '{cutoff}'" if days == 30 else ''
        if symbol:
            if where_clause:
                where_clause += f" AND symbol = '{symbol}'"
            else:
                where_clause = f"symbol = '{symbol}'"

        query = f'''
            SELECT 
                COUNT(*) as total_trades,
                AVG(pnl_pct) as avg_pnl,
                SUM(CASE WHEN pnl_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate_pct
            FROM trade_history 
            WHERE {where_clause if where_clause else '1=1'}
        '''
        
        with self.get_connection() as conn:
            cursor = conn.execute(query)
            row = cursor.fetchone()
            if row:
                return {
                    'total_trades': row[0],
                    'avg_pnl_pct': row[1] or 0,
                    'win_rate_pct': row[2] or 0
                }
            return {'total_trades': 0, 'avg_pnl_pct': 0, 'win_rate_pct': 0}

    def delete_all(self):
        """WARNING: Delete all data for testing (use carefully)."""
        with self.get_connection() as conn:
            conn.execute('DELETE FROM trade_history')
            conn.execute('DELETE FROM bot_state')
        log.warning("All data deleted from database")

# Global instance
db_manager = DatabaseManager()

if __name__ == "__main__":
    db_manager.init_db()
    print("Database manager ready. Tables created.")
    print("Run: sqlite3 paper_trading.db \".tables\" to verify.")

