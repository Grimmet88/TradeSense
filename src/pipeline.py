"""
Main pipeline module for TradeSense.
Orchestrates data fetching, processing, sentiment analysis, and forecasting.
"""

from typing import Dict, Any
import pandas as pd

from src.scraping import (
    fetch_stock_data,
    get_stock_info,
    scrape_news_headlines,
    get_current_price
)
from src.sentiment import (
    analyze_news_sentiment,
    get_sentiment_recommendation
)
from src.forecast import (
    simple_momentum_forecast,
    create_forecast_report
)
from src.utils import create_result_dict, validate_ticker


def run_pipeline(
    ticker: str,
    include_sentiment: bool = True,
    include_forecast: bool = True,
    period: str = "1mo"
) -> Dict[str, Any]:
    """
    Execute the complete analysis pipeline for a given stock ticker.
    
    Args:
        ticker: Stock ticker symbol
        include_sentiment: Whether to include sentiment analysis
        include_forecast: Whether to include price forecasting
        period: Historical data period
        
    Returns:
        Dictionary containing all analysis results
    """
    # Validate ticker
    if not validate_ticker(ticker):
        return {
            "error": f"Invalid ticker symbol: {ticker}",
            "ticker": ticker
        }
    
    print(f"Starting pipeline for {ticker}...")
    
    # Initialize result dictionary
    results = create_result_dict(ticker)
    
    try:
        # Step 1: Fetch stock data
        print("Fetching stock data...")
        price_data = fetch_stock_data(ticker, period=period)
        
        if price_data.empty:
            results["error"] = "Failed to fetch stock data"
            return results
        
        results["price_data"] = price_data
        
        # Get stock info
        stock_info = get_stock_info(ticker)
        results["stock_info"] = stock_info
        
        # Get current price
        current_price = get_current_price(ticker)
        results["current_price"] = current_price
        
        # Step 2: Sentiment Analysis (optional)
        sentiment_score = 0.0
        if include_sentiment:
            print("Analyzing sentiment...")
            news_articles = scrape_news_headlines(ticker, num_articles=10)
            
            if news_articles:
                sentiment_data = analyze_news_sentiment(news_articles)
                results["sentiment"] = sentiment_data
                sentiment_score = sentiment_data.get("score", 0.0)
                
                # Get sentiment-based recommendation
                sentiment_rec = get_sentiment_recommendation(sentiment_data)
                results["sentiment_recommendation"] = sentiment_rec
            else:
                results["sentiment"] = {
                    "score": 0.0,
                    "label": "neutral",
                    "confidence": 0.0,
                    "note": "No news articles available"
                }
        
        # Step 3: Forecasting (optional)
        if include_forecast:
            print("Generating forecast...")
            forecast_data = simple_momentum_forecast(price_data, forecast_days=7)
            
            if not forecast_data.empty:
                forecast_report = create_forecast_report(
                    price_data,
                    forecast_data,
                    sentiment_score
                )
                results["forecast"] = forecast_data
                results["forecast_report"] = forecast_report
                
                # Generate overall trend recommendation
                trend = forecast_report.get("trend", "neutral")
                results["trend"] = trend
        
        # Step 4: Generate final recommendation
        print("Generating recommendation...")
        recommendation = generate_recommendation(
            results.get("sentiment", {}),
            results.get("forecast_report", {}),
            results.get("trend", "neutral")
        )
        results["recommendation"] = recommendation
        
        print(f"Pipeline completed for {ticker}")
        return results
        
    except Exception as e:
        print(f"Error in pipeline: {str(e)}")
        results["error"] = str(e)
        return results


def generate_recommendation(
    sentiment: Dict[str, Any],
    forecast_report: Dict[str, Any],
    trend: str
) -> str:
    """
    Generate overall trading recommendation based on all analysis.
    
    Args:
        sentiment: Sentiment analysis results
        forecast_report: Forecast report data
        trend: Trend direction
        
    Returns:
        Trading recommendation string
    """
    recommendations = []
    
    # Sentiment-based recommendation
    sentiment_score = sentiment.get("score", 0.0)
    if sentiment_score > 0.2:
        recommendations.append("Positive sentiment")
    elif sentiment_score < -0.2:
        recommendations.append("Negative sentiment")
    
    # Trend-based recommendation
    if trend == "bullish":
        recommendations.append("Bullish technical trend")
    elif trend == "bearish":
        recommendations.append("Bearish technical trend")
    
    # Volatility check
    volatility = forecast_report.get("volatility", 0)
    if volatility > 0.5:
        recommendations.append("High volatility - caution advised")
    
    # Generate final recommendation
    if not recommendations:
        return "HOLD - Neutral signals across all indicators"
    
    # Count positive vs negative signals
    positive_signals = sum(1 for r in recommendations if any(
        word in r.lower() for word in ["positive", "bullish"]
    ))
    negative_signals = sum(1 for r in recommendations if any(
        word in r.lower() for word in ["negative", "bearish"]
    ))
    
    if positive_signals > negative_signals:
        action = "CONSIDER BUY"
    elif negative_signals > positive_signals:
        action = "CONSIDER SELL"
    else:
        action = "HOLD"
    
    return f"{action} - {', '.join(recommendations)}"


def batch_analyze(
    tickers: list,
    include_sentiment: bool = True,
    include_forecast: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Run pipeline for multiple tickers.
    
    Args:
        tickers: List of ticker symbols
        include_sentiment: Whether to include sentiment analysis
        include_forecast: Whether to include forecasting
        
    Returns:
        Dictionary mapping tickers to their results
    """
    results = {}
    
    for ticker in tickers:
        print(f"\n{'='*50}")
        print(f"Analyzing {ticker}")
        print('='*50)
        
        result = run_pipeline(
            ticker,
            include_sentiment=include_sentiment,
            include_forecast=include_forecast
        )
        results[ticker] = result
    
    return results
