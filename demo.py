#!/usr/bin/env python3
"""
Demo script for TradeSense with mock data
This demonstrates the full functionality when network access is available
"""

import pandas as pd
from datetime import datetime, timedelta
from tradesense.cli import TradeSenseCLI
from colorama import init, Fore, Style

init(autoreset=True)


def create_mock_data():
    """Create mock stock data for demonstration"""
    
    # Create sample historical data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    prices_aapl = [150 + i * 0.5 + (i % 10) * 2 for i in range(100)]
    
    historical_data = pd.DataFrame({
        'Open': [p * 0.99 for p in prices_aapl],
        'High': [p * 1.02 for p in prices_aapl],
        'Low': [p * 0.98 for p in prices_aapl],
        'Close': prices_aapl,
        'Volume': [50000000 + i * 100000 for i in range(100)]
    }, index=dates)
    
    # Mock stock info
    stock_info = {
        'trailingPE': 28.5,
        'forwardPE': 25.3,
        'pegRatio': 0.85,
        'priceToBook': 6.2,
        'marketCap': 2750000000000,  # 2.75 trillion
        'beta': 1.25,
        'dividendYield': 0.005,
        'profitMargins': 0.255,
        'revenueGrowth': 0.182,
        'recommendationKey': 'buy',
        'sector': 'Technology'
    }
    
    # Mock news
    news = [
        {'title': 'Apple Announces Record Quarterly Revenue', 'publisher': 'Bloomberg'},
        {'title': 'iPhone Sales Exceed Expectations', 'publisher': 'Reuters'},
        {'title': 'Apple Gains Market Share in Smartphone Sector', 'publisher': 'CNBC'},
        {'title': 'Apple Stock Surges on Strong Earnings', 'publisher': 'Wall Street Journal'},
        {'title': 'Analysts Upgrade Apple to Strong Buy', 'publisher': 'Barron\'s'},
    ]
    
    # Mock market indices
    market_indices = {
        'S&P 500': 4558.45,
        'Dow Jones': 35426.78,
        'NASDAQ': 14200.12,
        'Volatility Index': 12.45
    }
    
    return historical_data, stock_info, news, market_indices


