import yfinance as yf
import pandas as pd
import numpy as np # Although not directly used for the bug fix, good to keep for future numerical operations

# --- Configuration Constants ---
DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'SMCI', 'AMD'] # List of tickers to scan
DEFAULT_START_DATE = '2023-01-01' # Will be made configurable later
DEFAULT_END_DATE = '2023-12-31'   # Will be made configurable later
SHORT_MA_WINDOW = 50
LONG_MA_WINDOW = 200
DAYS_TO_CONSIDER_RECENT_SIGNAL = 5 # How many days back to look for a recent signal

# --- Functions ---

def get_stock_data(ticker, start, end):
    """
    Fetches historical stock data for a given ticker and date range.
    Handles potential errors during data retrieval.
    """
    try:
        # Fetch an extra 'long_window' worth of data to ensure MAs are calculated correctly from the start_date
        # The calculation needs data prior to the actual start date for the first MA values to be valid.
        lookback_offset_days = LONG_MA_WINDOW * 2 # Or any sufficiently large number
        actual_fetch_start = pd.to_datetime(start) - pd.DateOffset(days=lookback_offset_days)
        
        # Ensure we don't try to fetch data from before yfinance's typical earliest date (e.g., 1990-01-01)
        earliest_possible_date = pd.to_datetime('1990-01-01')
        if actual_fetch_start < earliest_possible_date:
            actual_fetch_start = earliest_possible_date
            
        data = yf.download(ticker, start=actual_fetch_start.strftime('%Y-%m-%d'), end=end, auto_adjust=True)

        if data.empty:
            print(f"No data found for {ticker} in the specified date range: {actual_fetch_start.strftime('%Y-%m-%d')} to {end}.")
            return None
        
        # Now trim the data to the original requested start date
        data = data[data.index >= pd.to_datetime(start)]
        
        if data.empty: # Check again after trimming if there's any data left for the actual period
            print(f"No sufficient data for {ticker} in the specified date range after MA calculation window.")
            return None
        
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Removed calculate_moving_averages function as it's now integrated into generate_signals

def generate_signals(data, short_window=SHORT_MA_WINDOW, long_window=LONG_MA_WINDOW, days_to_consider_recent=DAYS_TO_CONSIDER_RECENT_SIGNAL):
    """
    Generates 'Buy', 'Sell', or 'Hold' signals based on MA crossovers.
    Only considers the most recent signals within 'days_to_consider_recent' period.
    Returns the signal string and the latest valid data point (as a Series).
    """
    if data is None or data.empty:
        return 'N/A (No Data)', pd.Series()

    # Calculate MAs directly within this function
    data['short_ma'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    data['long_ma'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

    # Calculate raw buy/sell signals (True/False series)
    data['Buy_Signal_Raw'] = ((data['short_ma'].shift(1) < data['long_ma'].shift(1)) &
                              (data['short_ma'] > data['long_ma']))
    data['Sell_Signal_Raw'] = ((data['short_ma'].shift(1) > data['long_ma'].shift(1)) &
                               (data['short_ma'] < data['long_ma']))

    # Ensure that MAs are not NaN at the latest point by dropping rows with NaN MAs
    # and then taking the last row. This ensures valid comparisons.
    processed_data = data.dropna(subset=['short_ma', 'long_ma'])

    if processed_data.empty:
        return 'N/A (No Valid MA)', pd.Series() # Return an empty series if no valid MAs

    latest_data_point = processed_data.iloc[-1] # This is a Series representing the last row

    current_signal = 'HOLD' # Initialize for the return value

    # Since we dropped NA MAs, these should be valid.
    # Check for NaN values in MAs as a safeguard, though it should be handled by dropna
    if pd.isna(latest_data_point['short_ma']) or pd.isna(latest_data_point['long_ma']):
        current_signal = 'N/A (MA Invalid)'
    else:
        # Check for recent crossovers in the `recent_period_data`
        recent_period_data = processed_data.tail(days_to_consider_recent)
        
        last_buy_date = recent_period_data[recent_period_data['Buy_Signal_Raw']].index.max()
        last_sell_date = recent_period_data[recent_period_data['Sell_Signal_Raw']].index.max()

        if pd.isna(last_buy_date) and pd.isna(last_sell_date):
            # No recent crossover, determine hold based on current MA position
            # These values are now correctly scalar because latest_data_point is a single row Series
            if latest_data_point['short_ma'] > latest_data_point['long_ma']:
                current_signal = 'HOLD (Bullish)'
            elif latest_data_point['short_ma'] < latest_data_point['long_ma']:
                current_signal = 'HOLD (Bearish)'
            else: # MAs are very close or equal
                current_signal = 'HOLD'
        elif not pd.isna(last_buy_date) and (pd.isna(last_sell_date) or last_buy_date > last_sell_date):
            current_signal = 'BUY'
        elif not pd.isna(last_sell_date) and (pd.isna(last_buy_date) or last_sell_date > last_buy_date):
            current_signal = 'SELL'
            
    return current_signal, latest_data_point


def calculate_confidence(data, latest_data_point, signal_type):
    """
    Calculates a confidence level for a given signal.
    This is a basic placeholder and should be expanded significantly.
    Factors:
    1. Distance between MAs (wider gap = stronger trend)
    2. Volume (higher volume at crossover = stronger signal)
    3. Price action relative to MAs (e.g., price above short MA for buy)
    """
    if data is None or data.empty or latest_data_point.empty or signal_type.startswith('N/A'):
        return 'Very Low'
    
    # These are already scalar values from latest_data_point.iloc[-1]
    ma_difference = abs(latest_data_point['short_ma'] - latest_data_point['long_ma']) 
    
    # Avoid division by zero if std_dev is 0 or NaN (e.g., for very short data)
    std_dev = data['Close'].std()
    
    if std_dev == 0 or pd.isna(std_dev) or std_dev < 0.001: # Add a small threshold
        ma_diff_ratio = 0 # No volatility to compare against
    else:
        ma_diff_ratio = ma_difference / std_dev

    # Let's adjust confidence based on the MA difference ratio
    if ma_diff_ratio > 1.0: # MAs are very spread (strong trend)
        return 'High'
    elif ma_diff_ratio > 0.5: # MAs are moderately spread
        return 'Medium'
    elif ma_diff_ratio > 0.2: # MAs are slightly spread but still separated
        return 'Low'
    else: # MAs are very close or intertwined
        return 'Very Low'
