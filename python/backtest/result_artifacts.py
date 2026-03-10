from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from backtest.ticker_analysis import TickerAnalysis


def save_trade_records(trades: list[Any], output_dir: str | Path) -> Path | None:
    if not trades:
        return None

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    trades_df = pd.DataFrame(
        [
            {
                'ticker': trade.ticker,
                'entry_date': trade.entry_date.strftime('%Y-%m-%d') if trade.entry_date else None,
                'entry_price': round(trade.entry_price, 2),
                'exit_date': trade.exit_date.strftime('%Y-%m-%d') if trade.exit_date else None,
                'exit_price': round(trade.exit_price, 2) if trade.exit_price else None,
                'exit_reason': trade.exit_reason,
                'shares': trade.shares,
                'pnl': round(trade.pnl, 2),
                'pnl_pct': round(trade.pnl_pct * 100, 2),
            }
            for trade in trades
        ]
    )
    trades_path = output_path / 'trades.csv'
    trades_df.to_csv(trades_path, index=False)
    logger.info(f'Results saved to: {trades_path}')
    return trades_path


def persist_trade_artifacts(trade_logger) -> dict[str, str | None]:
    trade_log_path = trade_logger.save()
    logger.info(f'Trade log saved to: {trade_log_path}')

    ticker_analyzer = TickerAnalysis(output_dir=trade_logger.output_dir)
    ticker_analyzer.analyze(trade_logger.entries)
    ticker_stats_path = ticker_analyzer.save()
    logger.info(f'Ticker stats saved to: {ticker_stats_path}')
    ticker_analyzer.print_summary()

    return {
        'trade_log_csv': trade_log_path,
        'ticker_stats_csv': ticker_stats_path,
    }
