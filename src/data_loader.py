import datetime as dt
from typing import Optional
import yfinance as yf
import pandas as pd

from .config import ScreenerConfig

def download_price_data(ticker: str, cfg: ScreenerConfig) -> pd.DataFrame:
    end = dt.date.today()
    start = end - dt.timedelta(days=cfg.lookback_years * 365)

    df = yf.download(ticker, start=start, end=end, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No data for {ticker}")
    df = df.rename(columns=str.lower)
    df = df[['close', 'volume']].dropna()
    return df

def fetch_fundamentals(ticker: str) -> Optional[dict]:
    info = yf.Ticker(ticker).info
    if not info:
        return None
    return {
        "market_cap": info.get("marketCap"),
        "trailing_pe": info.get("trailingPE"),
        "ebit": info.get("ebitda"),  # proxy
        "operating_cashflow": info.get("operatingCashflow"),
        "country": info.get("country"),
        "sector": info.get("sector"),
        "longName": info.get("longName", ticker),
    }
