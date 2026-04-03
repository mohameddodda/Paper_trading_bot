import pytest
import sqlite3
from core.db_manager import db_manager

def test_init_db():
    """Test database initialization creates tables."""
    db_manager.init_db()
    
    conn = sqlite3.connect('paper_trading.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'trade_history' in tables
    assert 'bot_state' in tables
    conn.close()

def test_log_trade():
    """Test logging a trade and retrieving it."""
    db_manager.log_trade(
        symbol='BTCUSDT',
        trade_type='BUY',
        price=50000.0,
        qty=0.01,
        pnl_pct=0.0,
        balance_after=999500.0,
        reason='Test buy',
        strategy='test'
    )
    
    trades = db_manager.get_trades(symbol='BTCUSDT', limit=1)
    assert len(trades) >= 1
    trade = trades[0]
    assert trade['symbol'] == 'BTCUSDT'
    assert trade['type'] == 'BUY'
    assert abs(trade['price'] - 50000.0) < 0.01
    assert abs(trade['qty'] - 0.01) < 0.001
    assert trade['strategy'] == 'test'

def test_get_trades_filter():
    """Test filtering trades by symbol."""
    trades = db_manager.get_trades(symbol='BTCUSDT', limit=5)
    assert all(t['symbol'] == 'BTCUSDT' for t in trades)

def test_trade_stats():
    """Test trade statistics calculation."""
    stats = db_manager.get_trade_stats()
    assert 'total_trades' in stats
    assert stats['total_trades'] >= 0
    assert stats['avg_pnl_pct'] is not None

def test_save_load_state():
    """Test saving and loading bot state."""
    state_data = {
        'balance': 950000.0,
        'equity': 975000.0,
        'open_positions': {'BTCUSDT': 0.02}
    }
    
    db_manager.save_state(
        balance=state_data['balance'],
        equity=state_data['equity'],
        open_positions=state_data['open_positions']
    )
    
    loaded = db_manager.load_latest_state()
    assert loaded is not None
    assert abs(loaded['balance'] - state_data['balance']) < 0.01

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup test data after each test."""
    yield
    conn = sqlite3.connect('paper_trading.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trade_history WHERE reason LIKE "%Test%" OR strategy="test"')
    cursor.execute('DELETE FROM bot_state WHERE config_hash=""')  # Assuming test states have empty config_hash
    conn.commit()
    conn.close()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

