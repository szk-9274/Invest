# Stage2 Filtering Tuning Guide

## Overview

This guide explains how to configure and tune Stage2 (Trend Template) filtering thresholds to balance trade quality vs. trade quantity in your backtest.

## Problem: Zero Trades

If your backtest produces **0 trades**, it means **all 9 Stage2 conditions** failed to pass simultaneously for any ticker. The most common failure points are:

1. **`near_52w_high`** - Stock must be within 25% of its 52-week high (strict)
2. **`rs_new_high`** - Relative Strength line must be ≥95% of its 52-week high (strict)
3. **`sufficient_volume`** - Stock must meet minimum average volume requirement

## Solution: Strict vs. Relaxed Modes

The system now supports two filtering modes:

### Strict Mode (Default)
- **Purpose**: High-quality setups, fewer but better trades
- **Use when**: Bull market, plenty of Stage2 candidates
- **Thresholds**: Tighter (harder to pass)

### Relaxed Mode (Fallback)
- **Purpose**: Increase trade opportunities in harsh markets
- **Use when**: Bear/sideways market, strict mode produces 0 trades
- **Thresholds**: Looser (easier to pass)

## Configuration

All thresholds are in `python/config/params.yaml`:

```yaml
stage:
  sma_periods: [50, 150, 200]

  # STRICT MODE (default)
  strict:
    min_price_above_52w_low: 1.30      # Must be 30% above 52w low
    max_distance_from_52w_high: 0.75   # Must be within 25% of 52w high
    rs_new_high_threshold: 0.95        # RS must be ≥95% of 52w high
    min_volume: 500000                 # Min 500k average volume

  # RELAXED MODE (fallback)
  relaxed:
    min_price_above_52w_low: 1.20      # 20% above 52w low (easier)
    max_distance_from_52w_high: 0.60   # Within 40% of 52w high (easier)
    rs_new_high_threshold: 0.90        # RS ≥90% of 52w high (easier)
    min_volume: 300000                 # Min 300k volume (easier)

  # Automatic fallback behavior
  auto_fallback_enabled: true          # Enable automatic fallback
  min_trades_threshold: 1              # Fallback if < 1 trade
```

## Tuning Thresholds

### Which Conditions to Relax?

✅ **Safe to relax** (price/volume filters):
- `min_price_above_52w_low` - Price position relative to 52w range
- `max_distance_from_52w_high` - Proximity to 52w high
- `rs_new_high_threshold` - RS line strength
- `min_volume` - Average daily volume

❌ **DO NOT relax** (core trend structure):
- MA alignment (`price_above_sma50`, `sma50_above_sma150`, `sma150_above_sma200`)
- MA200 uptrend (`ma200_uptrend`)
- MA50 position (`ma50_above_ma150_200`)

### Recommended Adjustments

**If strict mode is too restrictive:**

```yaml
strict:
  max_distance_from_52w_high: 0.70  # Lower from 0.75 → 0.70 (within 30%)
  rs_new_high_threshold: 0.93       # Lower from 0.95 → 0.93
  min_volume: 400000                # Lower from 500k → 400k
```

**If relaxed mode is too loose:**

```yaml
relaxed:
  max_distance_from_52w_high: 0.65  # Raise from 0.60 → 0.65 (tighter)
  rs_new_high_threshold: 0.92       # Raise from 0.90 → 0.92
  min_volume: 350000                # Raise from 300k → 350k
```

## Automatic Fallback

### How It Works

1. **First Pass (Strict)**: Backtest runs with strict thresholds
2. **Check Results**: If `total_trades < min_trades_threshold`
3. **Fallback**: Switch to relaxed mode automatically
4. **Second Pass (Relaxed)**: Re-run backtest with relaxed thresholds

### Configuration

```yaml
stage:
  auto_fallback_enabled: true   # Set to false to disable
  min_trades_threshold: 1       # Trigger fallback if < 1 trade
```

**To disable automatic fallback:**

```yaml
stage:
  auto_fallback_enabled: false
```

**To require more trades before fallback:**

```yaml
stage:
  min_trades_threshold: 5  # Only fallback if < 5 trades
```

## Manual Mode Selection

To force a specific mode (disable automatic fallback):

```yaml
stage:
  auto_fallback_enabled: false
```

Then adjust thresholds directly:

- **For aggressive filtering**: Use strict values
- **For lenient filtering**: Use relaxed values

## Testing Your Configuration

### 1. Run Backtest

```bash
python main.py --mode backtest --start 2023-01-01 --end 2024-01-01
```

### 2. Check Diagnostics

Look for:
```
BACKTEST CONFIGURATION
=========================
Filtering mode:   STRICT
Auto fallback:    Enabled

BACKTEST DIAGNOSTICS
=========================
Total trades executed:       12
Stage 2 checks performed:    8,450
Stage 2 passed:             156
```

