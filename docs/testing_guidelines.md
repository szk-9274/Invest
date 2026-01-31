# Testing Guidelines

## Overview

This document defines testing requirements and guidelines for the Invest project, with a focus on preventing runtime errors like KeyError in production code.

## Testing Philosophy

### Core Principle: Contract Testing

Every public interface (function, class, script) must have a **contract test** that verifies:
1. **Input/Output structure** - What data format is expected and returned
2. **Critical fields** - Required columns, keys, or attributes that downstream code depends on
3. **Error handling** - Graceful degradation on failure

### Why Contract Tests?

**Problem**: A script produces output that looks correct during development, but breaks in production when a required field is missing.

**Solution**: Contract tests explicitly verify the data structure contract:
```python
# BAD: No verification
result = fetch_data()
df = pd.DataFrame(result)  # Might fail if 'ticker' column missing

# GOOD: Contract test ensures required columns exist
assert all(col in df.columns for col in ['ticker', 'exchange', 'sector'])
```

## Test Requirements by Code Type

### 1. Scripts (scripts/ directory)

**MANDATORY: Smoke Tests**

Every script in `scripts/` directory must have a corresponding smoke test in `tests/test_<script_name>_smoke.py`.

**Minimum requirements:**
- [ ] Script can be imported without errors
- [ ] Main execution path runs without exceptions (with mocked network calls)
- [ ] Output data structure matches contract (required columns/fields exist)
- [ ] CSV output (if applicable) has required columns

**Example:**
```python
# tests/test_update_tickers_smoke.py
def test_ticker_fetcher_output_has_required_columns():
    """Prevent KeyError on CSV output"""
    fetcher = TickerFetcher(...)
    result = fetcher.filter_tickers(sample_data)

    # CONTRACT: Must have these columns for CSV output
    required_columns = ['ticker', 'exchange', 'sector']
    for ticker_dict in result:
        assert all(col in ticker_dict for col in required_columns)
```

**When to update script tests:**
- [ ] Adding new script to `scripts/` → Create new smoke test
- [ ] Modifying script output structure → Update contract test
- [ ] Adding new required column → Add to contract test

### 2. Analysis Modules (analysis/ directory)

**RECOMMENDED: Unit Tests**

For critical analysis logic (Stage detection, VCP, indicators):
- [ ] Test core logic with known inputs/outputs
- [ ] Test edge cases (empty data, NaN values, insufficient data)
- [ ] Test error handling (missing columns, invalid data types)

**Example:**
```python
def test_stage_detector_insufficient_data():
    """Verify graceful handling of insufficient data"""
    detector = StageDetector(config)
    short_data = pd.DataFrame({'close': [100, 101, 102]})  # Only 3 bars

    result = detector.detect_stage(short_data)
    assert result['stage'] == 1  # Fallback to Stage 1
    assert not result['meets_criteria']
```

### 3. Backtest Engine (backtest/ directory)

**RECOMMENDED: Integration Tests**

For backtest logic:
- [ ] Test with synthetic data (deterministic results)
- [ ] Verify entry/exit logic
- [ ] Test edge cases (no trades, all stop losses, etc.)

## Running Tests

### Run all tests
```bash
cd python
pytest
```

### Run specific test file
```bash
pytest tests/test_ticker_fetcher_smoke.py -v
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run only smoke tests
```bash
pytest -m smoke
```

## Test Organization

```
python/
├── tests/
│   ├── __init__.py
│   ├── test_ticker_fetcher_smoke.py    # Scripts smoke tests
│   ├── test_stage_detector.py           # Analysis unit tests
│   └── test_backtest_engine.py          # Backtest integration tests
├── scripts/
│   └── update_tickers_extended.py       # Must have smoke test
├── analysis/
│   └── stage_detector.py                # Should have unit tests
└── backtest/
    └── engine.py                         # Should have integration tests
```

## Writing Good Tests

### DO: Test Contracts
```python
def test_required_output_columns():
    """Verify required columns exist in output"""
    result = function_under_test()
    assert 'ticker' in result.columns
    assert 'exchange' in result.columns
```

### DON'T: Test Implementation Details
```python
def test_internal_variable_name():
    """Bad: Testing internal implementation"""
    result = function_under_test()
    assert result._internal_cache is not None  # Don't do this
```

### DO: Mock External Dependencies
```python
@patch('scripts.update_tickers.pd.read_html')
def test_with_mocked_network(mock_read_html):
    """Mock network calls for fast, reliable tests"""
    mock_read_html.return_value = [sample_dataframe]
    result = fetch_sp500_tickers()
    assert len(result) > 0
```

### DON'T: Make Real Network Calls
```python
def test_with_real_network():
    """Bad: Slow, flaky, depends on external service"""
    result = fetch_sp500_tickers()  # Makes real HTTP request
    assert len(result) > 0
```

## Pre-Commit Checklist

Before committing changes to `scripts/`:

- [ ] Smoke test exists for the script
- [ ] `pytest tests/test_<script>_smoke.py` passes
- [ ] Contract test verifies output structure
- [ ] No real network calls in tests (all mocked)
- [ ] Test runs in < 5 seconds

## Historical Context

### KeyError Issue (2026-01-31)

**Problem**: `update_tickers_extended.py` produced a DataFrame missing required columns (`ticker`, `exchange`, `sector`), causing `KeyError` on CSV output.

**Root Cause**: No test verified the output contract.

**Solution**: Added `test_ticker_fetcher_smoke.py` with contract tests:
```python
def test_filter_tickers_returns_required_columns():
    """CRITICAL: Prevent KeyError on CSV output"""
    result = fetcher.filter_tickers(sample_data)
    required_columns = ['ticker', 'exchange', 'sector']
    for ticker_dict in result:
        assert all(col in ticker_dict for col in required_columns)
```

**Lesson**: Always verify data structure contracts with tests.

## Test Coverage Goals

- **Scripts**: 100% smoke test coverage (contract verification)
- **Analysis**: 80%+ code coverage (logic verification)
- **Backtest**: 70%+ code coverage (integration verification)

## Questions?

If unsure whether to add a test:
1. Will failure cause runtime errors? → **YES: Add test**
2. Does downstream code depend on this structure? → **YES: Add contract test**
3. Is this a public interface? → **YES: Add test**
4. Is this internal implementation? → Maybe skip

**When in doubt, add a smoke test. It's cheap and prevents production issues.**
