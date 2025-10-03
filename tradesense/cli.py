"""
Command-line interface for TradeSense
"""

import sys
from typing import Optional
from datetime import datetime
from colorama import init, Fore, Style
from .forecasting_engine import ForecastingEngine

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class TradeSenseCLI:
    """Command-line interface for TradeSense stock analysis"""
    
    def __init__(self):
        self.engine = ForecastingEngine()
    
    def print_banner(self):
        """Print TradeSense banner"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}  TradeSense - Stock Trading Forecasting Interface")
        print(f"{Fore.CYAN}  Analyze stocks with data from multiple sources")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def print_recommendation(self, recommendation: str, confidence: float):
        """
        Print colored recommendation
        
        Args:
            recommendation: BUY, SELL, or HOLD
            confidence: Confidence percentage
        """
        color = Fore.GREEN if recommendation == 'BUY' else Fore.RED if recommendation == 'SELL' else Fore.YELLOW
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{color}  RECOMMENDATION: {recommendation}")
        print(f"{color}  CONFIDENCE: {confidence:.1f}%")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def print_signal_section(self, title: str, signal: dict):
        """
        Print a signal section with details
        
        Args:
            title: Section title
            signal: Signal dictionary
        """
        action_color = (Fore.GREEN if signal['action'] == 'BUY' 
                       else Fore.RED if signal['action'] == 'SELL' 
                       else Fore.YELLOW)
        
        print(f"{Fore.CYAN}{title}:{Style.RESET_ALL}")
        print(f"  Action: {action_color}{signal['action']}{Style.RESET_ALL}")
        print(f"  Score: {signal['score']}")
        print(f"  Signals:")
        for s in signal['signals']:
            print(f"    • {s}")
        print()
    
    def print_metrics(self, analysis: dict):
        """
        Print key metrics
        
        Args:
            analysis: Analysis dictionary
        """
        price_metrics = analysis['metrics'].get('price')
        fundamental_metrics = analysis['metrics'].get('fundamental')
        
        print(f"{Fore.CYAN}KEY METRICS:{Style.RESET_ALL}")
        
        if price_metrics:
            print(f"\n  Price Metrics:")
            current = price_metrics.get('current_price')
            if current:
                print(f"    • Current Price: ${current:.2f}")
            
            change_pct = price_metrics.get('price_change_percent')
            if change_pct is not None:
                color = Fore.GREEN if change_pct > 0 else Fore.RED
                print(f"    • Price Change: {color}{change_pct:+.2f}%{Style.RESET_ALL}")
            
            if 'rsi' in price_metrics:
                print(f"    • RSI: {price_metrics['rsi']:.1f}")
            
            if 'sma_50' in price_metrics:
                print(f"    • 50-day MA: ${price_metrics['sma_50']:.2f}")
            
            if 'sma_200' in price_metrics:
                print(f"    • 200-day MA: ${price_metrics['sma_200']:.2f}")
        
        if fundamental_metrics:
            print(f"\n  Fundamental Metrics:")
            
            if fundamental_metrics.get('pe_ratio'):
                print(f"    • P/E Ratio: {fundamental_metrics['pe_ratio']:.2f}")
            
            if fundamental_metrics.get('market_cap'):
                market_cap = fundamental_metrics['market_cap']
                if market_cap >= 1e12:
                    print(f"    • Market Cap: ${market_cap/1e12:.2f}T")
                elif market_cap >= 1e9:
                    print(f"    • Market Cap: ${market_cap/1e9:.2f}B")
                elif market_cap >= 1e6:
                    print(f"    • Market Cap: ${market_cap/1e6:.2f}M")
            
            if fundamental_metrics.get('beta'):
                print(f"    • Beta: {fundamental_metrics['beta']:.2f}")
            
            if fundamental_metrics.get('dividend_yield'):
                print(f"    • Dividend Yield: {fundamental_metrics['dividend_yield']*100:.2f}%")
        
        print()
    
    def print_news(self, news: list, max_items: int = 5):
        """
        Print recent news headlines
        
        Args:
            news: List of news items
            max_items: Maximum number of items to display
        """
        if not news:
            return
        
        print(f"{Fore.CYAN}RECENT NEWS:{Style.RESET_ALL}")
        for i, item in enumerate(news[:max_items], 1):
            title = item.get('title', 'No title')
            publisher = item.get('publisher', 'Unknown')
            print(f"  {i}. {title}")
            print(f"     Source: {publisher}")
        print()
    
    def analyze(self, symbol: str, period: str = "1mo", show_news: bool = True):
        """
        Analyze a stock and display results
        
        Args:
            symbol: Stock ticker symbol
            period: Time period for analysis
            show_news: Whether to show news headlines
        """
        try:
            # Perform analysis
            analysis = self.engine.analyze_stock(symbol, period)
            
            # Display results
            print(f"\n{Fore.CYAN}Analysis for {analysis['symbol']} - {analysis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
            
            # Print recommendation
            self.print_recommendation(analysis['recommendation'], analysis['confidence'])
            
            # Print individual signals
            print(f"{Fore.CYAN}ANALYSIS BREAKDOWN:{Style.RESET_ALL}\n")
            self.print_signal_section("Technical Analysis", analysis['signals']['technical'])
            self.print_signal_section("Fundamental Analysis", analysis['signals']['fundamental'])
            self.print_signal_section("Sentiment Analysis", analysis['signals']['sentiment'])
            self.print_signal_section("Analyst Analysis", analysis['signals']['analyst'])
            
            # Print metrics
            self.print_metrics(analysis)
            
            # Print news if requested
            if show_news and analysis['data']['news']:
                self.print_news(analysis['data']['news'])
            
            # Print market context
            market_indices = analysis['data'].get('market_indices')
            if market_indices:
                print(f"{Fore.CYAN}MARKET CONTEXT:{Style.RESET_ALL}")
                for index_name, value in market_indices.items():
                    if value:
                        print(f"  • {index_name}: {value:.2f}")
                print()
            
            # Print sector
            sector = analysis['data'].get('sector')
            if sector:
                print(f"{Fore.CYAN}SECTOR: {sector}{Style.RESET_ALL}\n")
            
        except Exception as e:
            print(f"{Fore.RED}Error analyzing {symbol}: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
    
    def run_interactive(self):
        """Run in interactive mode"""
        self.print_banner()
        
        print(f"{Fore.YELLOW}Interactive Mode - Enter stock symbols to analyze{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Commands: 'quit' or 'exit' to quit, 'help' for help{Style.RESET_ALL}\n")
        
        while True:
            try:
                user_input = input(f"{Fore.GREEN}Enter stock symbol: {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{Fore.CYAN}Thank you for using TradeSense!{Style.RESET_ALL}\n")
                    break
                
                if user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                # Analyze the stock
                self.analyze(user_input.upper())
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}Thank you for using TradeSense!{Style.RESET_ALL}\n")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}\n")
    
    def print_help(self):
        """Print help information"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"TradeSense Help")
        print(f"{'='*70}{Style.RESET_ALL}")
        print("\nUsage:")
        print("  • Enter a stock symbol (e.g., AAPL, GOOGL, TSLA)")
        print("  • Type 'quit' or 'exit' to exit")
        print("  • Type 'help' for this help message")
        print("\nAnalysis includes:")
        print("  • Technical Analysis (RSI, Moving Averages, Momentum)")
        print("  • Fundamental Analysis (P/E, PEG, Profit Margins, Growth)")
        print("  • Sentiment Analysis (News headlines)")
        print("  • Analyst Recommendations")
        print("\nRecommendations:")
        print(f"  • {Fore.GREEN}BUY{Style.RESET_ALL}  - Stock shows positive signals")
        print(f"  • {Fore.YELLOW}HOLD{Style.RESET_ALL} - Stock shows mixed signals")
        print(f"  • {Fore.RED}SELL{Style.RESET_ALL} - Stock shows negative signals")
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def main():
    """Main entry point for CLI"""
    cli = TradeSenseCLI()
    
    # Check if symbol provided as argument
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        period = sys.argv[2] if len(sys.argv) > 2 else "1mo"
        cli.print_banner()
        cli.analyze(symbol, period)
    else:
        # Run in interactive mode
        cli.run_interactive()


if __name__ == "__main__":
    main()
