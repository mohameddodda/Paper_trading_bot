from core.db_manager import db_manager
from core.data_fetcher import DataFetcher
from core.strategy import TradingStrategy

class CLIBot:
    def __init__(self, db_manager, data_fetcher, strategy, bot_id='cli'):
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher
        self.strategy = strategy
        self.bot_id = bot_id
        self.running = False

    def run(self):
        self.running = True
        print(f'{self.bot_id} CLI bot started')
        while self.running:
            # Simple CLI bot loop - no real trading for tests
            pass

    def stop(self):
        self.running = False
        print(f'{self.bot_id} CLI bot stopped')
