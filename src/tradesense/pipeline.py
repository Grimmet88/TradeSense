# src/tradesense/pipeline.py
from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from loguru import logger

from .data_fetcher import fetch_prices_batch
from .data_analysis import compute_indicators
from .machine_learning import Model

# News + sentiment plumbing
from .sources.aggregate import fetch_all_headlines
from .sources.match_news import map_headlines_to_tickers
from .nlp.sentiment import (
    score_headlines,
    aggregate_sentiment,
    aggregate_per_ticker,
)


class Pipeline:
    def __init__(self, tickers=None, period: str = "6mo", interval: str = "1d"):
        """
        tickers: list[str] – symbols to analyze
        period:  e.g. '1mo','3mo','6mo','1y','5y','max'
        interval:e.g. '1d','1h','30m','15m','5m','1m'
        """
        self.tickers = tickers or ["AAPL", "MSFT", "NVDA"]
        self.period = period
        self.interval = interval
        self.model = Model()

    def run(self) -> dict:
        logger.info(f"Fetching data for: {len(self.tickers)} tickers")

        # 1) Prices (batch) -> Indicators
        frames = fetch_prices_batch(self.tickers, self.period, self.interval, batch_size=80)
        logger.info("Computing indicators…")
        feats = {t: compute_indicators(df) for t, df in frames.items() if not df.empty}
        if not feats:
            logger.warning("No features computed (empty price data). Returning empty result.")
            return {"meta": {"news": {"avg": 0.0, "n": 0, "pos": 0, "neg": 0, "neu": 0}}}

        # 2) Unified headlines (RSS + optional APIs), market & per-ticker sentiment
        logger.info("Fetching aggregated headlines…")
        heads = fetch_all_headlines(list(feats.keys()))  # returns List[Headline]
        # Convert to plain dicts for the existing sentiment helpers
        scored = score_headlines([h.to_dict() for h in heads])

        market_news = aggregate_sentiment(scored)                   # overall market sentiment
        mapped = map_headlines_to_tickers(scored, list(feats.keys()))  # per-ticker buckets
        per_ticker_news = aggregate_per_ticker(mapped)              # per-ticker aggregates

        # 3) Score with model
        logger.info("Scoring signals…")
        results = {
            t: self.model.score(
                feats[t],
                news_market=market_news,
                news_ticker=per_ticker_news.get(t)
            )
            for t in feats.keys()
        }

        logger.success("Pipeline run complete")

        # Include meta so the UI can show sentiment summaries.
        # Keep both keys for backward compatibility: 'news' and 'news_market'.
        return {
            "meta": {
                "news": market_news,
                "news_market": market_news,
            },
            **results
        }

