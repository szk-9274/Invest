"""
Backtest package for stock screening system
"""
from backtest.engine import BacktestEngine, BacktestResult, Position, run_backtest, print_backtest_report
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

__all__ = [
    'BacktestEngine',
    'BacktestResult',
    'Position',
    'run_backtest',
    'print_backtest_report',
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
]
