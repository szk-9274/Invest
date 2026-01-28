"""
Fundamentals Analyzer Module
Implements Minervini's growth stock criteria for fundamental analysis
"""
import warnings

# Suppress yfinance DeprecationWarning before import
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*Ticker.earnings.*")

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from loguru import logger
import time


@dataclass
class FundamentalsFilter:
    """Fundamentals filter configuration"""
    min_eps_growth: float = 0.25        # 25% minimum EPS growth
    min_revenue_growth: float = 0.25    # 25% minimum revenue growth
    min_operating_margin: float = 0.15  # 15% minimum operating margin (optional)
    require_qoq_acceleration: bool = True  # Require QoQ acceleration
    enabled: bool = True


@dataclass
class FundamentalsResult:
    """Result of fundamentals analysis"""
    ticker: str
    passes_filter: bool
    eps_growth: Optional[float] = None
    revenue_growth: Optional[float] = None
    operating_margin: Optional[float] = None
    qoq_eps_accelerating: Optional[bool] = None
    qoq_revenue_accelerating: Optional[bool] = None
    details: Dict = field(default_factory=dict)
    error: Optional[str] = None


class FundamentalsAnalyzer:
    """
    Analyzes stock fundamentals based on Minervini's growth criteria.

    Key Metrics:
    - EPS Growth: Earnings per share growth YoY (target: 25%+)
    - Revenue Growth: Sales growth YoY (target: 25%+)
    - QoQ Acceleration: Quarter-over-quarter growth acceleration
    - Operating Margin: Profitability indicator (target: 15%+)
    """

    def __init__(
        self,
        config: Optional[Dict] = None,
        request_delay: float = 0.3
    ):
        """
        Initialize the fundamentals analyzer.

        Args:
            config: Configuration dictionary with fundamentals settings
            request_delay: Delay between API requests
        """
        self.request_delay = request_delay

        # Load filter configuration
        if config and 'fundamentals' in config:
            fund_config = config['fundamentals']
            self.filter = FundamentalsFilter(
                min_eps_growth=fund_config.get('min_eps_growth', 0.25),
                min_revenue_growth=fund_config.get('min_revenue_growth', 0.25),
                min_operating_margin=fund_config.get('min_operating_margin', 0.15),
                require_qoq_acceleration=fund_config.get('require_qoq_acceleration', True),
                enabled=fund_config.get('enabled', True)
            )
        else:
            self.filter = FundamentalsFilter()

    def analyze(self, ticker: str) -> FundamentalsResult:
        """
        Analyze fundamentals for a single ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            FundamentalsResult with analysis details
        """
        if not self.filter.enabled:
            return FundamentalsResult(
                ticker=ticker,
                passes_filter=True,
                details={'message': 'Fundamentals filter disabled'}
            )

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Get basic metrics from info
            eps_growth = info.get('earningsQuarterlyGrowth')
            revenue_growth = info.get('revenueGrowth')
            operating_margin = info.get('operatingMargins')

            # Get quarterly data for QoQ analysis
            qoq_eps_accelerating = None
            qoq_revenue_accelerating = None

            try:
                quarterly_earnings = stock.quarterly_earnings
                if quarterly_earnings is not None and len(quarterly_earnings) >= 3:
                    qoq_eps_accelerating = self._check_qoq_acceleration(
                        quarterly_earnings['Earnings'].tolist()
                    )
            except Exception as e:
                logger.debug(f"{ticker}: Could not get quarterly earnings - {e}")

            try:
                quarterly_financials = stock.quarterly_financials
                if quarterly_financials is not None and 'Total Revenue' in quarterly_financials.index:
                    revenues = quarterly_financials.loc['Total Revenue'].tolist()
                    if len(revenues) >= 3:
                        qoq_revenue_accelerating = self._check_qoq_acceleration(revenues)
            except Exception as e:
                logger.debug(f"{ticker}: Could not get quarterly financials - {e}")

            # Evaluate against filter criteria
            passes = self._evaluate_criteria(
                eps_growth=eps_growth,
                revenue_growth=revenue_growth,
                operating_margin=operating_margin,
                qoq_eps_accelerating=qoq_eps_accelerating,
                qoq_revenue_accelerating=qoq_revenue_accelerating
            )

            time.sleep(self.request_delay)

            return FundamentalsResult(
                ticker=ticker,
                passes_filter=passes,
                eps_growth=eps_growth,
                revenue_growth=revenue_growth,
                operating_margin=operating_margin,
                qoq_eps_accelerating=qoq_eps_accelerating,
                qoq_revenue_accelerating=qoq_revenue_accelerating,
                details={
                    'eps_growth_pass': self._check_eps_growth(eps_growth),
                    'revenue_growth_pass': self._check_revenue_growth(revenue_growth),
                    'operating_margin_pass': self._check_operating_margin(operating_margin),
                    'qoq_acceleration_pass': self._check_qoq_requirement(
                        qoq_eps_accelerating,
                        qoq_revenue_accelerating
                    )
                }
            )

        except Exception as e:
            logger.error(f"{ticker}: Error analyzing fundamentals - {e}")
            return FundamentalsResult(
                ticker=ticker,
                passes_filter=False,
                error=str(e)
            )

    def _check_qoq_acceleration(self, values: List[float]) -> bool:
        """
        Check if quarter-over-quarter growth is accelerating.

        Acceleration means the growth rate is increasing:
        Q1 -> Q2 growth rate < Q2 -> Q3 growth rate

        Args:
            values: List of quarterly values (most recent first)

        Returns:
            True if accelerating
        """
        if len(values) < 3:
            return False

        # Values come in most recent first order from yfinance
        # We need at least 3 quarters to check acceleration
        try:
            # Calculate growth rates
            # growth_1 = (Q-1 - Q-2) / Q-2
            # growth_2 = (Q-2 - Q-3) / Q-3
            q1, q2, q3 = values[0], values[1], values[2]

            if q2 == 0 or q3 == 0:
                return False

            growth_recent = (q1 - q2) / abs(q2) if q2 != 0 else 0
            growth_prior = (q2 - q3) / abs(q3) if q3 != 0 else 0

            # Accelerating if recent growth > prior growth
            return growth_recent > growth_prior

        except (TypeError, ZeroDivisionError):
            return False

    def _check_eps_growth(self, eps_growth: Optional[float]) -> bool:
        """Check if EPS growth meets criteria"""
        if eps_growth is None:
            return False
        return eps_growth >= self.filter.min_eps_growth

    def _check_revenue_growth(self, revenue_growth: Optional[float]) -> bool:
        """Check if revenue growth meets criteria"""
        if revenue_growth is None:
            return False
        return revenue_growth >= self.filter.min_revenue_growth

    def _check_operating_margin(self, operating_margin: Optional[float]) -> bool:
        """Check if operating margin meets criteria (optional)"""
        if operating_margin is None:
            # Operating margin is optional, so missing data passes
            return True
        return operating_margin >= self.filter.min_operating_margin

    def _check_qoq_requirement(
        self,
        qoq_eps: Optional[bool],
        qoq_revenue: Optional[bool]
    ) -> bool:
        """Check if QoQ acceleration requirement is met"""
        if not self.filter.require_qoq_acceleration:
            return True

        # At least one should be accelerating if required
        eps_ok = qoq_eps is True
        rev_ok = qoq_revenue is True

        # Pass if either EPS or Revenue is accelerating
        return eps_ok or rev_ok

    def _evaluate_criteria(
        self,
        eps_growth: Optional[float],
        revenue_growth: Optional[float],
        operating_margin: Optional[float],
        qoq_eps_accelerating: Optional[bool],
        qoq_revenue_accelerating: Optional[bool]
    ) -> bool:
        """
        Evaluate all criteria.

        Required:
        - EPS growth >= min_eps_growth OR Revenue growth >= min_revenue_growth

        Optional:
        - Operating margin >= min_operating_margin
        - QoQ acceleration (if required)

        Returns:
            True if passes all required criteria
        """
        # At least one of EPS or Revenue growth should meet criteria
        eps_ok = self._check_eps_growth(eps_growth)
        revenue_ok = self._check_revenue_growth(revenue_growth)

        if not (eps_ok or revenue_ok):
            return False

        # Operating margin (if data available)
        if operating_margin is not None:
            if not self._check_operating_margin(operating_margin):
                # Log but don't fail - operating margin is secondary
                logger.debug(f"Operating margin {operating_margin:.1%} below threshold")

        # QoQ acceleration check
        if self.filter.require_qoq_acceleration:
            qoq_ok = self._check_qoq_requirement(
                qoq_eps_accelerating,
                qoq_revenue_accelerating
            )
            if not qoq_ok:
                # If we can't verify QoQ, we still pass if base metrics are strong
                if eps_ok and revenue_ok:
                    return True
                return False

        return True

    def analyze_batch(
        self,
        tickers: List[str],
        show_progress: bool = True
    ) -> Dict[str, FundamentalsResult]:
        """
        Analyze fundamentals for multiple tickers.

        Args:
            tickers: List of ticker symbols
            show_progress: Show progress bar

        Returns:
            Dictionary {ticker: FundamentalsResult}
        """
        results = {}

        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(tickers, desc="Fundamentals Analysis")
        else:
            iterator = tickers

        for ticker in iterator:
            results[ticker] = self.analyze(ticker)

        # Summary
        passed = sum(1 for r in results.values() if r.passes_filter)
        logger.info(f"Fundamentals: {passed}/{len(tickers)} passed filter")

        return results

    def get_summary(self, result: FundamentalsResult) -> str:
        """
        Get a human-readable summary of the analysis.

        Args:
            result: FundamentalsResult object

        Returns:
            Summary string
        """
        if result.error:
            return f"{result.ticker}: Error - {result.error}"

        status = "PASS" if result.passes_filter else "FAIL"
        parts = [f"{result.ticker}: {status}"]

        if result.eps_growth is not None:
            parts.append(f"EPS: {result.eps_growth:.1%}")

        if result.revenue_growth is not None:
            parts.append(f"Revenue: {result.revenue_growth:.1%}")

        if result.operating_margin is not None:
            parts.append(f"OpMargin: {result.operating_margin:.1%}")

        if result.qoq_eps_accelerating is not None:
            accel = "Yes" if result.qoq_eps_accelerating else "No"
            parts.append(f"EPS Accel: {accel}")

        return " | ".join(parts)
