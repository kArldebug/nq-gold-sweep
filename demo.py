"""
Runs the strategy on real Nasdaq-100 and Gold data, prints the results,
and saves a candlestick chart for each (dark theme, similar to what I
use on TradingView for the actual chart analysis).
"""
import numpy as np
import pandas as pd
import mplfinance as mpf

from data_fetch import TICKERS, get_data
from strategy import backtest, find_sweep_signals

# Dark style approximating TradingView's default chart colors
CHART_STYLE = mpf.make_mpf_style(
    base_mpf_style="nightclouds",
    marketcolors=mpf.make_marketcolors(up="#089981", down="#f23645", edge="inherit", wick="inherit"),
    facecolor="#131722", edgecolor="#131722", figcolor="#131722", gridcolor="#2a2e39", gridstyle="-",
    rc={"axes.labelcolor": "#d1d4dc", "xtick.color": "#d1d4dc", "ytick.color": "#d1d4dc", "text.color": "#d1d4dc"},
)


def run(ticker, name):
    print(f"\n=== {name} ({ticker}) ===")
    df = get_data(ticker)

    signals = find_sweep_signals(df)
    trades = backtest(df, signals)

    print(f"Trades: {len(trades)}")
    if trades:
        wins = [t for t in trades if t["result"] == "win"]
        total_r = sum(t["r"] for t in trades)
        print(f"Win rate: {len(wins) / len(trades):.1%}")
        print(f"Total R: {total_r:+.1f}")

    # mplfinance expects capitalized OHLC column names
    chart_df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"})

    buy_markers = pd.Series(np.nan, index=chart_df.index)
    sell_markers = pd.Series(np.nan, index=chart_df.index)
    for t in trades:
        if t["direction"] == "long":
            buy_markers.loc[t["date"]] = chart_df.loc[t["date"], "Low"] * 0.995
        else:
            sell_markers.loc[t["date"]] = chart_df.loc[t["date"], "High"] * 1.005

    addplots = [
        mpf.make_addplot(buy_markers, type="scatter", markersize=60, marker="^", color="#089981"),
        mpf.make_addplot(sell_markers, type="scatter", markersize=60, marker="v", color="#f23645"),
    ]

    filename = f"{ticker.replace('=', '_')}_chart.png"
    mpf.plot(
        chart_df, type="candle", style=CHART_STYLE, addplot=addplots, mav=(20, 50),
        mavcolors=["#2962ff", "#ff6d00"],
        title=f"{name} — liquidity sweep trades", ylabel="Price",
        figsize=(11, 6), savefig=dict(fname=filename, dpi=150),
    )
    print(f"Chart saved: {filename}")

    return trades


if __name__ == "__main__":
    for ticker, name in TICKERS.items():
        run(ticker, name)
