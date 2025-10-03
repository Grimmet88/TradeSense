"""
Data aggregator to combine data from multiple sources
"""

from typing import Dict, Optional, List
import pandas as pd
from .data_collectors import YahooFinanceCollector, NewsCollector, MarketDataCollector


class DataAggregator:
    """Aggregates data from multiple sources for comprehensive stock analysis"""
    
    def __init__(self):
        self.yahoo_collector = YahooFinanceCollector()
        self.news_collector = NewsCollector()
        self.market_collector = MarketDataCollector()
    
    def collect_all_data(self, symbol: str, period: str = "1mo") -> Dict:
        """
        Collect all available data for a stock symbol
        
        Args:
            symbol: Stock ticker symbol
            period: Time period for historical data
            
        Returns:
            Dictionary containing all collected data
        """
        print(f"\n📊 Collecting data for {symbol}...")
        
        data = {
            'symbol': symbol.upper(),
            'timestamp': pd.Timestamp.now(),
            'historical_data': None,
            'stock_info': None,
            'analyst_recommendations': None,
            'news': None,
            'news_sentiment': 'neutral',
            'market_indices': None,
            'sector': None
        }
        
        # Collect historical price data
        print("  ├─ Fetching historical data...")
        data['historical_data'] = self.yahoo_collector.get_stock_data(symbol, period)
        
        # Collect stock information
        print("  ├─ Fetching stock information...")
        data['stock_info'] = self.yahoo_collector.get_stock_info(symbol)
        
        # Collect analyst recommendations
        print("  ├─ Fetching analyst recommendations...")
        data['analyst_recommendations'] = self.yahoo_collector.get_recommendations(symbol)
        
        # Collect news
        print("  ├─ Fetching latest news...")
        data['news'] = self.news_collector.get_stock_news(symbol)
        
        # Analyze news sentiment
        if data['news']:
            print("  ├─ Analyzing news sentiment...")
            data['news_sentiment'] = self.news_collector.analyze_sentiment(data['news'])
        
        # Collect market indices
        print("  ├─ Fetching market indices...")
        data['market_indices'] = self.market_collector.get_market_indices()
        
        # Get sector information
        print("  └─ Fetching sector information...")
        data['sector'] = self.market_collector.get_sector_performance(symbol)
        
        print(f"✓ Data collection complete for {symbol}\n")
        
        return data
    
    def get_price_metrics(self, historical_data: pd.DataFrame) -> Optional[Dict]:
        """
        Calculate key price metrics from historical data
        
        Args:
            historical_data: DataFrame with historical price data
            
        Returns:
            Dictionary with calculated metrics
        """
        if historical_data is None or historical_data.empty:
            return None
        
        try:
            current_price = historical_data['Close'].iloc[-1]
            
            # Calculate various metrics
            metrics = {
                'current_price': current_price,
                'high_52w': historical_data['High'].max() if len(historical_data) > 200 else None,
                'low_52w': historical_data['Low'].min() if len(historical_data) > 200 else None,
                'avg_volume': historical_data['Volume'].mean(),
                'price_change': historical_data['Close'].iloc[-1] - historical_data['Close'].iloc[0],
                'price_change_percent': ((historical_data['Close'].iloc[-1] / historical_data['Close'].iloc[0]) - 1) * 100,
            }
            
            # Calculate moving averages if enough data
            if len(historical_data) >= 50:
                metrics['sma_50'] = historical_data['Close'].rolling(window=50).mean().iloc[-1]
            if len(historical_data) >= 200:
                metrics['sma_200'] = historical_data['Close'].rolling(window=200).mean().iloc[-1]
            
            # Calculate RSI (Relative Strength Index)
            if len(historical_data) >= 14:
                delta = historical_data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                metrics['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
            
            return metrics
        except Exception as e:
            print(f"Error calculating price metrics: {e}")
            return None
    
    def get_fundamental_metrics(self, stock_info: Dict) -> Optional[Dict]:
        """
        Extract key fundamental metrics from stock info
        
        Args:
            stock_info: Dictionary with stock information
            
        Returns:
            Dictionary with fundamental metrics
        """
        if not stock_info:
            return None
        
        try:
            metrics = {
                'pe_ratio': stock_info.get('trailingPE'),
                'forward_pe': stock_info.get('forwardPE'),
                'peg_ratio': stock_info.get('pegRatio'),
                'price_to_book': stock_info.get('priceToBook'),
                'market_cap': stock_info.get('marketCap'),
                'beta': stock_info.get('beta'),
                'dividend_yield': stock_info.get('dividendYield'),
                'profit_margin': stock_info.get('profitMargins'),
                'revenue_growth': stock_info.get('revenueGrowth'),
                'recommendation': stock_info.get('recommendationKey'),
            }
            return metrics
        except Exception as e:
            print(f"Error extracting fundamental metrics: {e}")
            return None
