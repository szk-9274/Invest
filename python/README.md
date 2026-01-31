# Stock Screening System

Python-based stock screening system based on Minervini's Stage Theory.

## Setup (Windows)

### 1. Create Virtual Environment

```bash
cd python
python -m venv .venv
```

### 2. Activate Virtual Environment

```bash
# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Git Bash / WSL
source .venv/Scripts/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Development Dependencies (Optional)

```bash
pip install -r requirements-dev.txt
```

## Usage

### Update Ticker List

Fetch and filter approximately 3,500 tickers from S&P 500, NASDAQ, and Russell 3000:

```bash
python -m scripts.update_tickers_extended
```

Options:
- `--min-market-cap`: Minimum market cap in USD (default: 2B)
- `--min-price`: Minimum stock price (default: $5)
- `--min-volume`: Minimum average daily volume (default: 500K)
- `--max-tickers`: Maximum number of tickers (default: 3500)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Run Stock Screening

#### Stage 2 Screening

```bash
python main.py --mode stage2
```

#### Full Screening (Stage 2 only, VCP disabled)

```bash
python main.py --mode full
```

#### Quick Test (5 tickers)

```bash
python main.py --mode test
```

#### Custom Ticker List

```bash
python main.py --mode stage2 --tickers AAPL,MSFT,NVDA
```

#### Disable Benchmark (RS condition)

```bash
python main.py --mode stage2 --no-benchmark
```

### Run Backtest

```bash
python main.py --mode backtest --start 2020-01-01 --end 2024-12-31
```

Options:
- `--start`: Backtest start date (YYYY-MM-DD)
- `--end`: Backtest end date (YYYY-MM-DD)
- `--no-benchmark`: Disable SPY benchmark for RS calculation

### Debug Stage 2 Filtering

Check why a specific ticker is not passing Stage 2 conditions:

```bash
python debug_stage2.py --ticker AAPL
python debug_stage2.py --ticker AAPL --date 2024-01-15
python debug_stage2.py --ticker AAPL --no-benchmark
```

## Project Structure

```
python/
├── main.py                      # Main entry point
├── debug_stage2.py              # Stage 2 debugging tool
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── config/
│   ├── params.yaml              # Configuration parameters
│   └── tickers.csv              # Ticker list
├── scripts/
│   └── update_tickers_extended.py  # Ticker fetcher
├── data/
│   └── fetcher.py               # Data fetching utilities
├── analysis/
│   ├── indicators.py            # Technical indicators
│   ├── stage_detector.py        # Stage 2 detection
│   ├── fundamentals.py          # Fundamental analysis
│   └── vcp_detector.py          # VCP pattern detection
├── screening/
│   └── screener.py              # Main screening logic
├── backtest/
│   ├── engine.py                # Backtest engine
│   ├── performance.py           # Performance metrics
│   └── visualization.py         # Chart generation
├── utils/
│   └── logger.py                # Logging utilities
├── cache/                       # Cached data (gitignored)
└── output/                      # Results (gitignored)
    ├── screening_results.csv
    └── backtest/
```

## Configuration

Edit `config/params.yaml` to customize:
- Stage 2 detection thresholds
- Risk management parameters
- Backtest settings
- Output paths

## Testing

```bash
pytest
pytest --cov=. --cov-report=html
```

## Development

### Code Style
- Immutability: Always create new objects, never mutate
- Small files: 200-400 lines typical, 800 max
- Type hints: Use TypeScript-style type annotations
- Error handling: Comprehensive try/catch blocks

### Testing
- Follow TDD workflow (write tests first)
- Maintain 80%+ test coverage
- Run tests before commits

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:
1. Virtual environment is activated
2. You're running from the `python/` directory
3. All dependencies are installed

### Data Fetching Issues

- Wikipedia S&P 500 fetch failures: Check network/SSL
- yfinance rate limiting: Adjust `request_delay` in update script
- Low ticker count: Review filter thresholds (market cap, price, volume)
