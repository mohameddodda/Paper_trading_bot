import threading
import time
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
from core.db_manager import DBManager
from core.data_fetcher import DataFetcher
from core.strategy import TradingStrategy
from bots.beast_bot import BeastBot
# Note: Import other bots as needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotOrchestrator:
    def __init__(self, db_path: str = 'paper_trading.db', num_bots: int = 2, bot_types: List[str] = None):
        self.db_manager = DBManager(db_path)
        self.data_fetcher = DataFetcher()
        self.strategy = TradingStrategy()
        self.num_bots = num_bots
        self.bot_types = bot_types or ['cli', 'beast']
        self.bots: Dict[str, Any] = {}
        self.threads: List[threading.Thread] = []
        self.lock = threading.Lock()
        self.running = False
        self.shared_balance = 10000.0  # Shared virtual portfolio
        self.bot_id_counter = 0

    def create_bot(self, bot_type: str) -> Any:
        bot_id = f"bot_{self.bot_id_counter}"
        self.bot_id_counter += 1
        if bot_type == 'beast':
            bot = BeastBot(self.db_manager, self.data_fetcher, self.strategy, bot_id=bot_id)
        else:
            raise ValueError(f"Unknown bot type: {bot_type}")
        return bot

    def run_bot(self, bot: Any):
        try:
            bot.run()  # Assume bots have run() method for continuous trading loop
        except Exception as e:
            logger.error(f"Bot error: {e}")

    def start(self):
        logger.info(f"Starting orchestrator with {self.num_bots} bots: {self.bot_types}")
        self.running = True
        
        for i in range(self.num_bots):
            bot_type = self.bot_types[i % len(self.bot_types)]
            bot = self.create_bot(bot_type)
            self.bots[bot.bot_id if hasattr(bot, 'bot_id') else f"bot_{i}"] = bot
            
            thread = threading.Thread(target=self.run_bot, args=(bot,), daemon=True)
            self.threads.append(thread)
            thread.start()
            logger.info(f"Started {bot_type} bot: {bot}")
        
        # Health check loop
        while self.running:
            time.sleep(10)
            self._health_check()

    def health_check(self) -> dict:
        \"\"\"Public health check for monitoring.\"\"\"
        with self.lock:
            active = sum(1 for t in self.threads if t.is_alive())
            trades = self.db_manager.get_recent_trades(limit=100)
            total_pnl = sum(t.get('pnl', 0) for t in trades)
            return {
                'active_bots': active,
                'total_bots': len(self.threads),
                'shared_balance': self.shared_balance,
                'recent_pnl': total_pnl,
                'status': 'healthy' if active > 0 else 'idle'
            }

    def _health_check(self):
        health = self.health_check()
        logger.info(f"Health: {health}")
        self.shared_balance += sum(t.get('pnl', 0) for t in self.db_manager.get_recent_trades(limit=100))

    def stop(self):
        logger.info("Stopping orchestrator...")
        self.running = False
        for bot in self.bots.values():
            if hasattr(bot, 'stop'):
                bot.stop()
        for thread in self.threads:
            thread.join(timeout=5)

if __name__ == '__main__':
    orch = BotOrchestrator(num_bots=2)
    try:
        orch.start()
    except KeyboardInterrupt:
        orch.stop()

