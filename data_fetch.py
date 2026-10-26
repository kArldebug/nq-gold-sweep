"""
Downloads daily price history for Nasdaq-100 futures and Gold futures
from Yahoo Finance, and does some basic cleaning.
"""
import pandas as pd
import yfinance as yf

TICKERS = {
    "NQ=F": "Nasdaq-100 Futures",
    "GC=F": "Gold Futures",
}


def get_data(ticker, start="2019-01-01"):
    df = yf.download(ticker, start=start, progress=False)

    # yfinance sometimes returns multi-level columns, flatten them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [c.lower() for c in df.columns]

    df = df.dropna()
    df["return"] = df["close"].pct_change()
    return df


if __name__ == "__main__":
    for ticker, name in TICKERS.items():
        df = get_data(ticker)
        print(f"{name} ({ticker}): {len(df)} days, from {df.index[0].date()} to {df.index[-1].date()}")
