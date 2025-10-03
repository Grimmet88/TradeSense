# File: data_fetcher.py
# Description: Downloads historical stock data for analysis and saves it locally.

import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# --- Configuration ---
TICKER = "SPY" # S&P 500 ETF (or use any ticker, e.g., "AAPL" for Apple)
START_DATE = "2020-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d") # Today's date
OUTPUT_FILE = "trade_data.pkl"

def fetch_and_save_data():
    """
    Fetches historical stock data from Yahoo Finance and saves it as a
    pickle file.
    """
    print(f"-> Starting data download for {TICKER} from {START_DATE} to {END_DATE}")

    try:
        # 1. Download data
        data = yf.download(TICKER, start=START_DATE, end=END_DATE)

        if data.empty:
            print(f"Error: No data found for ticker {TICKER}.")
            return

        # 2. Add technical indicators (Simple Moving Average - 20 days)
        # This is a simple addition for later analysis
        data['SMA_20'] = data['Close'].rolling(window=20).mean()

        # 3. Save to disk (using pickle for efficient storage of pandas DataFrames)
        data.to_pickle(OUTPUT_FILE)

        print(f"-> Successfully downloaded and saved data to {OUTPUT_FILE}")
        print(f"   Shape of data saved: {data.shape}")

    except Exception as e:
        print(f"An error occurred during data fetching: {e}")

if __name__ == "__main__":
    fetch_and_save_data()

