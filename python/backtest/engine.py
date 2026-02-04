"""
Backtesting Engine Module

Architecture:
- Stage2 = Universe Selection (tickers loaded from screening_results.csv)
- EntryCondition = Daily trade decision (lightweight, no rs_new_high)

Stage2 conditions (including rs_new_high) are evaluated ONCE at the start
when loading the universe. They are NOT re-evaluated daily.

EntryCondition is evaluated daily for entry decisions and includes only:
- price > sma50
- sma50 > sma150
- sufficient volume

This separation ensures:
1. Backtest generates trades (not 0)
2. Stage2 universe and Entry pass rates are independently observable
3. rs_new_high is NOT evaluated as daily entry condition
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger
from tqdm import tqdm

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetcher import YahooFinanceFetcher
from analysis.indicators import calculate_all_indicators
from analysis.stage_detector import StageDetector
from analysis.vcp_detector import VCPDetector
from backtest.fallback_manager import FallbackManager
from backtest.entry_condition import EntryCondition
from backtest.trade_logger import TradeLogger
from backtest.ticker_analysis import TickerAnalysis


@dataclass
class Position:
    """Represents a trading position"""
    ticker: str
    entry_date: datetime
    entry_price: float
    shares: int
    stop_price: float
    target_price: float
    pivot: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    pnl: float = 0.0
    pnl_pct: float = 0.0


@dataclass
class BacktestResult:
    """Backtest results summary"""
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    benchmark_enabled: bool = True
    trades: List[Position] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=pd.Series)


class BacktestEngine:
    """Backtesting engine for the screening strategy"""

    def __init__(self, config: Dict, use_benchmark: bool = True):
        """
        Initialize the backtest engine.

        Args:
            config: Configuration dictionary
            use_benchmark: Whether to use SPY benchmark for RS calculation
        """
        self.config = config
        self.use_benchmark = use_benchmark
        self.fetcher = YahooFinanceFetcher(
            request_delay=config['performance']['request_delay']
        )
        self.stage_detector = StageDetector(config['stage'])
        self.vcp_detector = VCPDetector(config['vcp'])

        # Initialize FallbackManager
        stage_config = config['stage']
        self.fallback_manager = FallbackManager(
            auto_fallback_enabled=stage_config.get('auto_fallback_enabled', True),
            min_trades_threshold=stage_config.get('min_trades_threshold', 1)
        )

        # Initialize EntryCondition for daily entry checks
        # NOTE: EntryCondition does NOT include rs_new_high
        # Stage2 (with rs_new_high) is only used for universe selection
        self.entry_condition = EntryCondition(
            config=config,
            mode=self.fallback_manager.get_current_mode()
        )

        # Backtest parameters
        self.initial_capital = config['backtest']['initial_capital']
        self.max_positions = config['backtest']['max_positions']
        self.commission = config['backtest']['commission']
        self.risk_per_trade = config['risk']['risk_per_trade']

        # Initialize TradeLogger for trade action logging (Task 2)
        output_config = config.get('output', {})
        output_dir = output_config.get('csv_path', 'python/output')
        # If csv_path points to a file, use its parent directory
        if output_dir.endswith('.csv'):
            output_dir = str(Path(output_dir).parent)
        self.trade_logger = TradeLogger(output_dir=output_dir)

        # Diagnostics with separate Stage2 and Entry tracking
        self.diagnostics = {
            # Stage2 is for universe selection (one-time at start)
            'stage2_universe_size': 0,

            # Entry evaluation is for daily trade decisions
            'entry_evaluations': 0,
            'entry_passed': 0,
            'entry_failed_conditions': {},

            # Legacy keys for backward compatibility
            'stage2_checks': 0,
            'stage2_passed': 0,
            'stage2_failed_conditions': {},

            # Other diagnostics
            'insufficient_capital': 0,
            'max_positions_reached': 0,
            'insufficient_data': 0,
            'total_entry_attempts': 0,
            'fallback_triggered': False,
            'strict_mode_trades': 0,
            'relaxed_mode_trades': 0,

            # Data fetch diagnostics (Task 1: Universe Size Display Bug Fix)
            'data_fetch_success_count': 0,
            'data_fetch_filtered_count': 0
        }

    def run(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str
    ) -> BacktestResult:
        """
        Run backtest.

        Args:
            tickers: List of ticker symbols
            start_date: Backtest start date (YYYY-MM-DD)
            end_date: Backtest end date (YYYY-MM-DD)

        Returns:
            BacktestResult object
        """
        logger.info("=" * 60)
        logger.info("BACKTEST CONFIGURATION")
        logger.info("=" * 60)
        logger.info(f"Period:           {start_date} to {end_date}")
        logger.info(f"Tickers:          {len(tickers)}")
        logger.info(f"Initial capital:  ${self.initial_capital:,.2f}")
        logger.info(f"Max positions:    {self.max_positions}")
        logger.info(f"Risk per trade:   {self.risk_per_trade:.1%}")
        logger.info(f"Commission:       {self.commission:.2%}")
        logger.info(f"Benchmark:        {'Enabled (SPY)' if self.use_benchmark else 'Disabled'}")
        logger.info(f"Filtering mode:   {self.fallback_manager.get_current_mode().upper()}")
        logger.info(f"Auto fallback:    {'Enabled' if self.fallback_manager.auto_fallback_enabled else 'Disabled'}")
        logger.info("=" * 60)

        # Fetch benchmark data (with fallback)
        benchmark_data = None
        use_benchmark = self.use_benchmark

        if use_benchmark:
            benchmark_data = self.fetcher.fetch_benchmark('SPY', period='5y')
            if benchmark_data is None:
                logger.warning(
                    "Failed to fetch benchmark data (SPY). "
                    "Falling back to no-benchmark mode for backtest."
                )
                use_benchmark = False
            else:
                # Normalize timezone to tz-naive for consistent comparison
                if benchmark_data.index.tz is not None:
                    benchmark_data.index = benchmark_data.index.tz_localize(None)

                # Filter benchmark data to backtest period
                start = pd.Timestamp(start_date)
                end = pd.Timestamp(end_date)
                benchmark_data = benchmark_data[
                    (benchmark_data.index >= start) & (benchmark_data.index <= end)
                ]
        else:
            logger.info("Benchmark disabled by user (--no-benchmark)")

        if not use_benchmark:
            logger.info("Backtest: Running in NO-BENCHMARK mode (RS condition auto-passed)")

        # Fetch all ticker data
        logger.info("\n" + "=" * 60)
        logger.info("DATA FETCHING")
        logger.info("=" * 60)

        # Task 1: Record Stage2 input ticker count BEFORE data fetch
        self.diagnostics['stage2_universe_size'] = len(tickers)
        logger.info(f"Stage2 input tickers: {self.diagnostics['stage2_universe_size']}")
        logger.info("Fetching historical data...")

        all_data = {}
        for ticker in tqdm(tickers, desc="Loading ticker data", unit="ticker"):
            data = self.fetcher.fetch_data(ticker, period='5y')
            if data is not None and len(data) > 252:
                # Normalize timezone to tz-naive for consistent comparison
                if data.index.tz is not None:
                    data.index = data.index.tz_localize(None)

                # Calculate indicators (benchmark may be None)
                data = calculate_all_indicators(data, benchmark_data)
                all_data[ticker] = data

        # Task 1: Record data fetch results
        self.diagnostics['data_fetch_success_count'] = len(all_data)
        self.diagnostics['data_fetch_filtered_count'] = len(tickers) - len(all_data)

        logger.info(f"After data fetch:     {self.diagnostics['data_fetch_success_count']}")
        logger.info(f"Filtered out:         {self.diagnostics['data_fetch_filtered_count']}")

        # CRITICAL VALIDATION: Check if we have data to backtest
        if len(all_data) == 0:
            logger.error("=" * 60)
            logger.error("CRITICAL ERROR: NO DATA FETCHED")
            logger.error("=" * 60)
            logger.error("Backtest cannot proceed - no ticker data available")
            logger.error("Possible reasons:")
            logger.error("  1. All tickers failed to fetch from Yahoo Finance")
            logger.error("  2. Network/API issues")
            logger.error("  3. Invalid ticker symbols")
            return self._empty_result(use_benchmark)

        # Determine trading days from data
        if benchmark_data is not None and not benchmark_data.empty:
            start = pd.Timestamp(start_date)
            end = pd.Timestamp(end_date)
            trading_days = benchmark_data.index
        else:
            # Without benchmark, derive trading days from available data
            start = pd.Timestamp(start_date)
            end = pd.Timestamp(end_date)
            all_dates = set()
            for data in all_data.values():
                all_dates.update(data.index)
            trading_days = pd.DatetimeIndex(sorted(all_dates))
            trading_days = trading_days[(trading_days >= start) & (trading_days <= end)]

        if len(trading_days) == 0:
            logger.warning("No trading days found in the specified period")
            return self._empty_result(use_benchmark)

        # Initialize portfolio
        capital = self.initial_capital
        positions: List[Position] = []
        closed_positions: List[Position] = []
        equity_curve = []

        logger.info(f"\nRunning backtest simulation ({len(trading_days)} trading days)...")

        # Main backtest loop with progress bar
        pbar = tqdm(
            enumerate(trading_days),
            total=len(trading_days),
            desc="Backtest progress",
            unit="day"
        )

        for i, date in pbar:
            # NOTE: The historical data requirement (252 bars) is checked per-ticker
            # at line 291 (len(hist_data) < 252), NOT by loop iteration index.
            # The old `if i < 252: continue` was incorrect because:
            # - trading_days is filtered to backtest period (may be < 252 days)
            # - Each ticker has its own full historical data (fetched with period='5y')
            # - We check if ticker has sufficient history before the simulation date

            # Update progress bar with current status
            current_equity = capital
            for pos in positions:
                if pos.ticker in all_data and date in all_data[pos.ticker].index:
                    current_price = all_data[pos.ticker].loc[date, 'close']
                    current_equity += pos.shares * current_price

            pbar.set_postfix({
                'date': date.strftime('%Y-%m-%d'),
                'positions': len(positions),
                'equity': f'${current_equity:,.0f}',
                'trades': len(closed_positions)
            })

            # Check exit conditions for existing positions
            for pos in positions[:]:
                if pos.ticker in all_data:
                    ticker_data = all_data[pos.ticker]
                    if date in ticker_data.index:
                        current_bar = ticker_data.loc[date]
                        exit_signal, exit_reason = self._check_exit(pos, current_bar)

                        if exit_signal:
                            pos.exit_date = date
                            pos.exit_price = current_bar['close']
                            pos.exit_reason = exit_reason
                            pos.pnl = (pos.exit_price - pos.entry_price) * pos.shares
                            pos.pnl -= (pos.entry_price + pos.exit_price) * pos.shares * self.commission
                            pos.pnl_pct = (pos.exit_price - pos.entry_price) / pos.entry_price

                            capital += pos.shares * pos.exit_price * (1 - self.commission)
                            positions.remove(pos)
                            closed_positions.append(pos)

                            logger.info(
                                f"EXIT: {pos.ticker} @ ${pos.exit_price:.2f} "
                                f"({pos.exit_reason}) | P&L: ${pos.pnl:+.2f} ({pos.pnl_pct:+.1%})"
                            )

                            # Task 2: Log EXIT action
                            self.trade_logger.log_exit(
                                date=date,
                                ticker=pos.ticker,
                                price=pos.exit_price,
                                shares=pos.shares,
                                reason=pos.exit_reason,
                                pnl=pos.pnl,
                                capital_after=capital
                            )

            # Check entry conditions for new positions
            if len(positions) < self.max_positions:
                for ticker, data in all_data.items():
                    # Skip if already have position in this ticker
                    if any(p.ticker == ticker for p in positions):
                        continue

                    if date not in data.index:
                        continue

                    # Get data up to current date
                    hist_data = data[data.index <= date].tail(300)
                    if len(hist_data) < 252:
                        self.diagnostics['insufficient_data'] += 1
                        continue

                    # ============================================================
                    # ARCHITECTURAL CHANGE: Use EntryCondition instead of Stage2
                    # ============================================================
                    # Stage2 is for UNIVERSE SELECTION (one-time at backtest start)
                    # EntryCondition is for DAILY ENTRY DECISIONS (no rs_new_high)
                    #
                    # The tickers here have already passed Stage2 (loaded from
                    # screening_results.csv by main.py). We only need to check
                    # lightweight entry conditions for daily trade decisions.
                    # ============================================================

                    self.diagnostics['entry_evaluations'] += 1
                    # Legacy key for backward compatibility
                    self.diagnostics['stage2_checks'] += 1

                    # Use EntryCondition for daily checks (excludes rs_new_high)
                    entry_result = self.entry_condition.evaluate(hist_data)

                    if not entry_result['passed']:
                        # Track which entry conditions failed
                        for condition, passed in entry_result['conditions'].items():
                            if not passed:
                                self.diagnostics['entry_failed_conditions'][condition] = \
                                    self.diagnostics['entry_failed_conditions'].get(condition, 0) + 1
                        continue

                    self.diagnostics['entry_passed'] += 1
                    # Legacy key for backward compatibility
                    self.diagnostics['stage2_passed'] += 1
                    self.diagnostics['total_entry_attempts'] += 1

                    # ===== VCP DETECTION DISABLED - USING SIMPLIFIED LOGIC =====
                    # # Check VCP
                    # vcp_result = self.vcp_detector.detect_vcp(hist_data)
                    # if vcp_result is None:
                    #     continue
                    #
                    # # Check breakout
                    # current_bar = data.loc[date]
                    # if current_bar['close'] < vcp_result['pivot']:
                    #     continue
                    #
                    # # Check volume
                    # vol_ratio = current_bar['volume'] / current_bar['volume_ma_50']
                    # if vol_ratio < self.config['entry']['breakout_vol_ratio']:
                    #     continue
                    #
                    # # Calculate position size
                    # entry_price = current_bar['close']
                    # stop_price = vcp_result['stop_price']
                    # risk = entry_price - stop_price
                    #
                    # if risk <= 0:
                    #     continue
                    #
                    # risk_amount = capital * self.risk_per_trade
                    # shares = int(risk_amount / risk)
                    #
                    # if shares <= 0:
                    #     continue
                    #
                    # cost = shares * entry_price * (1 + self.commission)
                    # if cost > capital:
                    #     continue
                    #
                    # # Open position
                    # pos = Position(
                    #     ticker=ticker,
                    #     entry_date=date,
                    #     entry_price=entry_price,
                    #     shares=shares,
                    #     stop_price=stop_price,
                    #     target_price=entry_price * 1.25,
                    #     pivot=vcp_result['pivot']
                    # )
                    # positions.append(pos)
                    # capital -= cost
                    #
                    # logger.debug(
                    #     f"{date.date()}: ENTRY {ticker} @ ${entry_price:.2f}, "
                    #     f"{shares} shares, Stop: ${stop_price:.2f}"
                    # )

                    # Simplified entry logic (Stage 2 with basic risk management)
                    current_bar = data.loc[date]
                    entry_price = current_bar['close']

                    # Simple 3% stop loss
                    stop_price = entry_price * 0.97

                    # Calculate position size
                    risk = entry_price - stop_price
                    if risk <= 0:
                        continue

                    risk_amount = capital * self.risk_per_trade
                    shares = int(risk_amount / risk)

                    if shares <= 0:
                        continue

                    cost = shares * entry_price * (1 + self.commission)
                    if cost > capital:
                        self.diagnostics['insufficient_capital'] += 1
                        continue

                    # Open position
                    pos = Position(
                        ticker=ticker,
                        entry_date=date,
                        entry_price=entry_price,
                        shares=shares,
                        stop_price=stop_price,
                        target_price=entry_price * 1.25,
                        pivot=entry_price  # Simplified: use current price as pivot
                    )
                    positions.append(pos)
                    capital -= cost

                    logger.info(
                        f"ENTRY: {ticker} @ ${entry_price:.2f} | "
                        f"{shares} shares | Stop: ${stop_price:.2f}"
                    )

                    # Task 2: Log ENTRY action
                    self.trade_logger.log_entry(
                        date=date,
                        ticker=ticker,
                        price=entry_price,
                        shares=shares,
                        reason='entry_signal',
                        capital_after=capital
                    )

                    if len(positions) >= self.max_positions:
                        break
            else:
                # Count how often we couldn't enter due to max positions
                if any(True for ticker, data in all_data.items()
                       if date in data.index and len(data[data.index <= date]) >= 252):
                    self.diagnostics['max_positions_reached'] += 1

            # Calculate current equity
            current_equity = capital
            for pos in positions:
                if pos.ticker in all_data and date in all_data[pos.ticker].index:
                    current_price = all_data[pos.ticker].loc[date, 'close']
                    current_equity += pos.shares * current_price

            equity_curve.append({'date': date, 'equity': current_equity})

        # Close remaining positions at end
        for pos in positions:
            if pos.ticker in all_data:
                last_date = trading_days[-1]
                if last_date in all_data[pos.ticker].index:
                    pos.exit_date = last_date
                    pos.exit_price = all_data[pos.ticker].loc[last_date, 'close']
                    pos.exit_reason = 'end_of_backtest'
                    pos.pnl = (pos.exit_price - pos.entry_price) * pos.shares
                    pos.pnl -= (pos.entry_price + pos.exit_price) * pos.shares * self.commission
                    pos.pnl_pct = (pos.exit_price - pos.entry_price) / pos.entry_price

                    # Update capital for final exit
                    capital += pos.shares * pos.exit_price * (1 - self.commission)
                    closed_positions.append(pos)

                    # Task 2: Log EXIT action for end_of_backtest
                    self.trade_logger.log_exit(
                        date=last_date,
                        ticker=pos.ticker,
                        price=pos.exit_price,
                        shares=pos.shares,
                        reason=pos.exit_reason,
                        pnl=pos.pnl,
                        capital_after=capital
                    )

        # Save trade log to CSV (Task 2)
        if self.trade_logger.entries:
            trade_log_path = self.trade_logger.save()
            logger.info(f"Trade log saved to: {trade_log_path}")

            # Run ticker-level P&L analysis (Task 3)
            ticker_analyzer = TickerAnalysis(output_dir=self.trade_logger.output_dir)
            ticker_analyzer.analyze(self.trade_logger.entries)
            ticker_stats_path = ticker_analyzer.save()
            logger.info(f"Ticker stats saved to: {ticker_stats_path}")
            ticker_analyzer.print_summary()

        # Print diagnostics
        self._print_diagnostics(len(closed_positions))

        # Calculate results
        return self._calculate_results(closed_positions, equity_curve, use_benchmark)

    def _print_diagnostics(self, total_trades: int):
        """Print diagnostic information about backtest execution."""
        logger.info("")
        logger.info("=" * 60)
        logger.info("BACKTEST DIAGNOSTICS")
        logger.info("=" * 60)
        logger.info(f"Total trades executed:       {total_trades}")
        logger.info("")

        # Stage2 Universe (one-time selection) with data fetch details
        logger.info("Stage2 Universe:")
        logger.info(f"  Stage2 input tickers:      {self.diagnostics.get('stage2_universe_size', 'N/A')}")
        logger.info(f"  After data fetch:          {self.diagnostics.get('data_fetch_success_count', 'N/A')}")
        logger.info(f"  Filtered out:              {self.diagnostics.get('data_fetch_filtered_count', 'N/A')}")
        logger.info("  Note: Stage2 tickers loaded from screening_results.csv")
        logger.info("")

        # Entry Evaluation (daily checks, excludes rs_new_high)
        logger.info("Entry Evaluation (daily checks, excludes rs_new_high):")
        logger.info(f"  Entry evaluations:         {self.diagnostics['entry_evaluations']:,}")
        logger.info(f"  Entry passed:              {self.diagnostics['entry_passed']:,}")
        logger.info(f"  Entry attempts:            {self.diagnostics['total_entry_attempts']:,}")
        logger.info(f"  Insufficient capital:      {self.diagnostics['insufficient_capital']:,}")
        logger.info(f"  Max positions reached:     {self.diagnostics['max_positions_reached']:,}")
        logger.info(f"  Insufficient data (<252):  {self.diagnostics['insufficient_data']:,}")

        # CRITICAL VALIDATION: Entry evaluations should be > 0 if we have valid tickers
        if self.diagnostics['entry_evaluations'] == 0:
            logger.warning("")
            logger.warning("=" * 60)
            logger.warning("WARNING: ZERO ENTRY EVALUATIONS PERFORMED")
            logger.warning("=" * 60)
            logger.warning("Entry evaluations = 0 indicates structural issue:")
            logger.warning("  1. No ticker data available for backtest period")
            logger.warning("  2. All tickers had insufficient data (<252 bars)")
            logger.warning("  3. Backtest period has no trading days")
            logger.warning("")
            logger.warning("RECOMMENDATION:")
            logger.warning("  - Run 'python main.py --mode stage2' first")
            logger.warning("  - Check that screening_results.csv has candidates")
            logger.warning("  - Verify backtest period overlaps with available data")
            logger.warning("=" * 60)

        if self.diagnostics['entry_failed_conditions']:
            logger.info("")
            logger.info("Top Entry failure reasons (rs_new_high excluded):")
            sorted_failures = sorted(
                self.diagnostics['entry_failed_conditions'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for condition, count in sorted_failures[:5]:
                logger.info(f"  {condition:25} {count:>6,} failures")

        # Calculate pass rate
        if self.diagnostics['entry_evaluations'] > 0:
            pass_rate = self.diagnostics['entry_passed'] / self.diagnostics['entry_evaluations'] * 100
            logger.info("")
            logger.info(f"Entry pass rate:             {pass_rate:.1f}%")
            logger.info("  (Entry conditions: price>sma50, sma50>sma150, volume)")
            logger.info("  (rs_new_high NOT included in daily entry checks)")

        # Warnings if no trades
        if total_trades == 0:
            logger.warning("")
            logger.warning("NO TRADES EXECUTED - Possible issues:")
            if self.diagnostics['entry_passed'] == 0:
                logger.warning("  - No stocks passed Entry conditions")
                if self.diagnostics['entry_failed_conditions']:
                    top_failure = max(
                        self.diagnostics['entry_failed_conditions'].items(),
                        key=lambda x: x[1]
                    )
                    logger.warning(f"    Most common failure: {top_failure[0]} ({top_failure[1]:,} times)")
            elif self.diagnostics['insufficient_capital'] > 0:
                logger.warning("  - Insufficient capital to open positions")
            elif self.diagnostics['total_entry_attempts'] > 0:
                logger.warning("  - Entry passed but position sizing failed")

        logger.info("=" * 60)

    def _check_exit(self, pos: Position, current_bar: pd.Series) -> tuple:
        """
        Check exit conditions.

        Returns:
            (exit_signal: bool, exit_reason: str)
        """
        close = current_bar['close']

        # Stop loss
        if close <= pos.stop_price:
            return True, 'stop_loss'

        # 50-day MA break
        if 'sma_50' in current_bar and close < current_bar['sma_50']:
            return True, 'ma50_break'

        # Target reached
        if close >= pos.target_price:
            return True, 'target_reached'

        return False, ''

    def _calculate_results(
        self,
        trades: List[Position],
        equity_curve: List[Dict],
        benchmark_enabled: bool = True,
    ) -> BacktestResult:
        """Calculate backtest statistics"""
        if not trades:
            return self._empty_result(benchmark_enabled)

        # Convert equity curve to Series
        equity_df = pd.DataFrame(equity_curve)
        equity_series = equity_df.set_index('date')['equity']

        # Basic statistics
        final_capital = equity_series.iloc[-1] if len(equity_series) > 0 else self.initial_capital
        total_return = final_capital - self.initial_capital
        total_return_pct = total_return / self.initial_capital

        # Win/Loss statistics
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]

        win_rate = len(winning_trades) / len(trades) if trades else 0
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.pnl for t in losing_trades])) if losing_trades else 0

        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # Maximum drawdown
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak
        max_drawdown_pct = drawdown.min()
        max_drawdown = (peak - equity_series).max()

        # Sharpe ratio (assuming risk-free rate of 0)
        if len(equity_series) > 1:
            returns = equity_series.pct_change().dropna()
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0

        return BacktestResult(
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            sharpe_ratio=sharpe_ratio,
            benchmark_enabled=benchmark_enabled,
            trades=trades,
            equity_curve=equity_series
        )

    def _empty_result(self, benchmark_enabled: bool = True) -> BacktestResult:
        """Return empty result"""
        return BacktestResult(
            initial_capital=self.initial_capital,
            final_capital=self.initial_capital,
            total_return=0,
            total_return_pct=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            avg_win=0,
            avg_loss=0,
            profit_factor=0,
            max_drawdown=0,
            max_drawdown_pct=0,
            sharpe_ratio=0,
            benchmark_enabled=benchmark_enabled,
            trades=[],
            equity_curve=pd.Series()
        )


def run_backtest(config: Dict, tickers: List[str], use_benchmark: bool = True) -> BacktestResult:
    """
    Run backtest with given configuration.

    Args:
        config: Configuration dictionary
        tickers: List of ticker symbols
        use_benchmark: Whether to use SPY benchmark

    Returns:
        BacktestResult object
    """
    engine = BacktestEngine(config, use_benchmark=use_benchmark)
    return engine.run(
        tickers,
        config['backtest']['start_date'],
        config['backtest']['end_date']
    )


def print_backtest_report(result: BacktestResult):
    """Print formatted backtest report"""
    print("\n" + "=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    benchmark_status = "Enabled" if result.benchmark_enabled else "Disabled"
    print(f"Benchmark:          {benchmark_status}")
    print(f"Initial Capital:    ${result.initial_capital:,.2f}")
    print(f"Final Capital:      ${result.final_capital:,.2f}")
    print(f"Total Return:       ${result.total_return:,.2f} ({result.total_return_pct:.1%})")
    print("-" * 60)
    print(f"Total Trades:       {result.total_trades}")
    print(f"Winning Trades:     {result.winning_trades}")
    print(f"Losing Trades:      {result.losing_trades}")
    print(f"Win Rate:           {result.win_rate:.1%}")
    print("-" * 60)
    print(f"Average Win:        ${result.avg_win:,.2f}")
    print(f"Average Loss:       ${result.avg_loss:,.2f}")
    print(f"Profit Factor:      {result.profit_factor:.2f}")
    print("-" * 60)
    print(f"Max Drawdown:       ${result.max_drawdown:,.2f} ({result.max_drawdown_pct:.1%})")
    print(f"Sharpe Ratio:       {result.sharpe_ratio:.2f}")
    print("=" * 60)
