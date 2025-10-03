import os, requests
from datetime import datetime, timezone, timedelta
from typing import List
from .base import Headline, dedupe

NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"

def fetch_headlines_newsapi(limit: int = 100, since_hours: int = 48, q: str = "stocks OR market OR earnings", language: str = "en") -> List[Headline]:
    key = os.getenv("NEWSAPI_KEY")
    if not key:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    params = {
        "apiKey": key,
        "language": language,
        "pageSize": min(limit, 100),
        "q": q,
    }
    try:
        r = requests.get(NEWSAPI_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    out: List[Headline] = []
    for a in data.get("articles", []):
        ts = a.get("publishedAt")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else datetime.now(timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)
        if dt < cutoff:
            continue
        out.append(Headline(
            title=(a.get("title") or "").strip(),
            summary=(a.get("description") or "").strip(),
            link=a.get("url") or "",
            source=(a.get("source", {}) or {}).get("name", "NewsAPI"),
            published_at=dt,
        ))
    out.sort(key=lambda x: x.published_at, reverse=True)
    return dedupe(out)[:limit]

