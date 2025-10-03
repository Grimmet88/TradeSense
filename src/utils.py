"""
Utility functions for TradeSense application.
Helper functions for data loading, formatting, and common operations.
"""

import os
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta


def load_tickers(filepath: str = "data/tickers.csv") -> List[str]:
    """
    Load stock tickers from CSV file.
    
    Args:
        filepath: Path to the tickers CSV file
        
    Returns:
        List of ticker symbols
    """
    try:
        df = pd.read_csv(filepath)
        return df['ticker'].tolist()
    except FileNotFoundError:
        print(f"Warning: {filepath} not found. Using default tickers.")
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]


def get_date_range(days_back: int = 30) -> tuple:
    """
    Get start and end dates for historical data.
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        Tuple of (start_date, end_date) as strings
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def format_currency(value: float) -> str:
    """
    Format number as currency.
    
    Args:
        value: Numeric value to format
        
    Returns:
        Formatted currency string
    """
    return f"${value:,.2f}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def validate_ticker(ticker: str) -> bool:
    """
    Validate if a ticker symbol is properly formatted.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False
    return ticker.isupper() and ticker.isalpha() and 1 <= len(ticker) <= 5


def create_result_dict(
    ticker: str,
    price_data: pd.DataFrame = None,
    sentiment: Dict[str, Any] = None,
    forecast: pd.DataFrame = None,
    recommendation: str = None
) -> Dict[str, Any]:
    """
    Create standardized result dictionary.
    
    Args:
        ticker: Stock ticker symbol
        price_data: Historical price data
        sentiment: Sentiment analysis results
        forecast: Forecast data
        recommendation: Trading recommendation
        
    Returns:
        Dictionary containing all results
    """
    results = {"ticker": ticker, "timestamp": datetime.now().isoformat()}
    
    if price_data is not None:
        results["price_data"] = price_data
    if sentiment is not None:
        results["sentiment"] = sentiment
    if forecast is not None:
        results["forecast"] = forecast
    if recommendation is not None:
        results["recommendation"] = recommendation
        
    return results
