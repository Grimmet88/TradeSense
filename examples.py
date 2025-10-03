#!/usr/bin/env python3
"""
Examples of using TradeSense programmatically
This shows how to integrate TradeSense into your own scripts
"""

from tradesense.forecasting_engine import ForecastingEngine
from tradesense.data_aggregator import DataAggregator
from colorama import init, Fore, Style
import sys

init(autoreset=True)


def example_1_single_stock():
    """Example 1: Analyze a single stock"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"Example 1: Analyzing a Single Stock")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    engine = ForecastingEngine()
    
    # Analyze Apple stock
    symbol = "AAPL"
    analysis = engine.analyze_stock(symbol)
    
    # Print results
    print(f"Stock: {analysis['symbol']}")
    print(f"Recommendation: {analysis['recommendation']}")
    print(f"Confidence: {analysis['confidence']:.1f}%")
    print()


def example_2_multiple_stocks():
    """Example 2: Compare multiple stocks"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"Example 2: Comparing Multiple Stocks")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    engine = ForecastingEngine()
    
    # List of stocks to compare
    symbols = ["AAPL", "GOOGL", "MSFT"]
    results = []
    
    for symbol in symbols:
        try:
            analysis = engine.analyze_stock(symbol)
            results.append({
                'symbol': analysis['symbol'],
                'recommendation': analysis['recommendation'],
                'confidence': analysis['confidence']
            })
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
    
    # Print comparison
    if results:
        print(f"{'Symbol':<10} {'Recommendation':<15} {'Confidence':<15}")
        print(f"{'-'*40}")
        for result in results:
            color = (Fore.GREEN if result['recommendation'] == 'BUY' 
                    else Fore.RED if result['recommendation'] == 'SELL' 
                    else Fore.YELLOW)
            print(f"{result['symbol']:<10} {color}{result['recommendation']:<15}{Style.RESET_ALL} "
                  f"{result['confidence']:.1f}%")
        print()


def example_3_detailed_analysis():
    """Example 3: Access detailed analysis components"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"Example 3: Accessing Detailed Analysis")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    engine = ForecastingEngine()
    
    # Analyze with full details
    symbol = "AAPL"
    analysis = engine.analyze_stock(symbol)
    
    # Access individual signals
    print(f"Technical Signal: {analysis['signals']['technical']['action']}")
    print(f"  Score: {analysis['signals']['technical']['score']}")
    print(f"  Details: {', '.join(analysis['signals']['technical']['signals'][:2])}")
    print()
    
    print(f"Fundamental Signal: {analysis['signals']['fundamental']['action']}")
    print(f"  Score: {analysis['signals']['fundamental']['score']}")
    print()
    
    # Access metrics
    if analysis['metrics']['price']:
        print(f"Current Price: ${analysis['metrics']['price']['current_price']:.2f}")
        print(f"Price Change: {analysis['metrics']['price']['price_change_percent']:.2f}%")
    print()


def example_4_custom_period():
    """Example 4: Analyze with custom time periods"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"Example 4: Analyzing Different Time Periods")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    engine = ForecastingEngine()
    
    symbol = "AAPL"
    periods = ["1mo", "3mo", "6mo"]
    
    print(f"{'Period':<10} {'Recommendation':<15} {'Confidence':<15}")
    print(f"{'-'*40}")
    
    for period in periods:
        try:
            analysis = engine.analyze_stock(symbol, period=period)
            color = (Fore.GREEN if analysis['recommendation'] == 'BUY' 
                    else Fore.RED if analysis['recommendation'] == 'SELL' 
                    else Fore.YELLOW)
            print(f"{period:<10} {color}{analysis['recommendation']:<15}{Style.RESET_ALL} "
                  f"{analysis['confidence']:.1f}%")
        except Exception as e:
            print(f"{period:<10} Error: {e}")
    print()


