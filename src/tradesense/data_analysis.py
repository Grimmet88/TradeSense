# File: data_analysis.py
# Description: Loads data, performs basic quantitative analysis, and saves visualizations.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration variables
INPUT_FILE = "trade_data.pkl"
OUTPUT_PLOT_CLOSE = "close_price_and_sma.png"
OUTPUT_PLOT_RETURNS = "daily_returns_histogram.png"

def analyze_and_plot_data():
    """
    Loads historical data, calculates returns, prints statistics,
    and generates two key visualizations using Matplotlib and Seaborn.
    """
    # Check if the data file from data_fetcher.py exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at {INPUT_FILE}. Please run data_fetcher.py first.")
        return

    print(f"-> Loading data from {INPUT_FILE}...")
    data = pd.read_pickle(INPUT_FILE)

    # 1. Calculate Daily Returns
    data['Daily_Return'] = data['Close'].pct_change()
    print("\n--- Descriptive Statistics for Daily Returns ---")
    print(data['Daily_Return'].describe())

    # 2. Visualize Closing Price and SMA (Moving Average)
    # Uses Matplotlib for figure setup and Pandas plot functionality
    plt.figure(figsize=(12, 6))
    data[['Close', 'SMA_20']].plot(ax=plt.gca(), title='Closing Price and 20-Day Simple Moving Average (SMA)')
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(OUTPUT_PLOT_CLOSE)
    print(f"\n-> Closing Price/SMA plot saved to {OUTPUT_PLOT_CLOSE}")
    plt.close() # Close figure to free up memory

    # 3. Visualize Daily Returns Distribution (Histogram)
    # Uses Seaborn for an enhanced statistical visualization
    plt.figure(figsize=(8, 6))
    sns.histplot(data['Daily_Return'].dropna(), bins=100, kde=True)
    plt.title("Daily Returns Distribution")
    plt.xlabel("Daily Return")
    plt.ylabel("Frequency")
    plt.savefig(OUTPUT_PLOT_RETURNS)
    print(f"-> Daily Returns Histogram saved to {OUTPUT_PLOT_RETURNS}")
    plt.close() # Close figure

    print("\nAnalysis complete. Check your directory for the saved PNG files.")


if __name__ == "__main__":
    # Configure matplotlib to use a clean, professional style
    plt.style.use('seaborn-v0_8-whitegrid')
    analyze_and_plot_data()

