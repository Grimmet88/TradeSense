"""
Stock forecasting module for TradeSense.
Implements various forecasting methods including momentum-based and ML predictions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


def calculate_momentum_indicators(price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate momentum indicators for stock data.
    
    Args:
        price_data: DataFrame with historical price data
        
    Returns:
        DataFrame with added momentum indicators
    """
    df = price_data.copy()
    
    # Simple Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Exponential Moving Average
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    # MACD (Moving Average Convergence Divergence)
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df


def simple_momentum_forecast(
    price_data: pd.DataFrame,
    forecast_days: int = 7
) -> pd.DataFrame:
    """
    Generate simple momentum-based forecast.
    
    Args:
        price_data: Historical price data
        forecast_days: Number of days to forecast
        
    Returns:
        DataFrame with forecasted values
    """
    if price_data.empty or len(price_data) < 2:
        return pd.DataFrame()
    
    # Calculate recent trend
    recent_data = price_data['Close'].tail(14)
    trend = (recent_data.iloc[-1] - recent_data.iloc[0]) / len(recent_data)
    
    # Generate forecast
    last_date = price_data.index[-1]
    last_price = price_data['Close'].iloc[-1]
    
    forecast_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=forecast_days,
        freq='D'
    )
    
    # Simple linear projection with some randomness
    forecast_values = []
    current_price = last_price
    
    for i in range(forecast_days):
        # Add trend with dampening
        dampening = 0.95 ** i  # Reduce trend impact over time
        current_price += trend * dampening
        forecast_values.append(current_price)
    
    forecast_df = pd.DataFrame({
        'Forecast': forecast_values
    }, index=forecast_dates)
    
    return forecast_df


def calculate_volatility(price_data: pd.DataFrame, window: int = 20) -> float:
    """
    Calculate historical volatility.
    
    Args:
        price_data: Historical price data
        window: Rolling window for calculation
        
    Returns:
        Volatility value
    """
    if price_data.empty or len(price_data) < window:
        return 0.0
    
    returns = price_data['Close'].pct_change()
    volatility = returns.rolling(window=window).std().iloc[-1]
    
    return volatility * np.sqrt(252)  # Annualized volatility


def generate_price_targets(
    current_price: float,
    volatility: float,
    sentiment_score: float = 0.0
) -> Dict[str, float]:
    """
    Generate price targets based on volatility and sentiment.
    
    Args:
        current_price: Current stock price
        volatility: Historical volatility
        sentiment_score: Sentiment score (-1 to 1)
        
    Returns:
        Dictionary with price targets (low, mid, high)
    """
    # Adjust volatility based on sentiment
    sentiment_multiplier = 1 + (sentiment_score * 0.2)
    adjusted_volatility = volatility * sentiment_multiplier
    
    # Calculate targets
    low_target = current_price * (1 - adjusted_volatility * 0.5)
    mid_target = current_price * (1 + sentiment_score * 0.1)
    high_target = current_price * (1 + adjusted_volatility * 0.5)
    
    return {
        "low": round(low_target, 2),
        "mid": round(mid_target, 2),
        "high": round(high_target, 2),
        "current": round(current_price, 2)
    }


def get_trend_direction(price_data: pd.DataFrame) -> str:
    """
    Determine overall trend direction.
    
    Args:
        price_data: Historical price data with indicators
        
    Returns:
        Trend direction: "bullish", "bearish", or "neutral"
    """
    if price_data.empty or len(price_data) < 50:
        return "neutral"
    
    df = calculate_momentum_indicators(price_data)
    
    # Get latest values
    latest = df.iloc[-1]
    current_price = latest['Close']
    sma_20 = latest.get('SMA_20', current_price)
    sma_50 = latest.get('SMA_50', current_price)
    rsi = latest.get('RSI', 50)
    
    # Determine trend
    bullish_signals = 0
    bearish_signals = 0
    
    # Price above moving averages
    if current_price > sma_20:
        bullish_signals += 1
    else:
        bearish_signals += 1
    
    if current_price > sma_50:
        bullish_signals += 1
    else:
        bearish_signals += 1
    
    # Short MA above long MA (golden cross)
    if sma_20 > sma_50:
        bullish_signals += 1
    else:
        bearish_signals += 1
    
    # RSI analysis
    if rsi > 50:
        bullish_signals += 1
    elif rsi < 50:
        bearish_signals += 1
    
    if bullish_signals > bearish_signals:
        return "bullish"
    elif bearish_signals > bullish_signals:
        return "bearish"
    else:
        return "neutral"


def create_forecast_report(
    price_data: pd.DataFrame,
    forecast_data: pd.DataFrame,
    sentiment_score: float = 0.0
) -> Dict[str, Any]:
    """
    Create comprehensive forecast report.
    
    Args:
        price_data: Historical price data
        forecast_data: Forecasted price data
        sentiment_score: Sentiment score
        
    Returns:
        Dictionary containing forecast analysis
    """
    current_price = price_data['Close'].iloc[-1] if not price_data.empty else 0
    volatility = calculate_volatility(price_data)
    trend = get_trend_direction(price_data)
    targets = generate_price_targets(current_price, volatility, sentiment_score)
    
    return {
        "current_price": current_price,
        "forecast": forecast_data,
        "trend": trend,
        "volatility": volatility,
        "targets": targets,
        "indicators": calculate_momentum_indicators(price_data).tail(1).to_dict('records')[0] if not price_data.empty else {}
    }
