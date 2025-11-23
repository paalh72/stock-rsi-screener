# stock-rsi-screener
stock-rsi-screener

# RSI Trend Screener

Python-basert aksjescreener som:
- Filtrerer aksjer på fundamentale kriterier
- Identifiserer gjentakende RSI-baserte trender over 5 år
- Beregner historisk "hit rate" (>10 % oppgang etter bunner)
- Kjører en enkel RSI-basert backtest med equity curve

## Installasjon

```bash
git clone https://github.com/<brukernavn>/stock-rsi-screener.git
cd stock-rsi-screener
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
