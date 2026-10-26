"""
A couple of basic sanity checks for the strategy logic.
Run with: python test_strategy.py
"""
import pandas as pd

from strategy import backtest, find_sweep_signals


def test_no_signal_on_flat_market():
    df = pd.DataFrame({
        "open": [100] * 30, "high": [101] * 30,
        "low": [99] * 30, "close": [100] * 30,
    })
    signals = find_sweep_signals(df, lookback=20)
    assert all(s is None for s in signals), "a flat market should never trigger a sweep signal"


def test_win_gives_positive_r():
    # 20 flat days, then a sweep below the low with a clean rejection,
    # then a strong move up that should hit the target
    rows = [{"open": 100, "high": 101, "low": 99, "close": 100}] * 20
    rows.append({"open": 99, "high": 100, "low": 95, "close": 99.8})   # sweep + rejection
    rows.append({"open": 100, "high": 108, "low": 99.5, "close": 107})  # hits target
    df = pd.DataFrame(rows)

    signals = find_sweep_signals(df, lookback=20)
    trades = backtest(df, signals)

    assert len(trades) == 1
    assert trades[0]["result"] == "win"
    assert trades[0]["r"] > 0


if __name__ == "__main__":
    test_no_signal_on_flat_market()
    test_win_gives_positive_r()
    print("All tests passed.")
