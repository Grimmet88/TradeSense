# TradeSense

A Streamlit dashboard for Buy/Sell/Hold stock signals using news scraping, sentiment analysis, and forecasting.

## Setup

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```

## Structure

- `app.py`: Streamlit UI
- `src/pipeline.py`: Main logic orchestration
- `data/tickers.csv`: List of tickers to analyze

## What TradeSense Does

- Scrapes news headlines and financial data
- Analyzes sentiment from news
- Uses simple forecasting models
- Displays: Top trading candidates, Buy/Sell/Hold signals, relevant news
