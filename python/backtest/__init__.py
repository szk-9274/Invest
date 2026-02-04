"""
Backtest package for stock screening system

Architecture:
- Stage2 = Universe Selection (one-time filter at start)
- EntryCondition = Daily trade decision (lightweight, no rs_new_high)
- state_conditions = Historical event conditions (rs_new_high as state)
"""
from backtest.engine import BacktestEngine, BacktestResult, Position, run_backtest, print_backtest_report
from backtest.entry_condition import EntryCondition
from backtest.universe_loader import UniverseLoader
from backtest.state_conditions import has_recent_rs_new_high
from backtest.performance import (
    calculate_cagr,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_calmar_ratio,
    calculate_monthly_returns,
    calculate_win_loss_stats,
    generate_performance_summary
)

try:
    from backtest.visualization import visualize_backtest_results, generate_html_report
except (ImportError, AttributeError, Exception):
    visualize_backtest_results = None
    generate_html_report = None

try:
    from backtest.ticker_charts import (
        generate_price_chart,
        generate_price_chart_from_dataframe,
        TickerCharts,
    )
except (ImportError, AttributeError, Exception):
    generate_price_chart = None
    generate_price_chart_from_dataframe = None
    TickerCharts = None

__all__ = [
    'BacktestEngine',
    'BacktestResult',
    'Position',
    'run_backtest',
    'print_backtest_report',
    'EntryCondition',
    'UniverseLoader',
    'has_recent_rs_new_high',
    'calculate_cagr',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'calculate_max_drawdown',
    'calculate_calmar_ratio',
    'calculate_monthly_returns',
    'calculate_win_loss_stats',
    'generate_performance_summary',
    'visualize_backtest_results',
    'generate_html_report',
    'generate_price_chart',
    'generate_price_chart_from_dataframe',
    'TickerCharts',
]
