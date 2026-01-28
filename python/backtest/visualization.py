"""
Backtest Visualization Module
Generates charts and visual reports for backtest results
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
from loguru import logger

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available, visualization will be limited")


def visualize_backtest_results(
    result,
    output_dir: Optional[Path] = None,
    show_plots: bool = False
) -> None:
    """
    Generate visualization charts for backtest results.

    Args:
        result: BacktestResult object
        output_dir: Directory to save charts
        show_plots: Whether to display plots interactively
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("matplotlib not installed, skipping visualization")
        return

    if output_dir is None:
        output_dir = Path("output/backtest")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')

    # Generate charts
    _plot_equity_curve(result, output_dir, show_plots)
    _plot_drawdown(result, output_dir, show_plots)
    _plot_monthly_returns(result, output_dir, show_plots)
    _plot_trade_distribution(result, output_dir, show_plots)

    logger.info(f"Visualization complete. Charts saved to: {output_dir}")


def _plot_equity_curve(
    result,
    output_dir: Path,
    show_plots: bool
) -> None:
    """Plot equity curve"""
    if result.equity_curve.empty:
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot equity curve
    ax.plot(
        result.equity_curve.index,
        result.equity_curve.values,
        linewidth=1.5,
        color='#2E86AB',
        label='Portfolio Equity'
    )

    # Add initial capital line
    ax.axhline(
        y=result.initial_capital,
        color='gray',
        linestyle='--',
        linewidth=1,
        label='Initial Capital'
    )

    # Format
    ax.set_title('Equity Curve', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Portfolio Value ($)')
    ax.legend(loc='upper left')

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)

    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

    # Add grid
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'equity_curve.png', dpi=150)

    if show_plots:
        plt.show()
    plt.close()


def _plot_drawdown(
    result,
    output_dir: Path,
    show_plots: bool
) -> None:
    """Plot drawdown chart"""
    if result.equity_curve.empty:
        return

    # Calculate drawdown
    equity = result.equity_curve
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max * 100

    fig, ax = plt.subplots(figsize=(12, 4))

    # Plot drawdown as filled area
    ax.fill_between(
        drawdown.index,
        drawdown.values,
        0,
        color='#E74C3C',
        alpha=0.5,
        label='Drawdown'
    )

    ax.plot(
        drawdown.index,
        drawdown.values,
        linewidth=0.5,
        color='#C0392B'
    )

    # Format
    ax.set_title('Portfolio Drawdown', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Drawdown (%)')

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)

    # Add max drawdown annotation
    min_dd_idx = drawdown.idxmin()
    min_dd = drawdown.min()
    ax.annotate(
        f'Max DD: {min_dd:.1f}%',
        xy=(min_dd_idx, min_dd),
        xytext=(min_dd_idx, min_dd - 5),
        fontsize=10,
        ha='center',
        arrowprops=dict(arrowstyle='->', color='black')
    )

    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'drawdown.png', dpi=150)

    if show_plots:
        plt.show()
    plt.close()


