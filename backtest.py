import pandas as pd
from polygon import RESTClient
from config import *
from bot import PaperTradingBot
import logging

logging.basicConfig(level="INFO")

def fetch_historical(symbol, days=BACKTEST_DAYS):
    client = RESTClient(POLYGON_API_KEY)
    end = pd.Timestamp.now(tz='UTC')
    start = end - pd.Timedelta(days=days)
    aggs = client.get_aggs(symbol, multiplier=1, timespan="minute", from_=start, to=end)
    df = pd.DataFrame(aggs)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def run_backtest():
    bot = PaperTradingBot()
    bot.history = {}
    bot.portfolio = {sym: 0.0 for sym in SYMBOLS}
    bot.portfolio["USD"] = STARTING_CASH

    for sym in SYMBOLS:
        df = fetch_historical(sym)
        bot.history[sym] = df[['timestamp', 'close']].rename(columns={'close': 'price'}).to_dict('records')

    # Simulate tick-by-tick
    max_len = max(len(bot.history[sym]) for sym in SYMBOLS)
    for i in range(0, max_len, 10):
        for sym in SYMBOLS:
            if i < len(bot.history[sym]):
                price = bot.history[sym][i]['price']
                bot.history[sym] = bot.history[sym][:i+1]  # simulate live history

        # Decision & trade
        for sym in SYMBOLS:
            action = bot.rule_based_decision(sym) if not USE_RL else bot.rl_decision(sym)
            if action != "hold":
                bot.execute_trade(sym, action, amount_usd=50)

    # Final value
    final = bot.portfolio["USD"]
    for sym in SYMBOLS:
        price = bot.history[sym][-1]['price']
        final += bot.portfolio[sym] * price
    logging.info(f"Backtest Final Net Worth: ${final:,.2f}")

if __name__ == "__main__":
    run_backtest()