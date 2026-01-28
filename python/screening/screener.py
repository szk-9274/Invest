"""
Stock screening integration module
"""
import pandas as pd
from typing import List, Dict, Optional
from loguru import logger
from tqdm import tqdm

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetcher import YahooFinanceFetcher
from analysis.stage_detector import StageDetector
from analysis.vcp_detector import VCPDetector
from analysis.indicators import calculate_all_indicators
from analysis.fundamentals import FundamentalsAnalyzer


class Screener:
    """Stock screening integration class"""

    def __init__(self, config: Dict, use_benchmark: bool = True):
        """
        Initialize the screener.

        Args:
            config: Configuration dictionary (from params.yaml)
            use_benchmark: Whether to use SPY benchmark for RS calculation.
                           If True but fetch fails, auto-fallback to False.
        """
        self.config = config
        self.use_benchmark = use_benchmark
        self.fetcher = YahooFinanceFetcher(
            request_delay=config['performance']['request_delay']
        )
        self.stage_detector = StageDetector(config['stage'])
        self.vcp_detector = VCPDetector(config['vcp'])
        self.fundamentals_analyzer = FundamentalsAnalyzer(config)

    def _fetch_benchmark(self) -> Optional[pd.DataFrame]:
        """
        Fetch benchmark data. On failure, log warning and return None
        (triggers automatic fallback to no-benchmark mode).
        """
        if not self.use_benchmark:
            logger.info("Benchmark disabled by user (--no-benchmark)")
            return None

        benchmark_symbol = self.config['benchmark']['symbol']
        benchmark_data = self.fetcher.fetch_benchmark(
            benchmark_symbol,
            period=self.config['data']['history_period'],
        )

        if benchmark_data is None:
            logger.warning(
                f"Failed to fetch benchmark data ({benchmark_symbol}). "
                "Falling back to no-benchmark mode."
            )
            return None

        return benchmark_data

    def screen(self, tickers: List[str]) -> pd.DataFrame:
        """
        Screen all tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            DataFrame with screening results
        """
        results = []

        # Fetch benchmark data (with fallback)
        benchmark_data = self._fetch_benchmark()
        use_benchmark = benchmark_data is not None

        if not use_benchmark:
            logger.info("Running in NO-BENCHMARK mode (RS condition auto-passed)")

        # Process each ticker
        logger.info(f"Screening {len(tickers)} tickers...")

        for ticker in tqdm(tickers, desc="Screening"):
            try:
                result = self._process_ticker(ticker, benchmark_data, use_benchmark)
                if result:
                    results.append(result)

            except Exception as e:
                logger.error(f"{ticker}: Error - {e}")
                continue

        # Convert to DataFrame
        if results:
            df = pd.DataFrame(results)
            logger.info(f"Found {len(df)} Stage 2 + VCP candidates")
            return df
        else:
            logger.warning("No candidates found")
            return pd.DataFrame()

    def screen_stage2_only(self, tickers: List[str]) -> pd.DataFrame:
        """
        Screen for Stage 2 stocks only (without VCP requirement).

        Args:
            tickers: List of ticker symbols

        Returns:
            DataFrame with Stage 2 stocks
        """
        results = []

        # Fetch benchmark data (with fallback)
        benchmark_data = self._fetch_benchmark()
        use_benchmark = benchmark_data is not None

        if not use_benchmark:
            logger.info("Running in NO-BENCHMARK mode (RS condition auto-passed)")

        logger.info(f"Screening {len(tickers)} tickers for Stage 2...")

        for ticker in tqdm(tickers, desc="Stage 2 Screening"):
            try:
                result = self._process_ticker_stage2(ticker, benchmark_data, use_benchmark)
                if result:
                    results.append(result)

            except Exception as e:
                logger.error(f"{ticker}: Error - {e}")
                continue

        if results:
            df = pd.DataFrame(results)
            logger.info(f"Found {len(df)} Stage 2 candidates")
            return df
        else:
            logger.warning("No Stage 2 candidates found")
            return pd.DataFrame()

    def screen_with_fundamentals(self, tickers: List[str]) -> pd.DataFrame:
        """
        Screen for Stage 2 stocks with fundamentals filter.

        Args:
            tickers: List of ticker symbols

        Returns:
            DataFrame with Stage 2 stocks that pass fundamentals filter
        """
        results = []

        # Fetch benchmark data (with fallback)
        benchmark_data = self._fetch_benchmark()
        use_benchmark = benchmark_data is not None

        if not use_benchmark:
            logger.info("Running in NO-BENCHMARK mode (RS condition auto-passed)")

        logger.info(f"Screening {len(tickers)} tickers for Stage 2 + Fundamentals...")

        for ticker in tqdm(tickers, desc="Stage 2 + Fundamentals Screening"):
            try:
                result = self._process_ticker_with_fundamentals(
                    ticker, benchmark_data, use_benchmark
                )
                if result:
                    results.append(result)

            except Exception as e:
                logger.error(f"{ticker}: Error - {e}")
                continue

        if results:
            df = pd.DataFrame(results)
            logger.info(f"Found {len(df)} Stage 2 + Fundamentals candidates")
            return df
        else:
            logger.warning("No candidates found with fundamentals filter")
            return pd.DataFrame()

    def _process_ticker_with_fundamentals(
        self,
        ticker: str,
        benchmark_data: Optional[pd.DataFrame],
        use_benchmark: bool = True,
    ) -> Optional[Dict]:
        """
        Process a single ticker for Stage 2 with fundamentals.

        Returns:
            Screening result or None
        """
        # Fetch data
        data = self.fetcher.fetch_data(
            ticker,
            period=self.config['data']['history_period']
        )

        if data is None or len(data) < 252:
            return None

        # Calculate technical indicators
        data = calculate_all_indicators(data, benchmark_data)

        # Stage detection
        rs_line = data['rs_line'] if use_benchmark else None
        stage_result = self.stage_detector.detect_stage(
            data, rs_line, use_benchmark=use_benchmark
        )

        if stage_result['stage'] != 2:
            return None

        # Fundamentals analysis
        fund_result = self.fundamentals_analyzer.analyze(ticker)

        if not fund_result.passes_filter:
            logger.debug(f"{ticker}: Failed fundamentals filter")
            return None

        # Get 52-week high/low
        high_52w = data['high'].tail(252).max()
        low_52w = data['low'].tail(252).min()

        current_price = data['close'].iloc[-1]
        distance_from_high = (high_52w - current_price) / high_52w * 100

        return {
            'ticker': ticker,
            'stage': 2,
            'current_price': round(current_price, 2),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'distance_from_high_pct': round(distance_from_high, 2),
            'sma_50': round(data['sma_50'].iloc[-1], 2),
            'sma_150': round(data['sma_150'].iloc[-1], 2),
            'sma_200': round(data['sma_200'].iloc[-1], 2),
            'rs_new_high': stage_result['details']['rs_new_high'],
            'benchmark_enabled': use_benchmark,
            'volume_50d_avg': int(data['volume_ma_50'].iloc[-1]),
            # Fundamentals data
            'eps_growth': round(fund_result.eps_growth * 100, 1) if fund_result.eps_growth else None,
            'revenue_growth': round(fund_result.revenue_growth * 100, 1) if fund_result.revenue_growth else None,
            'operating_margin': round(fund_result.operating_margin * 100, 1) if fund_result.operating_margin else None,
            'qoq_accelerating': fund_result.qoq_eps_accelerating or fund_result.qoq_revenue_accelerating,
            'conditions_met': sum(stage_result['details'].values()),
            'total_conditions': len(stage_result['details']),
            'last_updated': data.index[-1].strftime('%Y-%m-%d')
        }

    def _process_ticker(
        self,
        ticker: str,
        benchmark_data: Optional[pd.DataFrame],
        use_benchmark: bool = True,
    ) -> Optional[Dict]:
        """
        Process a single ticker.

        Returns:
            Screening result or None
        """
        # Fetch data
        data = self.fetcher.fetch_data(
            ticker,
            period=self.config['data']['history_period']
        )

        if data is None or len(data) < 252:
            return None

        # Calculate technical indicators
        data = calculate_all_indicators(data, benchmark_data)

        # Stage detection
        rs_line = data['rs_line'] if use_benchmark else None
        stage_result = self.stage_detector.detect_stage(
            data, rs_line, use_benchmark=use_benchmark
        )

        if stage_result['stage'] != 2:
            return None

        # VCP detection
        vcp_result = self.vcp_detector.detect_vcp(data)

        if vcp_result is None:
            return None

        # Risk validation
        risk_pct = vcp_result['risk_pct']
        max_risk = self.config['risk']['initial_stop_max']
        if risk_pct > max_risk:
            logger.debug(f"{ticker}: Risk too high ({risk_pct:.2%} > {max_risk:.2%})")
            return None

        # Risk/Reward calculation
        entry = vcp_result['entry_price']
        stop = vcp_result['stop_price']
        target = entry * 1.25  # +25% target

        risk = entry - stop
        reward = target - entry
        risk_reward = reward / risk if risk > 0 else 0

        if risk_reward < 3.0:
            logger.debug(f"{ticker}: R/R too low ({risk_reward:.2f})")
            return None

        # Return result
        return {
            'ticker': ticker,
            'stage': 2,
            'rs_new_high': stage_result['details']['rs_new_high'],
            'benchmark_enabled': use_benchmark,
            'has_vcp': True,
            'pivot': round(vcp_result['pivot'], 2),
            'entry_price': round(entry, 2),
            'stop_price': round(stop, 2),
            'target_price': round(target, 2),
            'risk_pct': round(risk_pct * 100, 2),
            'risk_reward': round(risk_reward, 2),
            'current_price': round(data['close'].iloc[-1], 2),
            'volume_50d_avg': int(data['volume_ma_50'].iloc[-1]),
            'contraction_count': vcp_result['contraction_count'],
            'dryup_confirmed': vcp_result['dryup_confirmed'],
            'last_updated': data.index[-1].strftime('%Y-%m-%d')
        }

    def _process_ticker_stage2(
        self,
        ticker: str,
        benchmark_data: Optional[pd.DataFrame],
        use_benchmark: bool = True,
    ) -> Optional[Dict]:
        """
        Process a single ticker for Stage 2 only.

        Returns:
            Screening result or None
        """
        # Fetch data
        data = self.fetcher.fetch_data(
            ticker,
            period=self.config['data']['history_period']
        )

        if data is None or len(data) < 252:
            return None

        # Calculate technical indicators
        data = calculate_all_indicators(data, benchmark_data)

        # Stage detection
        rs_line = data['rs_line'] if use_benchmark else None
        stage_result = self.stage_detector.detect_stage(
            data, rs_line, use_benchmark=use_benchmark
        )

        if stage_result['stage'] != 2:
            return None

        # Get 52-week high/low
        high_52w = data['high'].tail(252).max()
        low_52w = data['low'].tail(252).min()

        current_price = data['close'].iloc[-1]
        distance_from_high = (high_52w - current_price) / high_52w * 100

        return {
            'ticker': ticker,
            'stage': 2,
            'current_price': round(current_price, 2),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'distance_from_high_pct': round(distance_from_high, 2),
            'sma_50': round(data['sma_50'].iloc[-1], 2),
            'sma_150': round(data['sma_150'].iloc[-1], 2),
            'sma_200': round(data['sma_200'].iloc[-1], 2),
            'rs_new_high': stage_result['details']['rs_new_high'],
            'benchmark_enabled': use_benchmark,
            'volume_50d_avg': int(data['volume_ma_50'].iloc[-1]),
            'conditions_met': sum(stage_result['details'].values()),
            'total_conditions': len(stage_result['details']),
            'last_updated': data.index[-1].strftime('%Y-%m-%d')
        }
