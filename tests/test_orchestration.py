import pytest
from core.bot_orchestrator import BotOrchestrator
from bots.beast_bot import BeastBot
from unittest.mock import Mock, patch, MagicMock

@pytest.fixture
def orchestrator():
    orch = BotOrchestrator(num_bots=1, db_path=':memory:')
    orch.bots = {'test_bot': Mock()}
    orch.threads = [Mock()]
    return orch

def test_health_check(orchestrator):
    # Mock thread alive
    orchestrator.threads[0].is_alive.return_value = True
    health = orchestrator.health_check()
    assert health['active_bots'] == 1

def test_shared_balance_update(orchestrator, mocker):
    mocker.patch.object(orchestrator.db_manager, 'get_recent_trades', return_value [{'pnl': 100}])
    orchestrator._health_check()
    assert orchestrator.shared_balance > 10000

def test_create_bot(orchestrator):
    bot = orchestrator.create_bot('beast')
    assert isinstance(bot, BeastBot)
    assert hasattr(bot, 'bot_id')

@patch('threading.Thread')
def test_start(mock_thread, orchestrator):
    orchestrator.start()
    mock_thread.assert_called()

@patch('core.bot_orchestrator.threading.Thread.join')
def test_stop(mock_join, orchestrator):
    orchestrator.stop()
    mock_join.assert_called()

def test_multi_bot(orchestrator):
    orch = BotOrchestrator(num_bots=2)
    orch.start()
    assert len(orch.bots) == 2

if __name__ == '__main__':
    pytest.main([__file__])

