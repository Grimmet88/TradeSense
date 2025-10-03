import os, requests
from datetime import datetime, timezone, timedelta
from typing import List
from .base import Headline, dedupe

FMP_URL = "https://financialmodelingprep.com/api/v3/stock_news"

def fetch_headlines_fmp(limit: int = 100, since_hours: int = 48, tickers: list = None) -> List[Headline]:
    key = os.getenv("FMP_API_KEY")
    if not key:
        return []
    params = {"limit": str(min(limit, 250)), "apikey": key}
    if tickers:
        params["tickers"] = ",".join(tickers[:50])

    try:
        r = requests.get(FMP_URL, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    out: List[Headline] = []
    for item in data:
        ts = item.get("publishedDate")  # e.g. "2024-01-31 14:30:00"
        try:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)
        if dt < cutoff:
            continue
        out.append(Headline(
            title=(item.get("title") or "").strip(),
            summary=(item.get("text") or "").strip(),
            link=item.get("url") or "",
            source=item.get("site") or "FMP",
            published_at=dt
        ))
    out.sort(key=lambda x: x.published_at, reverse=True)
    return dedupe(out)[:limit]

