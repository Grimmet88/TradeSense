import time
import feedparser
from datetime import datetime, timezone, timedelta
from typing import List
from .base import Headline, dedupe, env_list

DEFAULT_FEEDS = [
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "https://www.marketwatch.com/feeds/topstories",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.investopedia.com/feedbuilder/feed/getfeed?feedName=news",
    "https://www.ft.com/?format=rss",
    "https://www.reuters.com/markets/rss",
]

def _parse_time(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

def fetch_headlines_rss(limit: int = 150, since_hours: int = 48) -> List[Headline]:
    feeds = env_list("RSS_FEEDS", DEFAULT_FEEDS)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    items: List[Headline] = []
    for url in feeds:
        feed = feedparser.parse(url)
        for e in feed.entries[:100]:
            ts = _parse_time(e)
            if ts < cutoff: 
                continue
            items.append(Headline(
                title=(e.get("title") or "").strip(),
                summary=(e.get("summary") or "").strip(),
                link=e.get("link") or "",
                source=feed.feed.get("title", url),
                published_at=ts,
            ))
        time.sleep(0.15)  # be polite
    items.sort(key=lambda x: x.published_at, reverse=True)
    return dedupe(items)[:limit]

