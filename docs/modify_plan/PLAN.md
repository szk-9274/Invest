There is a chart generation error caused by datetime timezone mismatch.

Observed error:
Invalid comparison between dtype=datetime64[ns, America/New_York] and Timestamp

Root cause:
- Price data (OHLCV DataFrame index) is timezone-aware (America/New_York)
- Entry/exit timestamps loaded from trade_log.csv are timezone-naive
- Pandas does not allow comparisons between tz-aware and tz-naive datetimes

Tasks:

1. Identify datetime comparison points
- Locate where entry/exit dates from trade_log.csv are compared against
  OHLCV dataframe index (e.g. slicing, filtering, marker placement)

2. Normalize datetime timezone
- Ensure all trade entry/exit timestamps are timezone-aware
- Use America/New_York as the standard timezone

Implementation requirements:
- When parsing trade_log.csv dates:
  - Convert to pandas Timestamp
  - If tz-naive, localize to America/New_York
  - If tz-aware, convert to America/New_York
- Ensure OHLCV dataframe index is also America/New_York

3. Safety checks
- Do not strip timezone information from price data
- Do not silently coerce datetimes to strings

4. Verification
- Run:
  python main.py --mode backtest
- Confirm:
  - No "Invalid comparison" errors
  - Charts are generated for Top 5 and Bottom 5 tickers
  - Entry/Exit markers are plotted at correct dates

This fix should only address datetime compatibility.
Do not remove any existing chart features.
