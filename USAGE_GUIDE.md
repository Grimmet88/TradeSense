# TradeSense Usage Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run TradeSense

**Interactive Mode:**
```bash
python tradesense.py
```

**Single Stock Analysis:**
```bash
python tradesense.py AAPL
```

**Custom Time Period:**
```bash
python tradesense.py AAPL 6mo
```

Available periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`

## Understanding the Analysis

### Recommendation Types

- **🟢 BUY** - Multiple positive indicators suggest the stock may be undervalued or trending upward
- **🟡 HOLD** - Mixed signals suggest waiting for clearer direction
- **🔴 SELL** - Multiple negative indicators suggest the stock may be overvalued or trending downward

### Confidence Level

The confidence percentage (0-100%) indicates how strong the signals are:
- **High (>70%)** - Strong agreement across multiple analysis types
- **Medium (40-70%)** - Moderate signals with some disagreement
- **Low (<40%)** - Weak or conflicting signals

### Analysis Components

#### 1. Technical Analysis (30% weight)

Analyzes price patterns and trends:

- **RSI (Relative Strength Index)**
  - < 30: Oversold (potential buy signal)
  - 30-70: Neutral range
  - > 70: Overbought (potential sell signal)

- **Moving Averages**
  - Price above MA: Bullish signal
  - Price below MA: Bearish signal
  - 50-day MA: Short-term trend
  - 200-day MA: Long-term trend

- **Price Momentum**
  - Recent price change percentage
  - Strong movement indicates trend strength

#### 2. Fundamental Analysis (30% weight)

Evaluates company financials:

- **P/E Ratio (Price-to-Earnings)**
  - Low (<15): Potentially undervalued
  - Moderate (15-30): Fair value
  - High (>30): Potentially overvalued

- **PEG Ratio (P/E to Growth)**
  - < 1: Good value relative to growth
  - > 2: Expensive relative to growth

- **Profit Margin**
  - > 20%: Strong profitability
  - < 0%: Unprofitable

- **Revenue Growth**
  - > 15%: Strong growth
  - < 0%: Declining revenue

- **Beta (Volatility)**
  - < 1: Less volatile than market
  - > 1: More volatile than market

#### 3. Sentiment Analysis (20% weight)

Analyzes news sentiment:

- Scans recent news headlines
- Identifies positive/negative keywords
- Determines overall sentiment trend

#### 4. Analyst Analysis (20% weight)

Incorporates professional analyst opinions:

- Analyst recommendation consensus
- Recent upgrades/downgrades
- Target price changes

## Example Workflow

### Analyzing a Single Stock

1. **Run Analysis:**
   ```bash
   python tradesense.py AAPL
   ```

2. **Review Recommendation:**
   - Check the main recommendation (BUY/SELL/HOLD)
   - Note the confidence level

3. **Examine Each Component:**
   - Look for consensus across analysis types
   - Identify any conflicting signals
   - Check which factors are strongest

4. **Review Metrics:**
   - Compare current price to moving averages
   - Check valuation metrics (P/E, PEG)
   - Review recent news for context

5. **Consider Market Context:**
   - Check market indices performance
   - Note sector trends

### Comparing Multiple Stocks

Run TradeSense in interactive mode:

```bash
python tradesense.py
Enter stock symbol: AAPL
Enter stock symbol: GOOGL
Enter stock symbol: MSFT
Enter stock symbol: quit
```

Compare:
- Recommendations across stocks
- Confidence levels
- Key metrics (P/E, growth rates)
- Sector performance

## Tips for Best Results

### 1. Use Appropriate Time Periods

- **Short-term trading (days to weeks):** `1d`, `5d`, `1mo`
- **Medium-term trading (months):** `3mo`, `6mo`
- **Long-term investing (years):** `1y`, `2y`, `5y`

### 2. Look for Consensus

The strongest signals occur when multiple analysis types agree:
- All BUY signals = Strong buy opportunity
- Mixed signals = Exercise caution
- All SELL signals = Strong sell signal

### 3. Consider Context

- **Market conditions:** Bull vs bear market
- **Sector trends:** Is the sector performing well?
- **News events:** Recent earnings, product launches, etc.

### 4. Don't Rely Solely on One Tool

TradeSense provides valuable insights, but should be used alongside:
- Your own research
- Professional financial advice
- Diversification strategy
- Risk tolerance assessment

## Common Use Cases

### 1. Pre-Market Research
```bash
# Check your watchlist before market opens
python tradesense.py AAPL
python tradesense.py GOOGL
python tradesense.py MSFT
```

### 2. Portfolio Review
```bash
# Analyze your current holdings
python tradesense.py
# Enter each holding symbol
```

### 3. Finding Opportunities
```bash
# Compare similar stocks in a sector
python tradesense.py
# Enter: AAPL, MSFT, GOOGL, AMZN
```

### 4. Trend Monitoring
```bash
# Check long-term trends
python tradesense.py AAPL 1y
python tradesense.py AAPL 2y
```

## Interpreting Results

### Strong Buy Signal Example
```
Recommendation: BUY
Confidence: 80%

✓ Technical: BUY (RSI oversold, above MAs)
✓ Fundamental: BUY (low P/E, strong growth)
✓ Sentiment: BUY (positive news)
✓ Analyst: BUY (consensus buy rating)
```
**Interpretation:** Multiple strong positive signals suggest good entry point.

### Mixed Signal Example
```
Recommendation: HOLD
Confidence: 45%

? Technical: BUY (strong momentum)
? Fundamental: SELL (high valuation)
? Sentiment: HOLD (neutral news)
? Analyst: BUY (analyst support)
```
**Interpretation:** Conflicting signals suggest waiting for clearer direction.

### Strong Sell Signal Example
```
Recommendation: SELL
Confidence: 75%

✗ Technical: SELL (RSI overbought, below MAs)
✗ Fundamental: SELL (high P/E, declining growth)
✗ Sentiment: SELL (negative news)
✗ Analyst: HOLD (mixed opinions)
```
**Interpretation:** Multiple negative signals suggest potential exit point.

## Troubleshooting

### No Data Available
- Check that the stock symbol is correct
- Ensure internet connection is working
- Try a different time period
- Some stocks may have limited data

### Conflicting Signals
- Review each analysis component individually
- Consider which factors are most important for your strategy
- Look at longer time periods for better context
- Wait for clearer signals before acting

### Low Confidence
- May indicate uncertain market conditions
- Consider analyzing over different time periods
- Look at similar stocks for comparison
- Wait for more data/clearer trends

## Advanced Usage

### Custom Analysis Weights

The default weights are:
- Technical: 30%
- Fundamental: 30%
- Sentiment: 20%
- Analyst: 20%

To customize (requires code modification):
```python
# In forecasting_engine.py
self.recommendation_weights = {
    'technical': 0.40,    # Increase technical weight
    'fundamental': 0.30,
    'sentiment': 0.15,
    'analyst': 0.15
}
```

### Batch Analysis

Create a script to analyze multiple stocks:
```python
from tradesense.forecasting_engine import ForecastingEngine

engine = ForecastingEngine()
symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']

for symbol in symbols:
    analysis = engine.analyze_stock(symbol)
    print(f"{symbol}: {analysis['recommendation']} ({analysis['confidence']:.1f}%)")
```

## Disclaimer

⚠️ **Important:** TradeSense is for informational and educational purposes only. It is NOT financial advice. Always:

- Do your own research
- Consult with licensed financial advisors
- Consider your risk tolerance
- Diversify your portfolio
- Never invest more than you can afford to lose

Past performance does not guarantee future results. Stock market investments carry risk.
