"""
Sentiment analysis module for TradeSense.
Analyzes sentiment from news headlines and social media for stock predictions.
"""

from typing import Dict, List, Any
import re


def analyze_text_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a single text using keyword-based approach.
    
    Note: This is a simplified implementation. In production, use
    transformers library with a pre-trained model for better accuracy.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary containing sentiment score and label
    """
    # Positive and negative keywords
    positive_keywords = [
        'bullish', 'surge', 'rally', 'gain', 'profit', 'growth', 'strong',
        'upgrade', 'beat', 'outperform', 'positive', 'rise', 'climb', 'jump',
        'soar', 'boom', 'success', 'exceed', 'boost', 'impressive'
    ]
    
    negative_keywords = [
        'bearish', 'fall', 'drop', 'loss', 'decline', 'weak', 'downgrade',
        'miss', 'underperform', 'negative', 'plunge', 'crash', 'slump',
        'tumble', 'sink', 'concern', 'worry', 'risk', 'fail', 'disappoint'
    ]
    
    text_lower = text.lower()
    
    # Count keyword occurrences
    positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
    
    # Calculate sentiment score (-1 to 1)
    total = positive_count + negative_count
    if total == 0:
        score = 0.0
        label = "neutral"
        confidence = 0.5
    else:
        score = (positive_count - negative_count) / total
        confidence = abs(score)
        
        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"
    
    return {
        "score": score,
        "label": label,
        "confidence": confidence,
        "positive_count": positive_count,
        "negative_count": negative_count
    }


def analyze_news_sentiment(articles: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Analyze sentiment from multiple news articles.
    
    Args:
        articles: List of article dictionaries with 'title' and 'publisher' keys
        
    Returns:
        Dictionary containing aggregated sentiment analysis
    """
    if not articles:
        return {
            "score": 0.0,
            "label": "neutral",
            "confidence": 0.0,
            "article_count": 0,
            "details": []
        }
    
    sentiments = []
    details = []
    
    for article in articles:
        title = article.get("title", "")
        if title:
            sentiment = analyze_text_sentiment(title)
            sentiments.append(sentiment)
            details.append({
                "title": title,
                "sentiment": sentiment["label"],
                "score": sentiment["score"]
            })
    
    # Aggregate scores
    if sentiments:
        avg_score = sum(s["score"] for s in sentiments) / len(sentiments)
        avg_confidence = sum(s["confidence"] for s in sentiments) / len(sentiments)
        
        if avg_score > 0.1:
            overall_label = "positive"
        elif avg_score < -0.1:
            overall_label = "negative"
        else:
            overall_label = "neutral"
    else:
        avg_score = 0.0
        avg_confidence = 0.0
        overall_label = "neutral"
    
    return {
        "score": avg_score,
        "label": overall_label,
        "confidence": avg_confidence,
        "article_count": len(articles),
        "details": details
    }


def get_sentiment_recommendation(sentiment_data: Dict[str, Any]) -> str:
    """
    Generate trading recommendation based on sentiment analysis.
    
    Args:
        sentiment_data: Dictionary containing sentiment analysis results
        
    Returns:
        Trading recommendation string
    """
    score = sentiment_data.get("score", 0.0)
    confidence = sentiment_data.get("confidence", 0.0)
    
    if confidence < 0.3:
        return "HOLD - Low confidence in sentiment signal"
    
    if score > 0.3:
        return "BUY - Strong positive sentiment detected"
    elif score > 0.1:
        return "CONSIDER BUY - Moderate positive sentiment"
    elif score < -0.3:
        return "SELL - Strong negative sentiment detected"
    elif score < -0.1:
        return "CONSIDER SELL - Moderate negative sentiment"
    else:
        return "HOLD - Neutral sentiment"


def combine_sentiments(
    news_sentiment: Dict[str, Any],
    social_sentiment: Dict[str, Any] = None,
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Combine multiple sentiment sources with weighted average.
    
    Args:
        news_sentiment: Sentiment from news sources
        social_sentiment: Sentiment from social media (optional)
        weights: Dictionary of weights for each source
        
    Returns:
        Combined sentiment analysis
    """
    if weights is None:
        weights = {"news": 0.7, "social": 0.3}
    
    combined_score = news_sentiment["score"] * weights["news"]
    
    if social_sentiment:
        combined_score += social_sentiment["score"] * weights["social"]
    
    if combined_score > 0.1:
        label = "positive"
    elif combined_score < -0.1:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "score": combined_score,
        "label": label,
        "confidence": news_sentiment["confidence"],
        "sources": ["news"] + (["social"] if social_sentiment else [])
    }