def example_5_data_aggregation():
    """Example 5: Using the data aggregator directly"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"Example 5: Direct Data Aggregation")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    aggregator = DataAggregator()
    
    # Collect data
    symbol = "AAPL"
    data = aggregator.collect_all_data(symbol)
    
    # Access collected data
    print(f"Symbol: {data['symbol']}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Sector: {data.get('sector', 'Unknown')}")
    print(f"News articles: {len(data.get('news', []))}")
    print(f"News sentiment: {data.get('news_sentiment', 'unknown')}")
    
    # Get calculated metrics
    price_metrics = aggregator.get_price_metrics(data['historical_data'])
    if price_metrics:
        print(f"\nPrice Metrics:")
        print(f"  Current: ${price_metrics.get('current_price', 0):.2f}")
        if 'rsi' in price_metrics:
            print(f"  RSI: {price_metrics['rsi']:.2f}")
    
    fundamental_metrics = aggregator.get_fundamental_metrics(data['stock_info'])
    if fundamental_metrics:
        print(f"\nFundamental Metrics:")
        if fundamental_metrics.get('pe_ratio'):
            print(f"  P/E Ratio: {fundamental_metrics['pe_ratio']:.2f}")
        if fundamental_metrics.get('market_cap'):
            print(f"  Market Cap: ${fundamental_metrics['market_cap']/1e9:.2f}B")
    print()


def example_6_watchlist():
    """Example 6: Monitor a watchlist"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"Example 6: Monitoring a Watchlist")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    engine = ForecastingEngine()
    
    # Your watchlist
    watchlist = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    # Find strong buy signals
    buy_signals = []
    sell_signals = []
    
    print("Scanning watchlist...")
    for symbol in watchlist:
        try:
            analysis = engine.analyze_stock(symbol)
            if analysis['recommendation'] == 'BUY' and analysis['confidence'] > 60:
                buy_signals.append({
                    'symbol': symbol,
                    'confidence': analysis['confidence']
                })
            elif analysis['recommendation'] == 'SELL' and analysis['confidence'] > 60:
                sell_signals.append({
                    'symbol': symbol,
                    'confidence': analysis['confidence']
                })
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
    
    # Print results
    if buy_signals:
        print(f"\n{Fore.GREEN}Strong Buy Signals:{Style.RESET_ALL}")
        for signal in sorted(buy_signals, key=lambda x: x['confidence'], reverse=True):
            print(f"  • {signal['symbol']}: {signal['confidence']:.1f}% confidence")
    
    if sell_signals:
        print(f"\n{Fore.RED}Strong Sell Signals:{Style.RESET_ALL}")
        for signal in sorted(sell_signals, key=lambda x: x['confidence'], reverse=True):
            print(f"  • {signal['symbol']}: {signal['confidence']:.1f}% confidence")
    
    if not buy_signals and not sell_signals:
        print(f"\n{Fore.YELLOW}No strong signals found in watchlist{Style.RESET_ALL}")
    print()


def main():
    """Run all examples"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"TradeSense - Programming Examples")
    print(f"{'='*70}{Style.RESET_ALL}")
    print(f"\nThese examples show how to use TradeSense in your own scripts.")
    print(f"Note: Network access required for live data.\n")
    
    examples = [
        ("Single Stock Analysis", example_1_single_stock),
        ("Multiple Stock Comparison", example_2_multiple_stocks),
        ("Detailed Analysis Access", example_3_detailed_analysis),
        ("Custom Time Periods", example_4_custom_period),
        ("Direct Data Aggregation", example_5_data_aggregation),
        ("Watchlist Monitoring", example_6_watchlist),
    ]
    
    if len(sys.argv) > 1:
        # Run specific example
        try:
            example_num = int(sys.argv[1])
            if 1 <= example_num <= len(examples):
                name, func = examples[example_num - 1]
                print(f"Running: {name}")
                func()
            else:
                print(f"Example {example_num} not found. Choose 1-{len(examples)}")
        except ValueError:
            print("Usage: python examples.py [example_number]")
    else:
        # List all examples
        print("Available examples:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")
        print(f"\nRun with: python examples.py [number]")
        print(f"Example: python examples.py 1")
        print()


if __name__ == "__main__":
    main()
