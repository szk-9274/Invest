"""
Technical indicators calculation module
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


def calculate_sma(data: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
    """
    Calculate Simple Moving Averages (SMA).

    Args:
        data: Stock price data
        periods: List of periods (e.g., [50, 150, 200])

    Returns:
        DataFrame with SMA columns added
    """
    result = data.copy()

    for period in periods:
        col_name = f'sma_{period}'
        result[col_name] = result['close'].rolling(window=period).mean()

    return result


def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).

    Args:
        data: Stock price data
        period: EMA period

    Returns:
        EMA Series
    """
    return data['close'].ewm(span=period, adjust=False).mean()


def calculate_52w_high_low(data: pd.DataFrame) -> Tuple[float, float]:
    """
    Calculate 52-week high and low.

    Args:
        data: Stock price data (minimum 252 trading days required)

    Returns:
        (52-week high, 52-week low)
    """
    lookback = min(252, len(data))  # 252 trading days = ~52 weeks

    high_52w = data['high'].tail(lookback).max()
    low_52w = data['low'].tail(lookback).min()

    return high_52w, low_52w


def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).

    Args:
        data: Stock price data
        period: ATR period (default 14)

    Returns:
        ATR Series
    """
    high = data['high']
    low = data['low']
    close = data['close']

    # True Range calculation
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # ATR = Moving average of True Range
    atr = true_range.rolling(window=period).mean()

    return atr


def calculate_rs_line(
    stock_data: pd.DataFrame,
    benchmark_data: pd.DataFrame
) -> pd.Series:
    """
    Calculate Relative Strength (RS) Line.

    RS = Stock Price / Benchmark Price

    Args:
        stock_data: Individual stock data
        benchmark_data: Benchmark (e.g., S&P 500) data

    Returns:
        RS Line Series
    """
    # Align indices
    common_index = stock_data.index.intersection(benchmark_data.index)

    if len(common_index) == 0:
        return pd.Series(dtype=float)

    stock_close = stock_data.loc[common_index, 'close']
    bench_close = benchmark_data.loc[common_index, 'close']

    rs_line = stock_close / bench_close

    return rs_line


def is_rs_new_high(rs_line: pd.Series, window: int = 252) -> bool:
    """
    Check if RS Line is making a new 52-week high.

    Args:
        rs_line: RS Line Series
        window: Lookback period (default 252 trading days)

    Returns:
        True: New high confirmed
        False: Not at new high
    """
    if len(rs_line) < window:
        return False

    recent_high = rs_line.tail(window).max()
    current_value = rs_line.iloc[-1]

    # Consider within 5% of high as "at new high"
    return current_value >= recent_high * 0.95


def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0
) -> Dict[str, pd.Series]:
    """
    Calculate Bollinger Bands.

    Args:
        data: Stock price data
        period: SMA period (default 20)
        std_dev: Standard deviation multiplier (default 2.0)

    Returns:
        {'middle': SMA, 'upper': Upper band, 'lower': Lower band}
    """
    middle = data['close'].rolling(window=period).mean()
    std = data['close'].rolling(window=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return {
        'middle': middle,
        'upper': upper,
        'lower': lower
    }


def calculate_volume_ma(data: pd.DataFrame, period: int) -> pd.Series:
    """
    Calculate Volume Moving Average.

    Args:
        data: Stock price data
        period: MA period

    Returns:
        Volume MA Series
    """
    return data['volume'].rolling(window=period).mean()


def calculate_daily_return(data: pd.DataFrame) -> pd.Series:
    """
    Calculate daily percentage return.

    Args:
        data: Stock price data

    Returns:
        Daily return Series
    """
    return data['close'].pct_change()


def calculate_volatility(data: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Calculate rolling volatility (standard deviation of returns).

    Args:
        data: Stock price data
        period: Rolling window period

    Returns:
        Volatility Series
    """
    returns = calculate_daily_return(data)
    return returns.rolling(window=period).std()


def calculate_all_indicators(
    data: pd.DataFrame,
    benchmark_data: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Calculate all technical indicators.

    Args:
        data: Stock price data
        benchmark_data: Benchmark data (optional; if None, RS line is not calculated)

    Returns:
        DataFrame with all indicators
    """
    result = data.copy()

    # Moving Averages
    result = calculate_sma(result, [50, 150, 200])
    result['ema_21'] = calculate_ema(result, 21)

    # ATR
    result['atr_14'] = calculate_atr(result, 14)

    # RS Line (only if benchmark data is provided)
    if benchmark_data is not None:
        result['rs_line'] = calculate_rs_line(result, benchmark_data)
    else:
        result['rs_line'] = pd.Series(dtype=float, index=result.index)

    # Bollinger Bands
    bb = calculate_bollinger_bands(result)
    result['bb_middle'] = bb['middle']
    result['bb_upper'] = bb['upper']
    result['bb_lower'] = bb['lower']

    # Volume MAs
    result['volume_ma_10'] = calculate_volume_ma(result, 10)
    result['volume_ma_50'] = calculate_volume_ma(result, 50)

    # Daily returns and volatility
    result['daily_return'] = calculate_daily_return(result)
    result['volatility_20'] = calculate_volatility(result, 20)

    return result
