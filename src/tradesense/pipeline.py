from loguru import logger
from .data_fetcher import fetch_prices
from .data_analysis import compute_indicators
from .machine_learning import Model


class Pipeline:
    def __init__(self, tickers=None, period="6mo", interval="1d"):
        self.tickers = tickers or ["AAPL", "MSFT"]
        self.period = period
        self.interval = interval
        self.model = Model()

    def run(self):
        logger.info(f"Fetching: {self.tickers}")
        frames = {t: fetch_prices(t, self.period, self.interval) for t in self.tickers}

        logger.info("Computing indicators")
        feats = {t: compute_indicators(df) for t, df in frames.items()}

        logger.info("Scoring")
        results = {t: self.model.score(feat) for t, feat in feats.items()}
        logger.success("Done")
        return results

