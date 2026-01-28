"""
Performance Metrics Module
Calculates various performance metrics for backtest results
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass


def calculate_cagr(
    initial_capital: float,
    final_capital: float,
    years: float
) -> float:
    """
    Calculate Compound Annual Growth Rate.

    Args:
        initial_capital: Starting capital
        final_capital: Ending capital
        years: Number of years

    Returns:
        CAGR as a decimal (e.g., 0.15 for 15%)
    """
    if initial_capital <= 0 or years <= 0:
        return 0.0

    return (final_capital / initial_capital) ** (1 / years) - 1


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sharpe Ratio.

    Args:
        returns: Series of periodic returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of trading periods per year

    Returns:
        Sharpe Ratio
    """
    if returns.empty or returns.std() == 0:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)
    return excess_returns.mean() / returns.std() * np.sqrt(periods_per_year)


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sortino Ratio (uses only downside deviation).

    Args:
        returns: Series of periodic returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of trading periods per year

    Returns:
        Sortino Ratio
    """
    if returns.empty:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)
    negative_returns = returns[returns < 0]

    if negative_returns.empty or negative_returns.std() == 0:
        return float('inf') if excess_returns.mean() > 0 else 0.0

    downside_std = negative_returns.std()
    return excess_returns.mean() / downside_std * np.sqrt(periods_per_year)


def calculate_max_drawdown(equity_curve: pd.Series) -> Dict[str, float]:
    """
    Calculate Maximum Drawdown and related metrics.

    Args:
        equity_curve: Series of equity values

    Returns:
        Dictionary with max_drawdown, max_drawdown_pct, drawdown_duration
    """
    if equity_curve.empty:
        return {
            'max_drawdown': 0.0,
            'max_drawdown_pct': 0.0,
            'drawdown_duration': 0
        }

    # Calculate running maximum
    rolling_max = equity_curve.cummax()

    # Calculate drawdown
    drawdown = equity_curve - rolling_max
    drawdown_pct = drawdown / rolling_max

    # Find maximum drawdown
    max_drawdown = abs(drawdown.min())
    max_drawdown_pct = abs(drawdown_pct.min())

    # Calculate drawdown duration
    in_drawdown = drawdown < 0
    duration = 0
    max_duration = 0
    for is_dd in in_drawdown:
        if is_dd:
            duration += 1
            max_duration = max(max_duration, duration)
        else:
            duration = 0

    return {
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_drawdown_pct,
        'drawdown_duration': max_duration
    }


def calculate_calmar_ratio(
    cagr: float,
    max_drawdown_pct: float
) -> float:
    """
    Calculate Calmar Ratio (CAGR / Max Drawdown).

    Args:
        cagr: Compound Annual Growth Rate
        max_drawdown_pct: Maximum Drawdown percentage

    Returns:
        Calmar Ratio
    """
    if max_drawdown_pct == 0:
        return float('inf') if cagr > 0 else 0.0

    return cagr / abs(max_drawdown_pct)


def calculate_monthly_returns(equity_curve: pd.Series) -> pd.DataFrame:
    """
    Calculate monthly returns table.

    Args:
        equity_curve: Series of equity values with datetime index

    Returns:
        DataFrame with monthly returns by year
    """
    if equity_curve.empty:
        return pd.DataFrame()

    # Resample to monthly
    monthly = equity_curve.resample('ME').last()
    monthly_returns = monthly.pct_change()

    # Create pivot table
    monthly_returns_df = monthly_returns.to_frame('return')
    monthly_returns_df['year'] = monthly_returns_df.index.year
    monthly_returns_df['month'] = monthly_returns_df.index.month

    # Pivot
    pivot = monthly_returns_df.pivot(
        index='year',
        columns='month',
        values='return'
    )

    # Rename columns to month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot.columns = [month_names[i - 1] for i in pivot.columns]

    # Add yearly total
    pivot['Year'] = (1 + pivot.fillna(0)).prod(axis=1) - 1

    return pivot


def calculate_win_loss_stats(trades: List) -> Dict[str, float]:
    """
    Calculate win/loss statistics from trades.

    Args:
        trades: List of Position objects

    Returns:
        Dictionary with win/loss statistics
    """
    if not trades:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'avg_win_pct': 0.0,
            'avg_loss_pct': 0.0,
            'profit_factor': 0.0,
            'expectancy': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'avg_holding_days': 0.0
        }

    winners = [t for t in trades if t.pnl > 0]
    losers = [t for t in trades if t.pnl <= 0]

    total_trades = len(trades)
    winning_trades = len(winners)
    losing_trades = len(losers)
    win_rate = winning_trades / total_trades if total_trades > 0 else 0

    avg_win = np.mean([t.pnl for t in winners]) if winners else 0
    avg_loss = abs(np.mean([t.pnl for t in losers])) if losers else 0
    avg_win_pct = np.mean([t.pnl_pct for t in winners]) if winners else 0
    avg_loss_pct = abs(np.mean([t.pnl_pct for t in losers])) if losers else 0

    gross_profit = sum(t.pnl for t in winners)
    gross_loss = abs(sum(t.pnl for t in losers))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    # Expectancy (average profit per trade)
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    # Best and worst trades
    best_trade = max(t.pnl_pct for t in trades)
    worst_trade = min(t.pnl_pct for t in trades)

    # Average holding period
    holding_days = []
    for t in trades:
        if t.entry_date and t.exit_date:
            days = (t.exit_date - t.entry_date).days
            holding_days.append(days)
    avg_holding_days = np.mean(holding_days) if holding_days else 0

    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'avg_win_pct': avg_win_pct,
        'avg_loss_pct': avg_loss_pct,
        'profit_factor': profit_factor,
        'expectancy': expectancy,
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'avg_holding_days': avg_holding_days
    }


def generate_performance_summary(
    result,
    start_date: str,
    end_date: str
) -> str:
    """
    Generate a formatted performance summary string.

    Args:
        result: BacktestResult object
        start_date: Backtest start date
        end_date: Backtest end date

    Returns:
        Formatted summary string
    """
    # Calculate additional metrics
    years = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days / 365.25
    cagr = calculate_cagr(result.initial_capital, result.final_capital, years)
    win_loss = calculate_win_loss_stats(result.trades)

    benchmark_status = "Enabled" if getattr(result, 'benchmark_enabled', True) else "Disabled"

    lines = [
        "=" * 80,
        f"BACKTEST RESULTS ({start_date} to {end_date})",
        "=" * 80,
        f"Benchmark:            {benchmark_status}",
        f"Initial Capital:      ${result.initial_capital:,.2f}",
        f"Final Capital:        ${result.final_capital:,.2f}",
        f"Total Return:         {result.total_return_pct:+.1%}",
        f"CAGR:                 {cagr:.1%}",
        f"Max Drawdown:         {result.max_drawdown_pct:.1%}",
        f"Sharpe Ratio:         {result.sharpe_ratio:.2f}",
        "-" * 80,
        f"Win Rate:             {win_loss['win_rate']:.1%}",
        f"Avg Gain:             {win_loss['avg_win_pct']:+.1%}",
        f"Avg Loss:             {-win_loss['avg_loss_pct']:.1%}",
        f"Profit Factor:        {win_loss['profit_factor']:.2f}",
        "-" * 80,
        f"Total Trades:         {win_loss['total_trades']}",
        f"Avg Holding Days:     {win_loss['avg_holding_days']:.1f}",
        f"Best Trade:           {win_loss['best_trade']:+.1%}",
        f"Worst Trade:          {win_loss['worst_trade']:.1%}",
        "=" * 80
    ]

    return "\n".join(lines)
