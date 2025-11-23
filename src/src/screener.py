from typing import List, Tuple
import pandas as pd
import numpy as np

from .config import ScreenerConfig

def find_rsi_cycles(df: pd.DataFrame, cfg: ScreenerConfig) -> List[Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    """
    Returnerer liste av (bunn_dato, topp_dato, neste_bunn_dato)
    hvor RSI går: < rsi_low -> > rsi_high -> < rsi_low
    """
    rsi = df["rsi"]
    dates = df.index

    lows = rsi < cfg.rsi_low
    highs = rsi > cfg.rsi_high

    cycles = []
    i = 0
    n = len(df)

    while i < n:
        # finn bunn
        while i < n and not lows.iloc[i]:
            i += 1
        if i >= n:
            break
        low1_idx = i

        # finn topp etter bunn
        while i < n and not highs.iloc[i]:
            i += 1
        if i >= n:
            break
        high_idx = i

        # finn ny bunn etter topp
        while i < n and not lows.iloc[i]:
            i += 1
        if i >= n:
            break
        low2_idx = i

        cycles.append((dates[low1_idx], dates[high_idx], dates[low2_idx]))
    return cycles

def evaluate_cycles(df: pd.DataFrame, cycles, cfg: ScreenerConfig) -> dict:
    """
    Sjekker:
    - prisdifferanse mellom bunn og topp >= 10 %
    - neste bunn høyere enn forrige
    - hit rate: >10 % oppgang innen 3 mnd etter bunn
    """
    close = df["close"]
    valid_cycles = []
    hits = 0

    for low1_date, high_date, low2_date in cycles:
        low1_price = close.loc[low1_date]
        high_price = close.loc[high_date]
        low2_price = close.loc[low2_date]

        # 10 % mellom bunn og topp
        if (high_price - low1_price) / low1_price < cfg.min_price_move_from_low:
            continue

        # høyere neste bunn
        if low2_price <= low1_price:
            continue

        valid_cycles.append((low1_date, high_date, low2_date))

        # hit rate – 10 % oppgang innen 3 mnd etter low1
        end_date = low1_date + pd.Timedelta(days=cfg.max_days_for_move)
        window = close.loc[low1_date:end_date]
        if len(window) == 0:
            continue
        max_price = window.max()
        if (max_price - low1_price) / low1_price > cfg.min_price_move_from_low:
            hits += 1

    cycles_count = len(valid_cycles)
    hit_rate = hits / cycles_count if cycles_count > 0 else 0.0

    return {
        "valid_cycles": cycles_count,
        "hits": hits,
        "hit_rate": hit_rate,
    }

def check_moving_average_condition(df: pd.DataFrame, cfg: ScreenerConfig) -> bool:
    cond = df["sma_short"] > df["sma_long"]
    ratio = cond.mean()  # andel dager
    return ratio >= cfg.min_ma_above_ratio

def passes_fundamental_filters(fund: dict, df: pd.DataFrame, cfg: ScreenerConfig) -> bool:
    if fund is None:
        return False

    mc = fund.get("market_cap")
    pe = fund.get("trailing_pe")
    ebit = fund.get("ebit")
    cf = fund.get("operating_cashflow")

    if mc is None or mc < cfg.min_market_cap:
        return False
    if pe is None or not (cfg.min_pe <= pe <= cfg.max_pe):
        return False
    if cfg.require_positive_ebit and (ebit is None or ebit <= 0):
        return False
    if cfg.require_positive_cashflow and (cf is None or cf <= 0):
        return False

    # 12m prisendring
    if len(df) < 252:
        return False
    last_price = df["close"].iloc[-1]
    price_12m_ago = df["close"].iloc[-252]
    if (last_price - price_12m_ago) / price_12m_ago < cfg.require_12m_price_change:
        return False

    # volum og pris
    if df["volume"].iloc[-30:].mean() < cfg.min_volume:
        return False
    if last_price < cfg.min_price:
        return False

    return True

def screen_ticker(ticker: str, cfg: ScreenerConfig, loader, fundamentals_loader) -> dict:
    """
    loader: funksjon(ticker, cfg) -> df
    fundamentals_loader: funksjon(ticker) -> dict
    Returnerer dict med resultater eller None hvis feiler/ikke passer.
    """
    try:
        df = loader(ticker, cfg)
    except Exception:
        return None

    fund = fundamentals_loader(ticker)
    if not passes_fundamental_filters(fund, df, cfg):
        return None

    from .indicators import add_indicators
    df = add_indicators(df, cfg.rsi_period, cfg.ma_short, cfg.ma_long).dropna()

    cycles = find_rsi_cycles(df, cfg)
    stats = evaluate_cycles(df, cycles, cfg)

    if stats["valid_cycles"] < cfg.min_rsi_cycles or stats["hits"] < 3:
        return None

    if not check_moving_average_condition(df, cfg):
        return None

    return {
        "ticker": ticker,
        "name": fund.get("longName", ticker),
        "market_cap": fund.get("market_cap"),
        "pe": fund.get("trailing_pe"),
        "valid_cycles": stats["valid_cycles"],
        "hits": stats["hits"],
        "hit_rate": stats["hit_rate"],
    }
