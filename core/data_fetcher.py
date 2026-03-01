# Copyright 2026 Mohamed Dodda
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
data_fetcher.py – Market Data Fetching Module
=============================================

Fetches real-time and historical price data for stocks and crypto.
- Stocks: Uses Yahoo Finance (yfinance)
- Crypto: Uses Crypto.com public API

For educational paper trading simulations only.
No real money involved.
"""

import time
import logging
from typing import Dict, List, Optional
import pandas as pd
import requests
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SYMBOLS,
    STOCK_MODE,
    CRYPTO_MODE,
    LOG_FILE,
)

# API timeout
API_TIMEOUT = 10

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    filename=LOG_FILE,
)
log = logging.getLogger(__name__)

# Price cache for performance
_price_cache: Dict[str, float] = {}
_cache_timestamp: float = 0
_CACHE_TTL: float = 5  # Cache prices for 5 seconds


def _get_crypto_prices() -> Dict[str, float]:
    """
    Fetch live crypto prices from Crypto.com public API.
    No API key required.
    """
    global _price_cache, _cache_timestamp
    
    try:
        response = requests.get(
            "https://api.crypto.com/exchange/v1/public/get-tickers",
            timeout=API_TIMEOUT,
            headers={'User-Agent': 'PaperTradingBot/3.0.0'}
        )
        response.raise_for_status()
        data = response.json()
        
        prices = {}
        for item in data.get("result", {}).get("data", []):
            if 'i' in item and 'a' in item:
                symbol = item['i']
                price = float(item['a'])
                prices[symbol] = price
        
        _price_cache.update(prices)
        _cache_timestamp = time.time()
        return prices
        
    except Exception as e:
        log.error(f"Crypto price fetch error: {e}")
        # Return cached prices as fallback
        return _price_cache.copy()


def _get_stock_prices() -> Dict[str, float]:
    """
    Fetch live stock prices from Yahoo Finance (yfinance).
    """
    global _price_cache, _cache_timestamp
    
    try:
        import yfinance as yf
        
        prices = {}
        for symbol in SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                # Get fast info - this is more reliable
                info = ticker.fast_info
                if info and hasattr(info, 'last_price'):
                    prices[symbol] = info.last_price
                else:
                    # Fallback to regular price
                    hist = ticker.history(period="1d", interval="1m")
                    if not hist.empty:
                        prices[symbol] = hist['Close'].iloc[-1]
                    else:
                        log.warning(f"No data for {symbol}")
            except Exception as e:
                log.error(f"Error fetching {symbol}: {e}")
        
        _price_cache.update(prices)
        _cache_timestamp = time.time()
        return prices
        
    except ImportError:
        log.error("yfinance not installed. Install with: pip install yfinance")
        return {}
    except Exception as e:
        log.error(f"Stock price fetch error: {e}")
        return _price_cache.copy()


def get_live_price(symbol: str) -> Optional[float]:
    """
    Get live price for a single symbol.
    
    Args:
        symbol: Stock ticker or crypto pair (e.g., 'AAPL' or 'BTC_USDT')
    
    Returns:
        Current price as float, or None if unavailable
    """
    if CRYPTO_MODE:
        prices = _get_crypto_prices()
        return prices.get(symbol)
    elif STOCK_MODE:
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            if info and hasattr(info, 'last_price'):
                return info.last_price
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                return hist['Close'].iloc[-1]
        except Exception as e:
            log.error(f"Error fetching {symbol}: {e}")
    return None


def fetch_all_prices() -> Dict[str, float]:
    """
    Fetch all prices for configured symbols.
    Uses caching to avoid rate limiting.
    
    Returns:
        Dictionary of symbol -> price
    """
    global _cache_timestamp
    
    # Use cache if recent
    if time.time() - _cache_timestamp < _CACHE_TTL and _price_cache:
        return _price_cache.copy()
    
    if CRYPTO_MODE:
        return _get_crypto_prices()
    elif STOCK_MODE:
        return _get_stock_prices()
    
    return {}


def fetch_data_for_symbols(
    period: str = "1mo",
    interval: str = "1d"
) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical data for all configured symbols.
    
    Args:
        period: Time period (e.g., "1d", "1mo", "1y")
        interval: Data interval (e.g., "1m", "1h", "1d")
    
    Returns:
        Dictionary of symbol -> DataFrame with OHLCV data
    """
    data = {}
    
    if CRYPTO_MODE:
        data = _fetch_crypto_history(period, interval)
    elif STOCK_MODE:
        data = _fetch_stock_history(period, interval)
    
    return data


def _fetch_crypto_history(
    period: str = "1mo",
    interval: str = "1d"
) -> Dict[str, pd.DataFrame]:
    """Fetch historical crypto data from Crypto.com API."""
    data = {}
    
    for symbol in SYMBOLS:
        try:
            # Convert BTC_USDT to BTC-USDT for API
            instrument = symbol.replace("_", "-")
            
            # Map interval to API timeframe
            timeframe_map = {
                "1m": "1m",
                "5m": "5m", 
                "15m": "15m",
                "1h": "1h",
                "4h": "4h",
                "1d": "1d",
            }
            timeframe = timeframe_map.get(interval, "1d")
            
            # Calculate count based on period
            period_days = {
                "1d": 1,
                "5d": 5,
                "1mo": 30,
                "3mo": 90,
                "6mo": 180,
                "1y": 365,
                "2y": 730,
            }
            days = period_days.get(period, 30)
            count = min(days * 24 * 60, 2000)  # Max 2000 candles
            
            url = "https://api.crypto.com/v2/public/get-candlestick"
            params = {
                "instrument_name": instrument,
                "timeframe": timeframe,
                "count": count,
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0 and result.get("result", {}).get("data"):
                df = pd.DataFrame(result["result"]["data"])
                df["t"] = pd.to_datetime(df["t"], unit="s", utc=True)
                df = df.rename(columns={
                    "t": "timestamp",
                    "o": "Open",
                    "h": "High", 
                    "l": "Low",
                    "c": "Close",
                    "v": "Volume"
                })
                df = df[["timestamp", "Open", "High", "Low", "Close", "Volume"]]
                df = df.sort_values("timestamp").reset_index(drop=True)
                data[symbol] = df
                log.info(f"Fetched {len(df)} candles for {symbol}")
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            log.error(f"Error fetching {symbol}: {e}")
    
    return data


def _fetch_stock_history(
    period: str = "1mo",
    interval: str = "1d"
) -> Dict[str, pd.DataFrame]:
    """Fetch historical stock data from Yahoo Finance."""
    data = {}
    
    try:
        import yfinance as yf
    except ImportError:
        log.error("yfinance not installed")
        return data
    
    for symbol in SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty:
                df = df.reset_index()
                if df.columns[0] == 'Date':
                    df = df.rename(columns={'Date': 'timestamp'})
                elif 'Datetime' in df.columns:
                    df = df.rename(columns={'Datetime': 'timestamp'})
                
                # Ensure we have the right columns
                df = df[['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
                data[symbol] = df
                log.info(f"Fetched {len(df)} candles for {symbol}")
            else:
                log.warning(f"No data for {symbol}")
                
        except Exception as e:
            log.error(f"Error fetching {symbol}: {e}")
    
    return data


def clear_cache():
    """Clear the price cache."""
    global _price_cache, _cache_timestamp
    _price_cache = {}
    _cache_timestamp = 0
