# TradeSense Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/Grimmet88/TradeSense.git
cd TradeSense

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### Analyze a Stock
```bash
python tradesense.py AAPL
```

### Interactive Mode
```bash
python tradesense.py
# Then enter stock symbols when prompted
```

### Try the Demo (No Internet Required)
```bash
python demo.py
```

## Example Symbols to Try

- **Tech:** AAPL, GOOGL, MSFT, AMZN, META, NVDA
- **Finance:** JPM, BAC, GS, V, MA
- **Healthcare:** JNJ, PFE, UNH, ABBV
- **Auto:** TSLA, F, GM
- **Retail:** WMT, TGT, COST

## Understanding Results

### Recommendations
- 🟢 **BUY** - Positive indicators suggest potential upside
- 🟡 **HOLD** - Mixed signals, wait for clearer direction
- 🔴 **SELL** - Negative indicators suggest potential downside

### Confidence Level
- **High (>70%)** - Strong agreement across all analysis types
- **Medium (40-70%)** - Moderate signals
- **Low (<40%)** - Weak or conflicting signals

### Key Metrics to Watch

**Technical:**
- RSI < 30: Oversold (potential buy)
- RSI > 70: Overbought (potential sell)
- Price above MAs: Bullish trend
- Price below MAs: Bearish trend

**Fundamental:**
- P/E < 15: Potentially undervalued
- P/E > 30: Potentially overvalued
- High profit margin (>20%): Strong profitability
- Positive revenue growth: Company expanding

**Sentiment:**
- Positive news: Bullish sentiment
- Negative news: Bearish sentiment

**Analyst:**
- Consensus BUY: Professional confidence
- Consensus SELL: Professional concern

## Quick Commands

```bash
# Analyze with 6-month data
python tradesense.py AAPL 6mo

# Analyze with 1-year data
python tradesense.py GOOGL 1y

# Interactive mode
python tradesense.py
```

## Tips for Best Results

1. **Compare Multiple Stocks** - Look at competitors in the same sector
2. **Check Different Time Periods** - Short-term vs long-term trends
3. **Look for Consensus** - Strongest signals when all analysis types agree
4. **Consider Context** - Check market conditions and recent news
5. **Use as One Tool** - Combine with your own research

## Need Help?

- Run `python tradesense.py` and type `help`
- Read [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed instructions
- Check [README.md](README.md) for full documentation

## Important Disclaimer

⚠️ **TradeSense is for informational purposes only - NOT financial advice!**

Always:
- Do your own research
- Consult professional financial advisors
- Consider your risk tolerance
- Never invest more than you can afford to lose

---

**Happy analyzing! 📈**
