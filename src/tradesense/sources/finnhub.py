import os, requests
from datetime import datetime, timezone, timedelta
from typing import List
from .base import Headline, dedupe

FINNHUB_URL = "https://finnhub.io/api/v1/company-news"

def fetch_headlines_finnhub(tickers: list, since_hours: int = 48, limit_per_ticker: int = 30) -> List[Headline]:
    key = os.getenv("FINNHUB_API_KEY")
    if not key or not tickers:
        return []

    end = datetime.now(timezone.utc).date()
    start = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).date()
    out: List[Headline] = []

    for t in tickers[:60]:  # avoid huge loops
        params = {"symbol": t, "from": start.isoformat(), "to": end.isoformat(), "token": key}
        try:
            r = requests.get(FINNHUB_URL, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
        except Exception:
            continue
        count = 0
        for item in sorted(data, key=lambda x: x.get("datetime", 0), reverse=True):
            if count >= limit_per_ticker:
                break
            ts = item.get("datetime")  # epoch seconds
            dt = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else datetime.now(timezone.utc)
            out.append(Headline(
                title=(item.get("headline") or "").strip(),
                summary=(item.get("summary") or "").strip(),
                link=item.get("url") or "",
                source=item.get("source") or "Finnhub",
                published_at=dt
            ))
            count += 1
    out.sort(key=lambda x: x.published_at, reverse=True)
    return dedupe(out)

