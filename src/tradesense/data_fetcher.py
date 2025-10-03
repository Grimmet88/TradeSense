import pandas as pd
import yfinance as yf

def fetch_prices(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """
    Download OHLCV data for a ticker and return a clean DataFrame with lowercased columns.
    """
    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    # Normalize and ensure expected columns
    df = df.rename(columns=str.lower)
    # yfinance may return 'adj close'; we keep 'close' as auto_adjust=True already adjusts
    expected = {"open", "high", "low", "close", "volume"}
    missing = expected - set(df.columns)
    if missing:
        # Some intervals don’t include volume; fill if missing
        for m in missing:
            if m == "volume":
                df["volume"] = 0
    return df.dropna()

