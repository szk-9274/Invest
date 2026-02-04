# Task: Investigate Missing Chart Outputs and Ensure Trade Entry/Exit Visualization

## Background

Backtest execution completes successfully and generates the following outputs:
- output/trade_log.csv
- output/ticker_stats.csv
- Console summary showing Top 5 Winners and Bottom 5 Losers

However, **no candlestick chart images are generated**, and the directory `output/charts/` does not exist after execution.

The codebase includes `python/backtest/ticker_charts.py`, and tests for chart generation are passing, but the functionality is not reflected in actual backtest runs.

## Objective

1. Identify and fix the root cause why candlestick charts are not generated during backtest execution.
2. Ensure charts are **automatically saved to disk** after each backtest run.
3. Generate charts for:
   - Top 5 winning tickers
   - Bottom 5 losing tickers
4. Each chart must clearly visualize:
   - Candlestick price data (1-year lookback)
   - Entry (IN) points
   - Exit (OUT) points
   - Entry reason (why the trade was opened)
   - Exit reason (why the trade was closed)

The goal is to visually verify that trade decisions align with strategy logic.

---

## Investigation Tasks (Root Cause Analysis)

Perform the following checks and document findings in code comments or logs:

1. Verify whether `generate_ticker_charts` (or equivalent) is called from the backtest execution path.
   - Confirm integration in `python/backtest/engine.py` or equivalent orchestrator.
2. Check if chart generation is gated behind:
   - Feature flags
   - Config values
   - CLI options
   - Conditional early returns
3. Confirm that:
   - `output/charts/` directory is created automatically if missing
   - Failures are not silently ignored
4. Ensure logging clearly indicates when:
   - Chart generation starts
   - Each ticker chart is generated
   - Output path is written

---

## Required Fixes

### 1. Ensure Chart Generation Is Executed

Modify the backtest completion flow so that chart generation is executed **unconditionally** after backtest results are finalized, at least for now.

Example intent (exact structure may differ):

- After ticker-level P&L analysis is completed
- After trade_log.csv and ticker_stats.csv are written
- Call chart generation with the exact tickers shown in console summary

### 2. Directory and File Output

- Automatically create `output/charts/` if it does not exist
- Save one image per ticker:
  - Naming format: `{TICKER}.png`
- Do not overwrite silently without logging

---

## Chart Requirements

Each chart must include:

- Time range: approximately 1 year (matching backtest period)
- Candlestick chart (mplfinance or equivalent)
- Visual markers:
  - Entry points (IN)
  - Exit points (OUT)
- Text annotations near markers:
  - Entry reason (e.g., price_above_sma50, breakout, etc.)
  - Exit reason (e.g., stop_loss, ma50_break, time_exit, etc.)

If annotations are too dense:
- Use numbered markers and include a legend or side table on the chart

---

## Data Sources

Use the following as authoritative inputs:

- trade_log.csv
  - ENTRY / EXIT timestamps
  - Ticker
  - Price
  - Reason
- ticker_stats.csv
  - Total P&L per ticker
  - Trade count

The Top 5 and Bottom 5 tickers must exactly match what is shown in the console summary.

---

## Validation Criteria

The task is complete when:

1. Running backtest produces:
   - output/charts/{TICKER}.png for all Top 5 and Bottom 5 tickers
2. Charts visibly show:
   - Correct entry/exit timing
   - Correct reasons
3. Console logs clearly indicate:
   - Chart generation start
   - Each generated chart file
4. No manual steps are required after running backtest

---

## Notes

- Tests may already exist; update or extend them only if needed.
- Prefer clarity and observability over configurability for this fix.
- This task is about **execution wiring and visibility**, not strategy logic changes.