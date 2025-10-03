"""
Data collection modules for scraping stock data from various sources
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time


class YahooFinanceCollector:
    """Collect stock data from Yahoo Finance API"""
    
    def __init__(self):
        self.name = "Yahoo Finance"
    
    def get_stock_data(self, symbol: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a given symbol
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y')
        
        Returns:
            DataFrame with stock data or None if error
        """
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching data from {self.name}: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get comprehensive stock information
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with stock info or None if error
        """
        try:
            stock = yf.Ticker(symbol)
            return stock.info
        except Exception as e:
            print(f"Error fetching info from {self.name}: {e}")
            return None
    
    def get_recommendations(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Get analyst recommendations
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            DataFrame with recommendations or None if error
        """
        try:
            stock = yf.Ticker(symbol)
            return stock.recommendations
        except Exception as e:
            print(f"Error fetching recommendations from {self.name}: {e}")
            return None


class NewsCollector:
    """Collect news sentiment data related to stocks"""
    
    def __init__(self):
        self.name = "News Collector"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_stock_news(self, symbol: str) -> List[Dict]:
        """
        Get recent news about a stock
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            List of news articles with title, date, and link
        """
        try:
            stock = yf.Ticker(symbol)
            news = stock.news
            return news if news else []
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def analyze_sentiment(self, news_items: List[Dict]) -> str:
        """
        Basic sentiment analysis on news headlines
        
        Args:
            news_items: List of news items
            
        Returns:
            Sentiment: 'positive', 'negative', or 'neutral'
        """
        if not news_items:
            return 'neutral'
        
        # Simple keyword-based sentiment analysis
        positive_keywords = ['surge', 'gain', 'profit', 'growth', 'rise', 'bullish', 
                            'strong', 'beat', 'exceed', 'up', 'high', 'soar']
        negative_keywords = ['drop', 'fall', 'loss', 'decline', 'bearish', 'weak',
                            'miss', 'down', 'low', 'crash', 'plunge', 'struggle']
        
        positive_count = 0
        negative_count = 0
        
        for item in news_items[:10]:  # Analyze last 10 news items
            title = item.get('title', '').lower()
            for keyword in positive_keywords:
                if keyword in title:
                    positive_count += 1
            for keyword in negative_keywords:
                if keyword in title:
                    negative_count += 1
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'


class MarketDataCollector:
    """Collect broader market data and indicators"""
    
    def __init__(self):
        self.name = "Market Data Collector"
    
    def get_market_indices(self) -> Dict[str, float]:
        """
        Get major market indices data
        
        Returns:
            Dictionary with index symbols and their current values
        """
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^VIX': 'Volatility Index'
        }
        
        results = {}
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                if not hist.empty:
                    results[name] = hist['Close'].iloc[-1]
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                results[name] = None
        
        return results
    
    def get_sector_performance(self, symbol: str) -> Optional[str]:
        """
        Get the sector of a stock
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Sector name or None
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return info.get('sector', None)
        except Exception as e:
            print(f"Error fetching sector: {e}")
            return None
