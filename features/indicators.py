"""
Technical Indicators Engine

Vectorized computation of technical indicators using pandas.
All indicators are production-grade and deterministic.
"""

import pandas as pd
import numpy as np
from typing import Tuple


def log_returns(close: pd.Series) -> pd.Series:
    """
    Compute log returns.
    
    Args:
        close: Close price series
    
    Returns:
        Log returns series
    """
    return pd.Series(np.log(close / close.shift(1)))


def exponential_moving_average(close: pd.Series, period: int) -> pd.Series:
    """
    Compute EMA (Exponential Moving Average).
    
    Args:
        close: Close price series
        period: EMA period
    
    Returns:
        EMA series
    """
    return close.ewm(span=period, adjust=False).mean()


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """
    Compute True Range (building block for ATR).
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
    
    Returns:
        True range series
    """
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)


def average_true_range(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Compute ATR (Average True Range).
    
    Uses Wilder's smoothing method.
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: ATR period (default 14)
    
    Returns:
        ATR series
    """
    tr = true_range(high, low, close)
    
    # Wilder's smoothing
    atr = pd.Series(index=tr.index, dtype=float)
    atr.iloc[period-1] = tr.iloc[:period].mean()
    
    for i in range(period, len(tr)):
        atr.iloc[i] = (atr.iloc[i-1] * (period - 1) + tr.iloc[i]) / period
    
    return atr


def directional_movement(high: pd.Series, low: pd.Series, period: int = 14) -> Tuple[pd.Series, pd.Series]:
    """
    Compute positive and negative directional movement.
    
    Args:
        high: High price series
        low: Low price series
        period: Period (default 14)
    
    Returns:
        Tuple of (+DM, -DM) series
    """
    high_diff = high.diff()
    low_diff = -low.diff()
    
    pos_dm = pd.Series(0.0, index=high.index)
    neg_dm = pd.Series(0.0, index=high.index)
    
    pos_dm[(high_diff > low_diff) & (high_diff > 0)] = high_diff
    neg_dm[(low_diff > high_diff) & (low_diff > 0)] = low_diff
    
    return pos_dm, neg_dm


def average_directional_index(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Compute ADX (Average Directional Index) - trend strength indicator.
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: ADX period (default 14)
    
    Returns:
        ADX series (0-100)
    """
    pos_dm, neg_dm = directional_movement(high, low, period)
    atr_val = average_true_range(high, low, close, period)
    
    # Directional indicators
    pos_di = 100 * pos_dm.ewm(span=period, adjust=False).mean() / atr_val
    neg_di = 100 * neg_dm.ewm(span=period, adjust=False).mean() / atr_val
    
    # DX
    di_sum = pos_di + neg_di
    di_diff = (pos_di - neg_di).abs()
    dx = 100 * di_diff / di_sum
    
    # ADX (smoothed DX)
    adx = dx.ewm(span=period, adjust=False).mean()
    
    return adx


def relative_strength_index(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Compute RSI (Relative Strength Index).
    
    Args:
        close: Close price series
        period: RSI period (default 14)
    
    Returns:
        RSI series (0-100)
    """
    delta = close.diff()
    
    gain = (delta.where(delta > 0, 0)).ewm(span=period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=period, adjust=False).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def rolling_percentile(series: pd.Series, period: int = 252) -> pd.Series:
    """
    Compute percentile rank within rolling window.
    
    Args:
        series: Input series
        period: Rolling window period
    
    Returns:
        Percentile rank (0-1)
    """
    def percentile_rank(x):
        return (x[-1] > x[:-1]).mean()
    
    return series.rolling(window=period).apply(percentile_rank, raw=True)


def volatility_percentile(volume: pd.Series, close: pd.Series, period: int = 20, lookback: int = 252) -> pd.Series:
    """
    Compute volatility percentile.
    
    Ranks recent volatility against 1-year history.
    
    Args:
        volume: Volume series
        close: Close price series
        period: Volatility calculation period
        lookback: Historical comparison period
    
    Returns:
        Volatility percentile (0-1)
    """
    returns = log_returns(close)
    rolling_vol = returns.rolling(window=period).std()
    vol_pct = rolling_percentile(rolling_vol, lookback)
    
    return vol_pct


def volume_profile(volume: pd.Series, period: int = 20) -> pd.Series:
    """
    Compute volume z-score.
    
    Measures if recent volume is above/below average.
    
    Args:
        volume: Volume series
        period: Moving average period
    
    Returns:
        Volume z-score
    """
    vol_ma = volume.rolling(window=period).mean()
    vol_std = volume.rolling(window=period).std()
    
    zscore = (volume - vol_ma) / vol_std
    
    return zscore


def price_momentum(close: pd.Series, period: int = 20) -> pd.Series:
    """
    Compute price momentum (% change over period).
    
    Args:
        close: Close price series
        period: Momentum period
    
    Returns:
        Momentum as percentage
    """
    return ((close / close.shift(period)) - 1) * 100


def volatility_expansion(close: pd.Series, atr: pd.Series, period: int = 20) -> pd.Series:
    """
    Compute volatility expansion ratio.
    
    Compares current ATR to recent average.
    
    Args:
        close: Close price series
        atr: ATR series
        period: Comparison period
    
    Returns:
        Expansion ratio (1.0 = baseline, >1 = expansion)
    """
    atr_avg = atr.rolling(window=period).mean()
    expansion = atr / atr_avg
    
    return expansion
