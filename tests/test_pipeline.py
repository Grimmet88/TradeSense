"""
Basic tests for TradeSense pipeline.
"""

import pytest
import pandas as pd
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import run_pipeline, generate_recommendation, batch_analyze
from src.utils import (
    load_tickers,
    validate_ticker,
    calculate_percentage_change,
    format_currency,
    create_result_dict
)
from src.sentiment import (
    analyze_text_sentiment,
    analyze_news_sentiment,
    get_sentiment_recommendation
)
from src.forecast import (
    calculate_momentum_indicators,
    get_trend_direction,
    generate_price_targets
)


class TestUtils:
    """Test utility functions."""
    
    def test_validate_ticker_valid(self):
        """Test ticker validation with valid tickers."""
        assert validate_ticker("AAPL") == True
        assert validate_ticker("MSFT") == True
        assert validate_ticker("GOOGL") == True
    
    def test_validate_ticker_invalid(self):
        """Test ticker validation with invalid tickers."""
        assert validate_ticker("") == False
        assert validate_ticker("aapl") == False  # lowercase
        assert validate_ticker("TOOLONG") == False  # too long
        assert validate_ticker(None) == False
        assert validate_ticker("123") == False  # not alpha
    
    def test_calculate_percentage_change(self):
        """Test percentage change calculation."""
        assert calculate_percentage_change(100, 110) == 10.0
        assert calculate_percentage_change(100, 90) == -10.0
        assert calculate_percentage_change(0, 100) == 0.0
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(1234.56) == "$1,234.56"
        assert format_currency(1000000) == "$1,000,000.00"
    
    def test_create_result_dict(self):
        """Test result dictionary creation."""
        result = create_result_dict("AAPL")
        assert result["ticker"] == "AAPL"
        assert "timestamp" in result


class TestSentiment:
    """Test sentiment analysis functions."""
    
    def test_analyze_text_sentiment_positive(self):
        """Test sentiment analysis with positive text."""
        text = "Stock surges on strong earnings beat and profit growth"
        result = analyze_text_sentiment(text)
        assert result["label"] == "positive"
        assert result["score"] > 0
    
    def test_analyze_text_sentiment_negative(self):
        """Test sentiment analysis with negative text."""
        text = "Stock plunges on weak guidance and declining revenue"
        result = analyze_text_sentiment(text)
        assert result["label"] == "negative"
        assert result["score"] < 0
    
    def test_analyze_text_sentiment_neutral(self):
        """Test sentiment analysis with neutral text."""
        text = "Company announces quarterly results"
        result = analyze_text_sentiment(text)
        assert result["label"] == "neutral"
        assert -0.2 <= result["score"] <= 0.2
    
    def test_analyze_news_sentiment_empty(self):
        """Test news sentiment with empty articles."""
        result = analyze_news_sentiment([])
        assert result["score"] == 0.0
        assert result["label"] == "neutral"
        assert result["article_count"] == 0
    
    def test_get_sentiment_recommendation(self):
        """Test sentiment recommendation generation."""
        positive_sentiment = {"score": 0.5, "confidence": 0.8}
        rec = get_sentiment_recommendation(positive_sentiment)
        assert "BUY" in rec
        
        negative_sentiment = {"score": -0.5, "confidence": 0.8}
        rec = get_sentiment_recommendation(negative_sentiment)
        assert "SELL" in rec


class TestForecast:
    """Test forecasting functions."""
    
    def test_calculate_momentum_indicators(self):
        """Test momentum indicator calculations."""
        # Create sample price data
        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        prices = pd.DataFrame({
            'Close': range(100, 160)
        }, index=dates)
        
        result = calculate_momentum_indicators(prices)
        assert 'SMA_20' in result.columns
        assert 'SMA_50' in result.columns
        assert 'RSI' in result.columns
        assert 'MACD' in result.columns
    
    def test_get_trend_direction(self):
        """Test trend direction determination."""
        # Create upward trending data
        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        prices = pd.DataFrame({
            'Close': range(100, 160)
        }, index=dates)
        
        trend = get_trend_direction(prices)
        assert trend in ["bullish", "bearish", "neutral"]
    
    def test_generate_price_targets(self):
        """Test price target generation."""
        targets = generate_price_targets(
            current_price=100.0,
            volatility=0.2,
            sentiment_score=0.5
        )
        
        assert "low" in targets
        assert "mid" in targets
        assert "high" in targets
        assert "current" in targets
        assert targets["low"] < targets["current"] < targets["high"]


class TestPipeline:
    """Test main pipeline functions."""
    
    def test_generate_recommendation(self):
        """Test recommendation generation."""
        sentiment = {"score": 0.5, "confidence": 0.8}
        forecast_report = {"volatility": 0.2}
        trend = "bullish"
        
        rec = generate_recommendation(sentiment, forecast_report, trend)
        assert isinstance(rec, str)
        assert len(rec) > 0
    
    def test_run_pipeline_invalid_ticker(self):
        """Test pipeline with invalid ticker."""
        result = run_pipeline("invalid", include_sentiment=False, include_forecast=False)
        assert "error" in result
    
    def test_batch_analyze(self):
        """Test batch analysis functionality."""
        # This test just checks the function exists and returns a dict
        # In production, you'd mock the API calls
        tickers = ["AAPL"]
        # Skip actual execution to avoid API calls in tests
        assert callable(batch_analyze)


def test_load_tickers():
    """Test ticker loading from CSV."""
    # This will use default tickers if file doesn't exist
    tickers = load_tickers("data/tickers.csv")
    assert isinstance(tickers, list)
    assert len(tickers) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
