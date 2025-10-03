"""
TradeSense - Stock Forecast Dashboard
Streamlit dashboard entry point for stock analysis and forecasting.
"""

import streamlit as st
import pandas as pd
from src.pipeline import run_pipeline
from src.utils import load_tickers


def main():
    """Main dashboard application."""
    st.title("📈 TradeSense - Stock Forecast Dashboard")
    st.write("AI-powered stock analysis and forecasting platform")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Load available tickers
    tickers = load_tickers()
    selected_ticker = st.sidebar.selectbox("Select Stock Ticker", tickers)
    
    # Analysis options
    st.sidebar.subheader("Analysis Options")
    include_sentiment = st.sidebar.checkbox("Include Sentiment Analysis", value=True)
    include_forecast = st.sidebar.checkbox("Include Forecast", value=True)
    
    # Run analysis button
    if st.sidebar.button("Run Analysis"):
        with st.spinner("Analyzing..."):
            results = run_pipeline(
                ticker=selected_ticker,
                include_sentiment=include_sentiment,
                include_forecast=include_forecast
            )
            
            # Display results
            st.header(f"Analysis Results for {selected_ticker}")
            
            if "price_data" in results:
                st.subheader("Price Data")
                st.line_chart(results["price_data"])
            
            if "sentiment" in results:
                st.subheader("Sentiment Analysis")
                st.write(f"Overall Sentiment: {results['sentiment']['score']}")
                st.write(f"Confidence: {results['sentiment']['confidence']:.2%}")
            
            if "forecast" in results:
                st.subheader("Forecast")
                st.line_chart(results["forecast"])
            
            if "recommendation" in results:
                st.subheader("Trading Recommendation")
                st.info(results["recommendation"])


if __name__ == "__main__":
    main()
