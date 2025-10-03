"""
Web scraping functions for TradeSense.
Functions to scrape stock prices, news articles, and other relevant data.
"""

import requests
import yfinance as yf
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def fetch_stock_data(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Fetch historical stock price data using yfinance.
    
    Args:
        ticker: Stock ticker symbol
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
    Returns:
        DataFrame with historical price data
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {str(e)}")
        return pd.DataFrame()


def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Get detailed stock information.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing stock information
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "symbol": info.get("symbol", ticker),
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "52_week_high": info.get("fiftyTwoWeekHigh", 0),
            "52_week_low": info.get("fiftyTwoWeekLow", 0),
        }
    except Exception as e:
        print(f"Error fetching stock info for {ticker}: {str(e)}")
        return {}


def scrape_news_headlines(
    ticker: str,
    num_articles: int = 10
) -> List[Dict[str, str]]:
    """
    Scrape news headlines related to a stock ticker.
    
    Args:
        ticker: Stock ticker symbol
        num_articles: Number of articles to retrieve
        
    Returns:
        List of dictionaries containing headline and source
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:num_articles] if stock.news else []
        
        articles = []
        for item in news:
            articles.append({
                "title": item.get("title", ""),
                "publisher": item.get("publisher", "Unknown"),
                "link": item.get("link", ""),
                "published": datetime.fromtimestamp(
                    item.get("providerPublishTime", 0)
                ).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return articles
    except Exception as e:
        print(f"Error scraping news for {ticker}: {str(e)}")
        return []


def get_financial_statements(ticker: str) -> Dict[str, pd.DataFrame]:
    """
    Get financial statements for a stock.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing income statement, balance sheet, and cash flow
    """
    try:
        stock = yf.Ticker(ticker)
        return {
            "income_statement": stock.financials,
            "balance_sheet": stock.balance_sheet,
            "cash_flow": stock.cashflow
        }
    except Exception as e:
        print(f"Error fetching financial statements for {ticker}: {str(e)}")
        return {}


def get_current_price(ticker: str) -> Optional[float]:
    """
    Get the current/latest price for a stock.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Current price or None if unavailable
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
        return None
    except Exception as e:
        print(f"Error fetching current price for {ticker}: {str(e)}")
        return None


def get_market_movers(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top market movers (gainers/losers).
    Note: This is a placeholder implementation.
    
    Args:
        limit: Number of stocks to return
        
    Returns:
        List of dictionaries containing stock movement data
    """
    # This is a placeholder - in production, you'd use a proper API
    # or web scraping to get actual market movers
    print("Market movers functionality is a placeholder")
    return []
