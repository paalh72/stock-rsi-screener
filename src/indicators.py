import pandas as pd
import numpy as np

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    gain = pd.Series(gain, index=series.index)
    loss = pd.Series(loss, index=series.index)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_indicators(df, rsi_period=14, ma_short=50, ma_long=200):
    df = df.copy()
    df["rsi"] = compute_rsi(df["close"], rsi_period)
    df["sma_short"] = df["close"].rolling(ma_short).mean()
    df["sma_long"] = df["close"].rolling(ma_long).mean()
    return df
