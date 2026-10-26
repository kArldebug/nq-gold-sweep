"""
A few basic technical indicators used to describe the trend.
"""


def sma(series, window):
    """Simple moving average."""
    return series.rolling(window).mean()


def rsi(series, period=14):
    """Relative Strength Index — measures if an asset is overbought/oversold."""
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