### 3. Analyze Failure Reasons

```
Top Stage 2 failure reasons:
  near_52w_high            4,234 failures  ← Most common
  rs_new_high              2,891 failures  ← Second most common
  above_52w_low            1,125 failures
```

### 4. Adjust Thresholds

If `near_52w_high` fails frequently, consider:
- Lowering `max_distance_from_52w_high` in strict mode
- OR letting automatic fallback handle it

## Common Scenarios

### Scenario 1: Bull Market (Many Candidates)

**Problem**: Too many trades, want higher quality

**Solution**: Tighten strict mode

```yaml
strict:
  max_distance_from_52w_high: 0.80  # Raise to 0.80 (tighter)
  rs_new_high_threshold: 0.97       # Raise to 0.97 (stronger RS)
  min_volume: 600000                # Raise to 600k
```

### Scenario 2: Bear Market (Zero Trades)

**Problem**: No stocks pass strict mode

**Solution**: Enable auto-fallback (already enabled by default)

```yaml
stage:
  auto_fallback_enabled: true
  min_trades_threshold: 1
```

### Scenario 3: Sideways Market (Few Trades)

**Problem**: 1-2 trades only, want more opportunities

**Solution**: Loosen relaxed mode or tighten fallback threshold

```yaml
relaxed:
  max_distance_from_52w_high: 0.55  # Lower to 0.55 (looser)
  rs_new_high_threshold: 0.88       # Lower to 0.88

auto_fallback_enabled: true
min_trades_threshold: 3  # Fallback if < 3 trades
```

### Scenario 4: Small Cap Focus

**Problem**: Missing small caps due to volume filter

**Solution**: Lower volume thresholds

```yaml
strict:
  min_volume: 300000  # Lower from 500k

relaxed:
  min_volume: 200000  # Lower from 300k
```

## Performance Trade-offs

| Configuration | Trade Quality | Trade Quantity | Best For |
|--------------|---------------|----------------|----------|
| Tight strict | ★★★★★ | ★☆☆☆☆ | Bull markets |
| Default strict | ★★★★☆ | ★★☆☆☆ | Normal conditions |
| Loose strict | ★★★☆☆ | ★★★☆☆ | Balanced approach |
| Default relaxed | ★★☆☆☆ | ★★★★☆ | Bear/sideways |
| Loose relaxed | ★☆☆☆☆ | ★★★★★ | Extreme conditions |

## Validation Workflow

1. **Backtest** with your configuration
2. **Check trades** - Are there enough opportunities?
3. **Analyze failures** - Which conditions fail most?
4. **Adjust thresholds** - Tune the problematic conditions
5. **Re-test** - Verify improvement
6. **Iterate** - Repeat until satisfied

## Advanced Tips

### Per-Condition Analysis

Use diagnostics to identify which single condition causes the most failures:

```python
# In backtest output
Top Stage 2 failure reasons:
  near_52w_high            4,234 failures  ← Focus here first
  rs_new_high              2,891 failures
  above_52w_low            1,125 failures
  sufficient_volume          892 failures
```

### Historical Sensitivity Analysis

Test multiple threshold combinations across different market periods:

```bash
# Bull market period
python main.py --mode backtest --start 2023-01-01 --end 2024-01-01

# Bear market period
python main.py --mode backtest --start 2022-01-01 --end 2022-12-31
```

### Custom Threshold Sets

Create multiple configurations for different strategies:

```yaml
# Conservative (high quality)
strict:
  max_distance_from_52w_high: 0.85
  rs_new_high_threshold: 0.97

# Aggressive (high quantity)
relaxed:
  max_distance_from_52w_high: 0.50
  rs_new_high_threshold: 0.85
```

## Troubleshooting

### Still Getting Zero Trades in Relaxed Mode

1. Check ticker list - Are you using recent, active stocks?
2. Check date range - Is it during extreme market conditions?
3. Check benchmark - Is SPY data available?
4. Lower relaxed thresholds further
5. Consider disabling RS condition (set `rs_new_high_required: false`)

### Too Many Low-Quality Trades

1. Tighten strict mode thresholds
2. Raise relaxed mode thresholds
3. Disable auto-fallback and use strict only
4. Add additional filters (fundamentals, sector, etc.)

### Fallback Not Triggering

1. Verify `auto_fallback_enabled: true`
2. Check `min_trades_threshold` - is it too low?
3. Look for "FALLBACK" messages in logs

## References

- **Minervini's Stage Theory**: Focus on proper MA alignment (never relax)
- **Relative Strength**: Higher RS = better performance (adjust threshold carefully)
- **52-Week High Proximity**: Stocks near highs tend to continue (balance quality vs. quantity)

## Support

For issues or questions:
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Check diagnostics output for detailed failure analysis
- Review backtest logs for fallback trigger messages
