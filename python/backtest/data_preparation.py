from __future__ import annotations

from typing import Dict, Iterable

import pandas as pd
from loguru import logger as default_logger
from tqdm import tqdm

from analysis.indicators import calculate_all_indicators


def prepare_backtest_data(
    fetcher,
    tickers: Iterable[str],
    benchmark_data: pd.DataFrame | None,
    diagnostics: dict,
    period: str = '5y',
    logger=default_logger,
) -> Dict[str, pd.DataFrame]:
    logger.info('\n' + '=' * 60)
    logger.info('DATA FETCHING')
    logger.info('=' * 60)

    tickers = list(tickers)
    diagnostics['stage2_universe_size'] = len(tickers)
    logger.info(f"Stage2 input tickers: {diagnostics['stage2_universe_size']}")
    logger.info('Fetching historical data...')

    prepared: Dict[str, pd.DataFrame] = {}
    for ticker in tqdm(tickers, desc='Loading ticker data', unit='ticker'):
        data = fetcher.fetch_data(ticker, period=period)
        if data is None or len(data) <= 252:
            continue

        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)

        prepared[ticker] = calculate_all_indicators(data, benchmark_data)

    diagnostics['data_fetch_success_count'] = len(prepared)
    diagnostics['data_fetch_filtered_count'] = len(tickers) - len(prepared)

    logger.info(f"After data fetch:     {diagnostics['data_fetch_success_count']}")
    logger.info(f"Filtered out:         {diagnostics['data_fetch_filtered_count']}")
    return prepared
