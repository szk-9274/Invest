# Task: TradingView-like Chart Generation Improvement (Phase 1)

## Context
Current chart generation exists but does not meet usability requirements.
The generated charts:
- Are not year-scale price charts
- Do not resemble TradingView UI
- Do not clearly show trend, moving averages, or trade context
- Do not yet visualize IN/OUT points per trade

This task focuses ONLY on improving the chart generation UI and structure.
Trade IN/OUT markers will be handled in a later task.

---

## Objective (Phase 1 Only)
Implement a TradingView-inspired annual price chart generator that:
- Displays ~1 year of daily OHLC data
- Visually resembles TradingView as closely as possible using matplotlib / mplfinance
- Includes common indicators (moving averages, volume)
- Can generate a chart for an arbitrary ticker via function arguments
- Saves the generated chart image deterministically to disk

NO trade markers (IN/OUT) are required in this phase.

---

## Explicit Non-Goals (Do NOT implement yet)
- Do not draw ENTRY / EXIT markers
- Do not connect to trade_log.csv yet
- Do not rank tickers
- Do not remove existing chart features
- Do not change backtest logic

---

## Functional Requirements

### 1. Chart Generator API
Create or refactor a function with the following signature:

```
generate_price_chart(
    ticker: str,
    start_date: str,
    end_date: str,
    output_dir: str,
    style: str = "tradingview"
) -> Path
```

Behavior:
- Generates ONE chart image per call
- Returns the saved image path
- Deterministic output filename: `{ticker}_price_chart.png`

---

### 2. Chart Visual Specification (TradingView-like)

The chart MUST include:

#### Price Panel
- Candlestick chart (daily)
- Black / dark background
- Green for up candles, red for down candles
- Proper candle wicks and bodies

#### Indicators
- SMA 20
- SMA 50
- SMA 200
- Bollinger Bands (20, 2) if feasible
- Volume bars aligned under price panel

#### Layout
- Single figure
- Price chart on top
- Volume panel below
- Shared x-axis (date)
- Proper margins (no cramped layout)

#### Styling
- Dark background (similar to TradingView dark mode)
- Thin grid lines
- Clear date labels (monthly ticks)
- No overlapping text
- No debug text printed on chart

---

### 3. Data Scope
- Use approximately 1 year of data (start_date → end_date)
- If data is missing, fail loudly with a clear exception
- Do NOT silently skip chart generation

---

### 4. Output Behavior
- Charts must be saved to:
  ```
  output/charts/{ticker}_price_chart.png
  ```
- Ensure directory exists or create it
- After generation, log:
  ```
  INFO | Chart generated: output/charts/{ticker}_price_chart.png
  ```

---

## Implementation Guidance

### Libraries
- Use mplfinance where possible
- matplotlib customization is allowed
- Do NOT introduce new visualization libraries unless strictly necessary

### Code Location
Prefer:
```
python/backtest/ticker_charts.py
```

Refactor if needed, but keep chart logic isolated.

---

## Acceptance Criteria

- Running the generator for a single ticker produces:
  - A visually readable, year-scale candlestick chart
  - Moving averages clearly visible
  - Volume visible
  - Saved image confirmed on disk
- Chart resembles TradingView UI more than the current implementation
- No trade markers are drawn yet
- Existing features are not broken

---

## Next Planned Task (Not in this PR)
Phase 2 will:
- Load trade_log.csv
- Overlay ENTRY / EXIT markers
- Annotate IN / OUT reasons per trade

Do NOT implement Phase 2 now.

---

## Instruction
Proceed step by step.
If any ambiguity exists, prefer explicit failure over silent behavior.
