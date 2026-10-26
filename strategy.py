"""
Liquidity sweep strategy.

The idea: price often makes a fake break below a recent low (or above a
recent high) to grab the stop-losses resting there, then reverses. This
module looks for that pattern on daily candles and backtests a simple
rule: when it happens, enter a trade in the reversal direction, risk a
fixed amount, and aim for 1.5x that risk as a target.

Note: my actual live trading confirms this pattern on 15-minute candles.
Free 15-minute history only goes back about 60 days on Yahoo Finance, so
to backtest over several years I use daily candles here instead. Same
idea, different timeframe.
"""


def find_sweep_signals(df, lookback=20):
    """
    For each day, checks if it swept the low/high of the previous
    `lookback` days and closed back on the other side. Returns a list
    the same length as df: "long", "short", or None for each day.
    """
    signals = [None] * lookback

    for i in range(lookback, len(df)):
        recent = df.iloc[i - lookback:i]
        today = df.iloc[i]

        pool_low = recent["low"].min()
        pool_high = recent["high"].max()

        swept_low = today["low"] < pool_low and today["close"] > pool_low
        swept_high = today["high"] > pool_high and today["close"] < pool_high

        if swept_low:
            signals.append("long")
        elif swept_high:
            signals.append("short")
        else:
            signals.append(None)

    return signals


def backtest(df, signals, risk_reward=1.5, max_days_held=10):
    """
    Simple trade-by-trade backtest. Only one trade open at a time:
    enters the day after a signal, exits on stop-loss, target, or after
    `max_days_held` days (whichever comes first).
    """
    trades = []
    i = 0

    while i < len(df) - 1:
        if signals[i] is None:
            i += 1
            continue

        direction = signals[i]
        entry_price = df.iloc[i + 1]["open"]

        if direction == "long":
            stop = df.iloc[i]["low"]
            risk = entry_price - stop
            target = entry_price + risk_reward * risk
        else:
            stop = df.iloc[i]["high"]
            risk = stop - entry_price
            target = entry_price - risk_reward * risk

        if risk <= 0:
            i += 1
            continue

        result, exit_price, j = None, None, i + 1
        last_j = min(i + 1 + max_days_held, len(df) - 1)

        for j in range(i + 1, last_j + 1):
            bar = df.iloc[j]
            if direction == "long":
                if bar["low"] <= stop:
                    result, exit_price = "loss", stop
                    break
                if bar["high"] >= target:
                    result, exit_price = "win", target
                    break
            else:
                if bar["high"] >= stop:
                    result, exit_price = "loss", stop
                    break
                if bar["low"] <= target:
                    result, exit_price = "win", target
                    break

        if result is None:
            result, exit_price = "timeout", df.iloc[j]["close"]

        r_multiple = risk_reward if result == "win" else (-1 if result == "loss" else 0)
        trades.append({
            "date": df.index[i],
            "direction": direction,
            "entry": entry_price,
            "exit": exit_price,
            "result": result,
            "r": r_multiple,
        })

        i = j + 1  # don't look for a new signal until this trade is closed

    return trades
