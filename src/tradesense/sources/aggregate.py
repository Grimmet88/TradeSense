import os
from typing import List
from datetime import datetime
from .base import Headline, dedupe
from .rss import fetch_headlines_rss
from .newsapi import fetch_headlines_newsapi
from .fmp import fetch_headlines_fmp
from .finnhub import fetch_headlines_finnhub

def fetch_all_headlines(tickers: List[str], since_hours: int = None, limit: int = None) -> List[Headline]:
    since_hours = since_hours or int(os.getenv("NEWS_SINCE_HOURS", "48"))
    limit = limit or int(os.getenv("NEWS_LIMIT", "300"))

    items: List[Headline] = []

    # RSS (no key)
    items.extend(fetch_headlines_rss(limit=limit, since_hours=since_hours))

    # NewsAPI (optional)
    try:
        items.extend(fetch_headlines_newsapi(limit=min(100, limit), since_hours=since_hours))
    except Exception:
        pass

    # FMP (optional; can pass tickers so it biases to your universe)
    try:
        items.extend(fetch_headlines_fmp(limit=min(150, limit), since_hours=since_hours, tickers=tickers))
    except Exception:
        pass

    # Finnhub company news (optional; directly ticker-focused)
    try:
        items.extend(fetch_headlines_finnhub(tickers=tickers, since_hours=since_hours, limit_per_ticker=10))
    except Exception:
        pass

    # De-dupe and cap
    items = dedupe(items)
    items.sort(key=lambda x: x.published_at, reverse=True)
    return items[:limit]

