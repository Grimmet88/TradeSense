import pandas as pd
from src.scraping import fetch_news, fetch_prices
from src.sentiment import analyze_sentiment
from src.forecast import get_momentum_score
from src.utils import get_action, mentions_ticker

def main():
    tickers = pd.read_csv('data/tickers.csv', header=None)[0].tolist()
    prices = fetch_prices(tickers)
    momentum = get_momentum_score(prices)
    ranked = momentum.sort_values(ascending=False)

    articles = fetch_news()
    news_results = []
    for a in articles:
        sentiment = analyze_sentiment(a.get("title", "") + " " + a.get("summary", ""))
        mentioned = mentions_ticker(a, tickers)
        if mentioned:
            news_results.append({
                "title": a["title"],
                "link": a["link"],
                "sentiment": sentiment,
                "tickers": mentioned
            })

    avg_sentiment = {ticker: 0 for ticker in tickers}
    for nr in news_results:
        for ticker in nr['tickers']:
            avg_sentiment[ticker] += nr['sentiment']
    for ticker in avg_sentiment:
        avg_sentiment[ticker] /= max(1, sum(ticker in nr['tickers'] for nr in news_results))

    decisions = {}
    for ticker in tickers:
        momentum_score = ranked.get(ticker, 0)
        sentiment_score = avg_sentiment.get(ticker, 0)
        action = get_action(momentum_score, sentiment_score)
        decisions[ticker] = {
            "momentum": momentum_score,
            "sentiment": sentiment_score,
            "action": action
        }

    return ranked, news_results, decisions
