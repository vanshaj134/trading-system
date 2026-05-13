"""
Feature Engine

Converts raw OHLCV data into structured feature matrix.
Produces daily feature snapshot for each stock.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

from features.indicators import (
    log_returns,
    exponential_moving_average,
    average_true_range,
    average_directional_index,
    relative_strength_index,
    volatility_percentile,
    volume_profile,
    price_momentum,
    volatility_expansion
)

logger = logging.getLogger(__name__)


class FeatureEngine:
    """
    Production-grade feature computation for equity analysis.
    """
    
    def __init__(self, min_records: int = 252):
        """
        Initialize feature engine.
        
        Args:
            min_records: Minimum trading days required to compute features
        """
        self.min_records = min_records
    
    
    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute complete feature set for a stock.
        
        Args:
            df: DataFrame with columns [date, symbol, Open, High, Low, Close, Volume]
        
        Returns:
            DataFrame with computed features
        """
        if len(df) < self.min_records:
            logger.warning(f"{df['symbol'].iloc[0]}: Only {len(df)} records, need {self.min_records}")
            return pd.DataFrame()
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Basic fields
        result = df[['date', 'symbol', 'Close', 'Volume']].copy()
        
        # Returns
        result['returns_pct'] = log_returns(df['Close']) * 100
        
        # Moving averages (trend)
        result['ema20'] = exponential_moving_average(df['Close'], 20)
        result['ema50'] = exponential_moving_average(df['Close'], 50)
        result['ema200'] = exponential_moving_average(df['Close'], 200)
        
        # Volatility indicators
        result['atr'] = average_true_range(df['High'], df['Low'], df['Close'], 14)
        result['atr_pct'] = (result['atr'] / df['Close']) * 100
        
        # Trend strength
        result['adx'] = average_directional_index(df['High'], df['Low'], df['Close'], 14)
        
        # Momentum
        result['rsi'] = relative_strength_index(df['Close'], 14)
        result['momentum'] = price_momentum(df['Close'], 20)
        
        # Volume analysis
        result['volume_zscore'] = volume_profile(df['Volume'], 20)
        result['vol_percentile'] = volatility_percentile(df['Volume'], df['Close'], 20, 252)
        
        # Volatility structure
        result['vol_expansion'] = volatility_expansion(df['Close'], result['atr'], 20)
        
        # Depth: high-low ratio (volatility within day)
        result['intraday_range_pct'] = ((df['High'] - df['Low']) / df['Close']) * 100
        
        # Drop NaN rows (first 252 days don't have all indicators)
        result = result.dropna()
        
        return result
    
    
    def get_latest_features(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Get latest day's feature snapshot.
        
        Args:
            df: Computed features DataFrame
        
        Returns:
            Dictionary of features for latest date, or None
        """
        if df.empty:
            return None
        
        latest = df.iloc[-1]
        
        return {
            'date': latest['date'],
            'symbol': latest['symbol'],
            'close': float(latest['Close']),
            'returns_pct': float(latest['returns_pct']),
            'ema20': float(latest['ema20']),
            'ema50': float(latest['ema50']),
            'ema200': float(latest['ema200']),
            'atr': float(latest['atr']),
            'atr_pct': float(latest['atr_pct']),
            'adx': float(latest['adx']),
            'rsi': float(latest['rsi']),
            'momentum': float(latest['momentum']),
            'volume_zscore': float(latest['volume_zscore']),
            'vol_percentile': float(latest['vol_percentile']),
            'vol_expansion': float(latest['vol_expansion']),
            'intraday_range_pct': float(latest['intraday_range_pct']),
        }
    
    
    @staticmethod
    def feature_summary(features: Dict) -> str:
        """
        Create human-readable summary of features.
        
        Args:
            features: Feature dictionary
        
        Returns:
            Formatted string
        """
        if not features:
            return "No features available"
        
        lines = [
            f"{features['symbol']} ({features['date']})",
            f"Close: {features['close']:.2f}",
            f"Returns: {features['returns_pct']:.2f}%",
            f"Trend (EMA): 20={features['ema20']:.2f} 50={features['ema50']:.2f} 200={features['ema200']:.2f}",
            f"Volatility: ATR={features['atr']:.2f} ({features['atr_pct']:.2f}%) | Expansion={features['vol_expansion']:.2f}x",
            f"Trend Strength: ADX={features['adx']:.1f}",
            f"Momentum: RSI={features['rsi']:.1f} | {features['momentum']:.2f}%",
            f"Volume: Z-score={features['volume_zscore']:.2f} | %ile={features['vol_percentile']:.2f}",
        ]
        
        return "\n".join(lines)
