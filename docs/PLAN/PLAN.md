# Phase A–C: Backtest Visualization Enhancement & TradingView-style Web UI Implementation Plan (Revised)

## Background
The current backtest visualization has the following issues:

- Chart generation fails when price data is empty or insufficient
- Errors stop the entire chart generation process
- Charts are file-output oriented, resulting in poor usability and visibility
- IN / OUT points for Top / Bottom tickers cannot be visually verified
- Charts cannot be browsed, switched, or zoomed like TradingView

This plan aims to:

1. Harden chart generation logic with full edge-case handling
2. Provide a TradingView-style Web UI running on localhost
3. Enable visual verification of IN / OUT points for Top / Bottom tickers


============================================================
Phase A-1: Chart Generation Edge Case Handling (Confirmed)
============================================================

### Scope
- python/backtest/ticker_charts.py
- All chart generation entry points

### Requirements

#### 1. Empty Data Detection
Before generating any chart, validate:

- DataFrame is None
- DataFrame is empty
- DataFrame has zero rows

If any condition matches, skip chart generation without raising an exception.

#### 2. Insufficient Data Detection
Skip chart generation if any of the following apply:

- Number of OHLC bars < MIN_REQUIRED_BARS (e.g. 50–100)
- Not enough data to compute SMA20 / SMA50 / SMA200

#### 3. Skip Logging
When skipping chart generation, always emit a WARNING log.

Examples:
- Skipping chart for TICKER: no price data in selected period
- Skipping chart for TICKER: insufficient bars (34 < required 50)

#### 4. Exception Resilience
- Catch mplfinance / numpy / pandas related exceptions
- Log ERROR with ticker name and exception message
- Continue processing remaining tickers

============================================================
Phase A-2: Chart Generation Interface Standardization (UI-Oriented)
============================================================

### Unified Interface
All chart generation functions must accept the following parameters:

- ticker
- price_df
- trades_df (IN / OUT information)
- start_date
- end_date
- chart_mode (daily / weekly / auto)

### chart_mode=auto Behavior
- Automatically resample to weekly when data volume is large
- Use daily when data volume is small
- Automatically suppress "too much data" warnings

============================================================
Phase B: TradingView-style Web UI Foundation (FastAPI + React Fixed)
============================================================

## Technology Stack (Confirmed)
- Backend: FastAPI
- Frontend: React
- Charting: Plotly (Candlestick)
- Runtime: localhost (Web Application)
- Desktop app packaging is out of scope

## Dependency Note
Phase B-2 (Chart UI) depends on Phase B-1 (Web Application Foundation).
Phase B-1 must be completed first.

============================================================
Phase B-1: Minimal Web Application Foundation (Required)
============================================================

### Proposed Directory Structure

- backend/
  - main.py (FastAPI entry point)
  - api/
    - backtest.py
    - charts.py
  - services/
    - backtest_runner.py
    - result_loader.py
- frontend/
  - src/
    - pages/
      - Home.tsx
      - Chart.tsx
    - components/
      - BacktestForm.tsx
      - TickerList.tsx
    - api/
      - client.ts

### Features

#### 1. Backtest Execution
- Input fields for start / end dates
- "Run Backtest" button
- Invoke existing Python backtest logic internally

#### 2. Result Retrieval
- trade_log.csv
- ticker_stats.csv
- Retrieve Top 5 / Bottom 5 tickers via API

#### 3. Ticker List Display
- Top 5 Winners
- Bottom 5 Losers
- Click to navigate to chart view

============================================================
Phase B-2: TradingView-style Chart UI
============================================================

### UI Requirements

- Candlestick chart
- Volume bars
- Moving averages:
  - SMA20
  - SMA50
  - SMA200
- Dark theme
- Wide horizontal layout optimized for 1-year view
- Zoom and pan interaction
- TradingView-like color scheme and grid

### Implementation Notes

- Use Plotly Candlestick charts
- Render directly in the browser (no image file output)
- Re-render chart on ticker selection

============================================================
Phase C: IN / OUT Marker Rendering & Time Range Control
============================================================

### IN / OUT Markers

- Render markers based on trade_log.csv
- Clearly distinguish Entry and Exit with color
- Marker tooltips must include:
  - Entry date / price
  - Exit date / price
  - P&L
  - Holding period (days)

### Chart Time Range Control

- Full-period view
- Auto-focus from first Entry to last Exit
- Allow user-controlled time range switching

### Notes
- Support multiple overlapping trades
- Ensure marker placement remains readable
