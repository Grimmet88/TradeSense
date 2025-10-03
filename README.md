# TradeSense

AI-powered stock analysis and forecasting platform that combines web scraping, sentiment analysis, and machine learning to provide trading insights.

## 🚀 Features

- **Real-time Stock Data**: Fetch and analyze live stock prices
- **Sentiment Analysis**: Analyze news and social media sentiment for stocks
- **Price Forecasting**: ML-based stock price predictions
- **Interactive Dashboard**: Streamlit-based web interface
- **Automated Pipeline**: End-to-end data processing and decision making

## 📁 Project Structure

```
stock-forecast-dashboard/
│
├── app.py                # Streamlit dashboard entry point
├── requirements.txt      # All required Python packages
├── README.md             # Project overview and setup instructions
├── data/
│   └── tickers.csv       # List of tickers to analyze
├── src/
│   ├── pipeline.py       # Main logic: data fetching, processing, decision making
│   ├── scraping.py       # Functions to scrape news, prices, etc.
│   ├── sentiment.py      # Sentiment analysis logic
│   ├── forecast.py       # Stock forecasting logic (e.g., ML or momentum)
│   └── utils.py          # Helper functions
└── tests/
    └── test_pipeline.py  # Basic pipeline tests
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Grimmet88/TradeSense.git
cd TradeSense
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

1. Add your stock tickers to `data/tickers.csv`
2. Set up any required API keys in a `.env` file (if needed)

## 🚀 Running the Application

### Start the Dashboard

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

### Run the Pipeline Directly

```python
from src.pipeline import run_pipeline

results = run_pipeline(ticker="AAPL", include_sentiment=True, include_forecast=True)
print(results)
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## 📊 Usage

1. Launch the dashboard using `streamlit run app.py`
2. Select a stock ticker from the sidebar
3. Choose analysis options (sentiment, forecast)
4. Click "Run Analysis" to see results
5. View price charts, sentiment scores, and forecasts

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Do not use it as the sole basis for investment decisions. Always do your own research and consult with financial advisors.
