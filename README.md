# TradeSense

**Stock Trading Forecasting Interface** - Get intelligent buy/sell/hold recommendations based on comprehensive data analysis from multiple sources.

## Overview

TradeSense is a powerful stock analysis tool that aggregates data from multiple sources to provide you with actionable trading recommendations. It analyzes:

- 📈 **Technical Indicators** - RSI, Moving Averages, Price Momentum
- 💰 **Fundamental Metrics** - P/E Ratio, PEG Ratio, Profit Margins, Revenue Growth
- 📰 **News Sentiment** - Real-time analysis of news headlines
- 👨‍💼 **Analyst Recommendations** - Professional analyst opinions and ratings
- 🌐 **Market Context** - Major indices and sector performance

## Features

- **Multi-Source Data Collection**: Aggregates data from Yahoo Finance, news sources, and market indices
- **Comprehensive Analysis**: Combines technical, fundamental, sentiment, and analyst data
- **Clear Recommendations**: Provides BUY, SELL, or HOLD recommendations with confidence levels
- **Interactive CLI**: Easy-to-use command-line interface with colored output
- **Real-time Data**: Fetches the latest stock data and news

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Grimmet88/TradeSense.git
cd TradeSense
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode

Run TradeSense in interactive mode to analyze multiple stocks:

```bash
python tradesense.py
```

Then enter stock symbols when prompted:
```
Enter stock symbol: AAPL
Enter stock symbol: GOOGL
Enter stock symbol: quit
```

### Single Stock Analysis

Analyze a specific stock directly:

```bash
python tradesense.py AAPL
```

Specify a custom time period (default is 1 month):

```bash
python tradesense.py AAPL 6mo
```

Available periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`

### Commands

- Enter a stock symbol (e.g., `AAPL`, `GOOGL`, `TSLA`) to analyze
- Type `help` for help information
- Type `quit` or `exit` to exit the program

## How It Works

TradeSense uses a sophisticated multi-factor analysis approach:

### 1. Data Collection
- Fetches historical price data from Yahoo Finance
- Retrieves company fundamentals (P/E ratio, market cap, etc.)
- Collects recent news articles and headlines
- Gathers analyst recommendations
- Monitors major market indices

### 2. Analysis Components

**Technical Analysis (30% weight)**
- RSI (Relative Strength Index): Identifies overbought/oversold conditions
- Moving Averages: 50-day and 200-day trends
- Price Momentum: Recent price change analysis

**Fundamental Analysis (30% weight)**
- Valuation metrics (P/E, PEG ratios)
- Financial health (profit margins, revenue growth)
- Risk assessment (beta, volatility)

**Sentiment Analysis (20% weight)**
- Analyzes news headlines for positive/negative keywords
- Considers volume and recency of news

**Analyst Analysis (20% weight)**
- Aggregates professional analyst recommendations
- Considers consensus ratings and recent changes

### 3. Recommendation Generation
- Combines all signals with weighted scoring
- Generates BUY/SELL/HOLD recommendation
- Calculates confidence level (0-100%)
- Provides detailed breakdown of each factor

## Example Output

```
======================================================================
  TradeSense - Stock Trading Forecasting Interface
  Analyze stocks with data from multiple sources
======================================================================

📊 Collecting data for AAPL...
  ├─ Fetching historical data...
  ├─ Fetching stock information...
  ├─ Fetching analyst recommendations...
  ├─ Fetching latest news...
  ├─ Analyzing news sentiment...
  ├─ Fetching market indices...
  └─ Fetching sector information...
✓ Data collection complete for AAPL

======================================================================
  RECOMMENDATION: BUY
  CONFIDENCE: 75.0%
======================================================================

ANALYSIS BREAKDOWN:

Technical Analysis:
  Action: BUY
  Score: 3
  Signals:
    • RSI neutral (55.2)
    • Price above 50-day MA
    • Price above 200-day MA
    • Strong upward momentum (+12.5%)

Fundamental Analysis:
  Action: BUY
  Score: 2
  Signals:
    • Moderate P/E ratio (28.5)
    • Good PEG ratio (0.85)
    • Strong profit margin (25.5%)
    • Strong revenue growth (18.2%)

Sentiment Analysis:
  Action: BUY
  Score: 2
  Signals:
    • Positive news sentiment (15 articles analyzed)
    • Recent headlines: 15 articles available

Analyst Analysis:
  Action: BUY
  Score: 2
  Signals:
    • Analyst consensus: BUY

KEY METRICS:

  Price Metrics:
    • Current Price: $175.50
    • Price Change: +12.50%
    • RSI: 55.2
    • 50-day MA: $168.30
    • 200-day MA: $160.80

  Fundamental Metrics:
    • P/E Ratio: 28.50
    • Market Cap: $2.75T
    • Beta: 1.25
    • Dividend Yield: 0.50%

RECENT NEWS:
  1. Apple Announces Record Quarterly Revenue
     Source: Bloomberg
  2. iPhone Sales Exceed Expectations
     Source: Reuters
  ...

MARKET CONTEXT:
  • S&P 500: 4558.45
  • Dow Jones: 35426.78
  • NASDAQ: 14200.12
  • Volatility Index: 12.45

SECTOR: Technology
```

## Requirements

- Python 3.7+
- See `requirements.txt` for package dependencies

## Data Sources

TradeSense aggregates data from:
- **Yahoo Finance** - Historical prices, company info, analyst recommendations
- **News APIs** - Real-time news and sentiment
- **Market Indices** - S&P 500, Dow Jones, NASDAQ, VIX

## Limitations & Disclaimers

⚠️ **Important**: TradeSense is for informational and educational purposes only. It is NOT financial advice.

- Past performance does not guarantee future results
- Stock market investments carry risk
- Always do your own research before making investment decisions
- Consider consulting with a licensed financial advisor
- The accuracy of recommendations depends on data quality and market conditions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Happy Trading! 📈**
