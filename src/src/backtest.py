import pandas as pd
import numpy as np
from .config import ScreenerConfig
from .indicators import add_indicators

def backtest_rsi_strategy(df: pd.DataFrame, cfg: ScreenerConfig, rsi_buy=30, rsi_sell=70):
    df = add_indicators(df, cfg.rsi_period, cfg.ma_short, cfg.ma_long).dropna().copy()

    position = 0  # 0 = ingen, 1 = long
    entry_price = 0.0
    equity = 1.0  # startkapital
    equity_curve = []

    for date, row in df.iterrows():
        price = row["close"]
        rsi = row["rsi"]

        # kjøpssignal
        if position == 0 and rsi < rsi_buy:
            position = 1
            entry_price = price

        # salgssignal
        elif position == 1 and rsi > rsi_sell:
            ret = (price - entry_price) / entry_price
            equity *= (1 + ret)
            position = 0

        equity_curve.append({"date": date, "equity": equity})

    curve = pd.DataFrame(equity_curve).set_index("date")
    return curve
