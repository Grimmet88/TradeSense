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
        logger.info(f"Fetching data for: {self.tickers}")

        # Step 1: fetch price data
        frames = {
            t: fetch_prices(t, self.period, self.interval) for t in self.tickers
        }

        # Step 2: compute indicators
        logger.info("Computing indicators...")
        features = {t: compute_indicators(df) for t, df in frames.items()}

        # Step 3: score with the model
        logger.info("Scoring signals...")
        results = {t: self.model.score(df) for t, df in features.items()}

        logger.success("Pipeline run complete")
        return results

