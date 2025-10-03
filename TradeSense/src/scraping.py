import feedparser
import requests

def fetch_news():
    # Test with NPR to confirm if feeds work at all
    test_rss = "https://www.npr.org/rss/rss.php?id=1001"
    feed = feedparser.parse(test_rss)
    print(f"NPR entries: {len(feed.entries)}")

    # Try fetching raw feed from Reuters as example
    url = "https://feeds.reuters.com/reuters/businessNews"
    try:
        resp = requests.get(url)
        print(f"Reuters HTTP status: {resp.status_code}")
        print(f"First 500 chars:\n{resp.text[:500]}")
    except Exception as e:
        print(f"Error fetching Reuters: {e}")

    # Original finance RSS feeds (will also try to parse)
    rss_urls = [
        "https://finance.yahoo.com/news/rssindex",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.marketwatch.com/rss/topstories",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.ft.com/?format=rss",
        "https://seekingalpha.com/market_currents.xml",
        "https://www.investopedia.com/feedbuilder/feed/getfeed?feedName=rss_headline",
        "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    ]
    articles = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            print(f"Parsed {url}, entries: {len(feed.entries)}")
            for entry in feed.entries:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                })
        except Exception as e:
            print(f"Error parsing {url}: {e}")
    print(f"Fetched {len(articles)} articles from RSS feeds.")
    return articles

def fetch_prices(tickers):
    import pandas as pd
    import numpy as np
    prices = pd.DataFrame(index=range(20), columns=tickers)
    for t in tickers:
        prices[t] = np.random.normal(100, 10, size=20)
    return prices