def _plot_monthly_returns(
    result,
    output_dir: Path,
    show_plots: bool
) -> None:
    """Plot monthly returns heatmap"""
    if result.equity_curve.empty:
        return

    # Calculate monthly returns
    monthly = result.equity_curve.resample('ME').last()
    monthly_returns = monthly.pct_change().dropna() * 100

    if monthly_returns.empty:
        return

    # Create DataFrame for heatmap
    monthly_df = monthly_returns.to_frame('return')
    monthly_df['year'] = monthly_df.index.year
    monthly_df['month'] = monthly_df.index.month

    # Pivot for heatmap
    try:
        pivot = monthly_df.pivot(index='year', columns='month', values='return')
    except ValueError:
        logger.warning("Could not create monthly returns heatmap")
        return

    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 6))

    # Color scale
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(vmin=-20, vmax=20)

    # Plot heatmap
    im = ax.imshow(pivot.values, cmap=cmap, norm=norm, aspect='auto')

    # Set ticks
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([month_names[m - 1] for m in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    # Add text annotations
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            if pd.notna(value):
                text_color = 'white' if abs(value) > 10 else 'black'
                ax.text(j, i, f'{value:.1f}%', ha='center', va='center',
                        color=text_color, fontsize=9)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Return (%)')

    ax.set_title('Monthly Returns Heatmap', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')

    plt.tight_layout()
    plt.savefig(output_dir / 'monthly_returns.png', dpi=150)

    if show_plots:
        plt.show()
    plt.close()


def _plot_trade_distribution(
    result,
    output_dir: Path,
    show_plots: bool
) -> None:
    """Plot trade P&L distribution"""
    if not result.trades:
        return

    pnl_pcts = [t.pnl_pct * 100 for t in result.trades]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    ax1 = axes[0]
    winners = [p for p in pnl_pcts if p > 0]
    losers = [p for p in pnl_pcts if p <= 0]

    ax1.hist(winners, bins=20, color='#27AE60', alpha=0.7, label='Winners')
    ax1.hist(losers, bins=20, color='#E74C3C', alpha=0.7, label='Losers')

    ax1.axvline(x=0, color='black', linestyle='--', linewidth=1)
    ax1.set_title('Trade P&L Distribution', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Return (%)')
    ax1.set_ylabel('Number of Trades')
    ax1.legend()

    # Scatter plot by date
    ax2 = axes[1]
    dates = [t.entry_date for t in result.trades if t.entry_date]
    pnls = [t.pnl_pct * 100 for t in result.trades if t.entry_date]

    colors = ['#27AE60' if p > 0 else '#E74C3C' for p in pnls]
    ax2.scatter(dates, pnls, c=colors, alpha=0.6, s=30)

    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax2.set_title('Trade Returns Over Time', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Entry Date')
    ax2.set_ylabel('Return (%)')

    # Format x-axis
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(output_dir / 'trade_distribution.png', dpi=150)

    if show_plots:
        plt.show()
    plt.close()


def generate_html_report(
    result,
    output_path: Path,
    start_date: str,
    end_date: str
) -> None:
    """
    Generate an HTML report with embedded charts.

    Args:
        result: BacktestResult object
        output_path: Path to save HTML report
        start_date: Backtest start date
        end_date: Backtest end date
    """
    from backtest.performance import calculate_cagr, calculate_win_loss_stats

    years = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days / 365.25
    cagr = calculate_cagr(result.initial_capital, result.final_capital, years)
    stats = calculate_win_loss_stats(result.trades)

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backtest Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2C3E50; }}
            .summary {{ background: #ECF0F1; padding: 20px; border-radius: 5px; }}
            .metric {{ margin: 10px 0; }}
            .metric-label {{ font-weight: bold; color: #7F8C8D; }}
            .metric-value {{ font-size: 1.2em; color: #2C3E50; }}
            .positive {{ color: #27AE60; }}
            .negative {{ color: #E74C3C; }}
            .charts {{ margin-top: 20px; }}
            .chart {{ margin: 20px 0; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <h1>Backtest Report</h1>
        <p>Period: {start_date} to {end_date}</p>

        <div class="summary">
            <h2>Performance Summary</h2>
            <div class="metric">
                <span class="metric-label">Initial Capital:</span>
                <span class="metric-value">${result.initial_capital:,.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Final Capital:</span>
                <span class="metric-value">${result.final_capital:,.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Return:</span>
                <span class="metric-value {'positive' if result.total_return_pct > 0 else 'negative'}">
                    {result.total_return_pct:+.1%}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">CAGR:</span>
                <span class="metric-value">{cagr:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Max Drawdown:</span>
                <span class="metric-value negative">{result.max_drawdown_pct:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Sharpe Ratio:</span>
                <span class="metric-value">{result.sharpe_ratio:.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Win Rate:</span>
                <span class="metric-value">{stats['win_rate']:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Trades:</span>
                <span class="metric-value">{stats['total_trades']}</span>
            </div>
        </div>

        <div class="charts">
            <h2>Charts</h2>
            <div class="chart">
                <h3>Equity Curve</h3>
                <img src="equity_curve.png" alt="Equity Curve">
            </div>
            <div class="chart">
                <h3>Drawdown</h3>
                <img src="drawdown.png" alt="Drawdown">
            </div>
            <div class="chart">
                <h3>Monthly Returns</h3>
                <img src="monthly_returns.png" alt="Monthly Returns">
            </div>
            <div class="chart">
                <h3>Trade Distribution</h3>
                <img src="trade_distribution.png" alt="Trade Distribution">
            </div>
        </div>
    </body>
    </html>
    """

    with open(output_path, 'w') as f:
        f.write(html_template)

    logger.info(f"HTML report saved to: {output_path}")
