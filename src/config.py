from dataclasses import dataclass

@dataclass
class ScreenerConfig:
    # Univers
    lookback_years: int = 5

    # Screening – fundamentalt
    min_market_cap: float = 1_000_000_000  # USD
    min_history_years: int = 3
    min_price: float = 1.0
    min_volume: int = 1_000_000
    min_pe: float = 6.0
    max_pe: float = 30.0
    require_positive_ebit: bool = True
    require_positive_cashflow: bool = True
    require_12m_price_change: float = 0.10  # 10 %

    # RSI / trend
    rsi_period: int = 14
    rsi_low: float = 20.0
    rsi_high: float = 70.0
    min_rsi_cycles: int = 5
    min_price_move_from_low: float = 0.10  # 10 %
    max_days_for_move: int = 90  # ca 3 mnd

    # MA
    ma_short: int = 50
    ma_long: int = 200
    min_ma_above_ratio: float = 0.5  # 50 %

