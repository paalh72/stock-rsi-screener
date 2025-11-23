import pandas as pd
from .config import ScreenerConfig
from .data_loader import download_price_data, fetch_fundamentals
from .screener import screen_ticker
from .backtest import backtest_rsi_strategy

def main():
    cfg = ScreenerConfig()

    # Start med et lite univers for testing
    tickers = ["AAPL", "MSFT", "NVDA", "TSLA"]

    results = []
    for t in tickers:
        print(f"Screening {t}...")
        res = screen_ticker(
            t,
            cfg,
            loader=download_price_data,
            fundamentals_loader=fetch_fundamentals,
        )
        if res:
            results.append(res)

    if not results:
        print("Ingen aksjer matchet kriteriene.")
        return

    df_res = pd.DataFrame(results).sort_values("hit_rate", ascending=False)
    print(df_res)

    # Backtest på beste aksje
    best = df_res.iloc[0]["ticker"]
    print(f"\nBacktester {best}...")
    from .data_loader import download_price_data
    prices = download_price_data(best, cfg)
    curve = backtest_rsi_strategy(prices, cfg)
    print(curve.tail())

if __name__ == "__main__":
    main()
