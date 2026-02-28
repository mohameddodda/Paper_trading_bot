#!/usr/bin/env python3
"""
train_lstm.py – LSTM Training Script for AI Signals
=================================================

Trains an LSTM model on historical data for alpha signals in paper trading simulations.
Run: python train_lstm.py
Requires: pip install yfinance tensorflow scikit-learn (optional advanced deps in requirements.txt)

WARNING: This is for PAPER TRADING SIMULATIONS ONLY.
Do not use for real financial transactions or investment advice.
AI predictions are experimental and not guaranteed.
"""

import os
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib  # For saving scaler
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SYMBOLS, STOCK_MODE, CRYPTO_MODE, PROJECT_ROOT

# Paths for saving model/scaler
MODEL_PATH = PROJECT_ROOT / "checkpoints" / "lstm_model.h5"
SCALER_PATH = PROJECT_ROOT / "checkpoints" / "scaler.pkl"
os.makedirs(MODEL_PATH.parent, exist_ok=True)

def fetch_training_data(symbols: list = SYMBOLS, period: str = '1y') -> pd.DataFrame:
    """
    Fetches historical data for training.

    Args:
        symbols (list): List of symbols.
        period (str): Data period (e.g., '1y' for 1 year).

    Returns:
        pd.DataFrame: Close prices.
    """
    try:
        if STOCK_MODE:
            data = yf.download(symbols, period=period)['Close']
        elif CRYPTO_MODE:
            # Convert to yfinance format (e.g., BTC_USDT -> BTC-USD)
            crypto_symbols = [s.replace('_', '-') for s in symbols]
            data = yf.download(crypto_symbols, period=period)['Close']
        else:
            raise ValueError("Invalid mode in config.py")
        
        data = data.dropna()
        if data.empty:
            raise ValueError("No data fetched. Check symbols or network.")
        print(f"✅ Fetched data for {len(symbols)} symbols, shape: {data.shape}")
        return data
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()

def create_dataset(ds: np.ndarray, lookback: int = 60) -> tuple:
    """
    Creates X, y datasets for LSTM.

    Args:
        ds (np.ndarray): Scaled data.
        lookback (int): Lookback window.

    Returns:
        tuple: X, y arrays.
    """
    X, y = [], []
    for i in range(lookback, len(ds)):
        X.append(ds[i-lookback:i])
        y.append(ds[i])
    return np.array(X), np.array(y)

def build_lstm_model(input_shape: tuple) -> Sequential:
    """
    Builds the LSTM model.

    Args:
        input_shape (tuple): Shape of input data.

    Returns:
        Sequential: Compiled model.
    """
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def train_and_save_model(data: pd.DataFrame, epochs: int = 50, batch_size: int = 32) -> None:
    """
    Trains and saves the LSTM model.

    Args:
        data (pd.DataFrame): Training data.
        epochs (int): Training epochs.
        batch_size (int): Batch size.
    """
    try:
        # Scale data
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(data.values.reshape(-1, 1))

        # Create dataset
        X, y = create_dataset(scaled)
        num_features = data.shape[1] if data.shape[1] > 1 else 1
        X = X.reshape((X.shape[0], X.shape[1], num_features))

        # Build and train model
        model = build_lstm_model((X.shape[1], num_features))
        history = model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=1)

        # Validate
        predictions = model.predict(X)
        mse = mean_squared_error(y, predictions)
        print(f"✅ Model trained! Validation MSE: {mse:.4f}")
        print(f"Final training loss: {history.history['loss'][-1]:.4f}")

        # Save
        model.save(str(MODEL_PATH))
        joblib.dump(scaler, str(SCALER_PATH))
        print(f"✅ Model saved to {MODEL_PATH}")
        print(f"✅ Scaler saved to {SCALER_PATH}")
        print("💡 Load in bot.py's TradingStrategy for AI signals!")

    except Exception as e:
        print(f"❌ Training failed: {e}")

def main():
    """Main training function."""
    print("🚀 Starting LSTM Training for Paper Trading AI...")
    data = fetch_training_data()
    if data.empty:
        print("❌ No data available. Aborting.")
        return
    train_and_save_model(data)

if __name__ == "__main__":
    main()