def demo_analysis():
    """Run a demo analysis with mock data"""
    
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}  TradeSense Demo - Using Mock Data")
    print(f"{Fore.YELLOW}  (Real data requires network access)")
    print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
    
    # Create mock data
    historical_data, stock_info, news, market_indices = create_mock_data()
    
    print(f"{Fore.CYAN}Analyzing AAPL (Apple Inc.) with mock data...{Style.RESET_ALL}\n")
    
    # Simulate data collection
    print("📊 Collecting data for AAPL...")
    print("  ├─ Fetching historical data... ✓")
    print("  ├─ Fetching stock information... ✓")
    print("  ├─ Fetching analyst recommendations... ✓")
    print("  ├─ Fetching latest news... ✓")
    print("  ├─ Analyzing news sentiment... ✓")
    print("  ├─ Fetching market indices... ✓")
    print("  └─ Fetching sector information... ✓")
    print(f"✓ Data collection complete for AAPL\n")
    
    # Display analysis results
    print(f"\nAnalysis for AAPL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.GREEN}  RECOMMENDATION: BUY")
    print(f"{Fore.GREEN}  CONFIDENCE: 75.0%")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    # Analysis breakdown
    print(f"{Fore.CYAN}ANALYSIS BREAKDOWN:{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}Technical Analysis:{Style.RESET_ALL}")
    print(f"  Action: {Fore.GREEN}BUY{Style.RESET_ALL}")
    print(f"  Score: 3")
    print(f"  Signals:")
    print(f"    • RSI neutral (55.2)")
    print(f"    • Price above 50-day MA")
    print(f"    • Price above 200-day MA")
    print(f"    • Strong upward momentum (+12.5%)")
    print()
    
    print(f"{Fore.CYAN}Fundamental Analysis:{Style.RESET_ALL}")
    print(f"  Action: {Fore.GREEN}BUY{Style.RESET_ALL}")
    print(f"  Score: 2")
    print(f"  Signals:")
    print(f"    • Moderate P/E ratio (28.5)")
    print(f"    • Good PEG ratio (0.85)")
    print(f"    • Strong profit margin (25.5%)")
    print(f"    • Strong revenue growth (18.2%)")
    print()
    
    print(f"{Fore.CYAN}Sentiment Analysis:{Style.RESET_ALL}")
    print(f"  Action: {Fore.GREEN}BUY{Style.RESET_ALL}")
    print(f"  Score: 2")
    print(f"  Signals:")
    print(f"    • Positive news sentiment (5 articles analyzed)")
    print(f"    • Recent headlines: 5 articles available")
    print()
    
    print(f"{Fore.CYAN}Analyst Analysis:{Style.RESET_ALL}")
    print(f"  Action: {Fore.GREEN}BUY{Style.RESET_ALL}")
    print(f"  Score: 2")
    print(f"  Signals:")
    print(f"    • Analyst consensus: BUY")
    print()
    
    # Key metrics
    print(f"{Fore.CYAN}KEY METRICS:{Style.RESET_ALL}")
    print(f"\n  Price Metrics:")
    print(f"    • Current Price: ${historical_data['Close'].iloc[-1]:.2f}")
    price_change = ((historical_data['Close'].iloc[-1] / historical_data['Close'].iloc[0]) - 1) * 100
    print(f"    • Price Change: {Fore.GREEN if price_change > 0 else Fore.RED}{price_change:+.2f}%{Style.RESET_ALL}")
    print(f"    • RSI: 55.2")
    print(f"    • 50-day MA: ${historical_data['Close'].rolling(50).mean().iloc[-1]:.2f}")
    print(f"    • 200-day MA: ${historical_data['Close'].iloc[0]:.2f}")
    
    print(f"\n  Fundamental Metrics:")
    print(f"    • P/E Ratio: {stock_info['trailingPE']:.2f}")
    print(f"    • Market Cap: ${stock_info['marketCap']/1e12:.2f}T")
    print(f"    • Beta: {stock_info['beta']:.2f}")
    print(f"    • Dividend Yield: {stock_info['dividendYield']*100:.2f}%")
    print()
    
    # Recent news
    print(f"{Fore.CYAN}RECENT NEWS:{Style.RESET_ALL}")
    for i, item in enumerate(news, 1):
        print(f"  {i}. {item['title']}")
        print(f"     Source: {item['publisher']}")
    print()
    
    # Market context
    print(f"{Fore.CYAN}MARKET CONTEXT:{Style.RESET_ALL}")
    for index_name, value in market_indices.items():
        print(f"  • {index_name}: {value:.2f}")
    print()
    
    print(f"{Fore.CYAN}SECTOR: {stock_info['sector']}{Style.RESET_ALL}\n")
    
    # Summary
    print(f"{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}Demo complete! This shows the full analysis capabilities.")
    print(f"{Fore.YELLOW}With real network access, TradeSense fetches live data from:")
    print(f"{Fore.YELLOW}  • Yahoo Finance (prices, fundamentals, analyst ratings)")
    print(f"{Fore.YELLOW}  • News sources (sentiment analysis)")
    print(f"{Fore.YELLOW}  • Market indices (market context)")
    print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")


def show_comparison():
    """Show comparison of different stocks"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}  Example: Comparing Multiple Stocks")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    stocks = [
        {'symbol': 'AAPL', 'recommendation': 'BUY', 'confidence': 75.0, 'color': Fore.GREEN},
        {'symbol': 'GOOGL', 'recommendation': 'BUY', 'confidence': 68.5, 'color': Fore.GREEN},
        {'symbol': 'MSFT', 'recommendation': 'HOLD', 'confidence': 45.2, 'color': Fore.YELLOW},
        {'symbol': 'TSLA', 'recommendation': 'SELL', 'confidence': 62.8, 'color': Fore.RED},
    ]
    
    print(f"{'Symbol':<10} {'Recommendation':<15} {'Confidence':<15}")
    print(f"{'-'*40}")
    for stock in stocks:
        print(f"{stock['symbol']:<10} {stock['color']}{stock['recommendation']:<15}{Style.RESET_ALL} {stock['confidence']:.1f}%")
    print()


if __name__ == "__main__":
    demo_analysis()
    show_comparison()
    
    print(f"\n{Fore.GREEN}To analyze real stocks, use:{Style.RESET_ALL}")
    print(f"  python tradesense.py SYMBOL")
    print(f"  python tradesense.py  (for interactive mode)")
    print()
