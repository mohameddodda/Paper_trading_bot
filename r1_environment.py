import gymnasium as gym
import numpy as np
from tensortrade.env.default import TradingEnv
from tensortrade.feed.core import Stream, DataFeed
from tensortrade.oms.exchanges import Exchange
from tensortrade.oms.wallets import Wallet, Portfolio
from tensortrade.oms.instruments import Instrument
from tensortrade.oms.orders import proportion_order
from polygon import RESTClient
from config import POLYGON_API_KEY, SYMBOLS

# Instruments
USD = Instrument("USD", 2, "U.S. Dollar")
CRYPTO = {sym.split("_")[0]: Instrument(sym.split("_")[0], 8, sym.split("_")[0]) for sym in SYMBOLS}

class PolygonExchange(Exchange):
    def __init__(self, api_key: str):
        super().__init__(base_instrument=USD, default=True)
        self.client = RESTClient(api_key)

    def _get_price(self, symbol: str) -> float:
        try:
            resp = self.client.get_last_trade(symbol)
            return float(resp.last.price) if resp and resp.last else 0.0
        except:
            return 0.0

    def quote_price(self, instrument: Instrument, quote: Instrument = USD) -> float:
        if instrument == USD:
            return 1.0
        symbol = f"{instrument.symbol}_USD"
        return self._get_price(symbol)

def create_tensortrade_env(symbol: str = "BTC", window_size: int = 20):
    exchange = PolygonExchange(POLYGON_API_KEY)
    
    # Wallets
    cash = Wallet(exchange, STARTING_CASH * USD)
    asset = Wallet(exchange, 0 * CRYPTO[symbol])
    portfolio = Portfolio(USD, [cash, asset])

    # Price stream
    price_stream = Stream.source(
        lambda: exchange.quote_price(CRYPTO[symbol]), dtype="float"
    ).rename(f"{symbol.lower()}_usd")

    feed = DataFeed([price_stream])

    env = TradingEnv(
        portfolio=portfolio,
        feed=feed,
        action_scheme="managed-risk",
        reward_scheme="risk-adjusted",
        window_size=window_size
    )
    return env

class RLTradingEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, symbol: str = "BTC", window_size: int = 20):
        self.tt_env = create_tensortrade_env(symbol, window_size)
        self.window_size = window_size
        self.observation_space = gym.spaces.Box(low=0, high=1e10, shape=(window_size,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(3)  # 0=hold, 1=buy, 2=sell

    def reset(self, **kwargs):
        obs = self.tt_env.reset()
        return np.array(obs["price"][-self.window_size:]).astype(np.float32)

    def step(self, action):
        order = None
        if action == 1:
            order = proportion_order(self.tt_env.portfolio, "buy", 0.1)
        elif action == 2:
            order = proportion_order(self.tt_env.portfolio, "sell", 0.1)

        obs, reward, done, info = self.tt_env.step(order)
        price_obs = np.array(obs["price"][-self.window_size:]).astype(np.float32)
        return price_obs, reward, done, False, info

    def render(self):
        print(f"Net Worth: {self.tt_env.portfolio.net_worth:,.2f} USD")