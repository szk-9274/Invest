# Implementation Plan: Backtest Visualization & Logging Improvements

## Overview

Enhance the backtest system with comprehensive trade logging and visual analysis to enable post-backtest verification of:

- Why trades occurred
- Which tickers performed best and worst

This work adds analysis capabilities without modifying the core trading logic.

---

## Problem Statement

Current issues identified:

1. **Universe size display bug**
   - Displayed Stage2 count does not match actual backtest universe after data filtering
2. **Missing trade log**
   - No persistent CSV log for ENTRY / EXIT actions and reasons
3. **No ticker-level analysis**
   - Cannot identify which tickers contribute most to profit or loss
4. **No visual verification**
   - Cannot visually confirm entry/exit decisions on charts

---

## Architecture Overview

### Backtest Flow

```
Stage2 Filter (screening_results.csv)
        ↓
Data Fetch Filter (>=252 bars required)
        ↓
Backtest Loop (daily evaluation)
        ↓
NEW: Trade Log CSV (ENTRY / EXIT)
        ↓
NEW: Ticker-level aggregation (Top 5 / Bottom 5)
        ↓
NEW: Candlestick charts with trade markers
```

---

## Task Breakdown

## Task 1: Fix Universe Size Display Bug
**Priority: CRITICAL**

### Problem
The displayed Stage2 universe size does not reflect the actual backtest universe after data-fetch filtering.

### Solution
Store and display:
- Stage2 input ticker count
- Actual universe after data fetch
- Number of filtered-out tickers

### Changes

**File:** `python/backtest/engine.py`

1. Before data fetch loop:
```python
self.diagnostics['stage2_universe_size'] = len(tickers)
```

2. Diagnostics output:
```python
logger.info(f"  Stage2 input tickers: {self.diagnostics['stage2_universe_size']}")
logger.info(f"  After data fetch:     {len(all_data)}")
logger.info(f"  Filtered out:         {self.diagnostics['stage2_universe_size'] - len(all_data)}")
```

### Expected Output
```
Stage2 input tickers: 47
After data fetch:     42
Filtered out:         5
```

---

## Task 2: Implement Trade Log CSV
**Priority: HIGH**

### Purpose
Persist all trade actions for later analysis.

### New File
`python/backtest/trade_logger.py`

### CSV Format
```
date,ticker,action,price,shares,reason,pnl,capital_after
```

### Logged Fields
- date (YYYY-MM-DD)
- ticker
- action (ENTRY / EXIT)
- price
- shares
- reason
- pnl (EXIT only)
- capital_after

### Integration Points

- Initialize logger in `BacktestEngine.__init__`
- Log ENTRY immediately after position creation
- Log EXIT immediately after position close
- Save CSV after backtest completes

### Exit Reasons (existing logic)
- stop_loss
- ma50_break
- target_reached
- end_of_backtest

---

## Task 3: Ticker-Level P&L Analysis
**Priority: MEDIUM**

### New File
`python/backtest/ticker_analysis.py`

### Purpose
Aggregate EXIT trades by ticker to compute:
- Total P&L
- Trade count

### Outputs
- `ticker_stats.csv`
- Console display:
  - Top 5 winners
  - Bottom 5 losers

### Data Source
- `trade_log.csv` (EXIT rows only)

---

## Task 4: Ticker Chart Visualization
**Priority: MEDIUM**

### Dependency
Add to `requirements.txt`:
```
mplfinance>=0.12.9
```

### New File
`python/backtest/ticker_charts.py`

### Chart Requirements

- Candlestick chart
- SMA20 / SMA50 overlays
- ENTRY markers (up arrow)
- EXIT markers (down arrow)
- 1-year backtest period
- One chart per ticker

### Scope
Generate charts for:
- Top 5 profitable tickers
- Bottom 5 losing tickers

### Output
```
python/output/charts/{TICKER}.png
```

---

## Testing Strategy

### Unit Tests
- TradeLogger entry logging
- TradeLogger exit logging
- CSV persistence
- Ticker P&L aggregation

### Integration Tests
- trade_log.csv generation
- ticker_stats.csv generation
- chart image generation

### Manual Verification
```bash
python main.py --mode backtest --start 2024-01-01 --end 2024-12-31
```

Verify:
- output/trade_log.csv
- output/ticker_stats.csv
- output/charts/*.png

---

## Risk Assessment

### Low Risk
- Universe size display fix
- Trade logger (non-invasive)

### Medium Risk
- Chart generation dependency
- Data alignment for markers

### Mitigation
- Make mplfinance optional
- Graceful failure with logging
- Validate CSV format before analysis

---

## Success Criteria

1. Accurate universe size reporting
2. Complete trade_log.csv with reasons
3. Correct ticker-level P&L aggregation
4. Charts generated for top/bottom performers
5. Clear visual entry/exit verification
6. All tests pass with sufficient coverage

---

## Out of Scope (Future Work)

- ATR-based stops
- Cooldown rules
- Interactive charts (Plotly)
- Strategy parameter optimization
