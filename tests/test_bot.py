import unittest
from bot import PaperTradingBot   # <-- change if your class name is different

class TestBotBasics(unittest.TestCase):
    def setUp(self):
        self.bot = PaperTradingBot(balance=1000)

    def test_initial_balance(self):
        self.assertEqual(self.bot.balance, 1000)

    def test_portfolio_empty(self):
        self.assertEqual(self.bot.portfolio, {})

if __name__ == '__main__':
    unittest.main()