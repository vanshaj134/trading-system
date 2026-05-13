"""
Market Data Ingestion

Provides market data loading utilities for the trading system.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def load_prices(symbol: str) -> Dict[str, Any]:
    """
    Load price data for a symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS', 'DEMO')
    
    Returns:
        Dictionary with OHLCV data and metadata
    """
    if symbol == "DEMO":
        # Generate demo data for testing
        dates = pd.date_range(end=datetime.now(), periods=252)
        prices = 100 + np.cumsum(np.random.randn(252) * 0.5)
        
        return {
            'symbol': symbol,
            'dates': dates.tolist(),
            'closes': prices.tolist(),
            'opens': prices.tolist(),
            'highs': (prices + np.abs(np.random.randn(252) * 0.2)).tolist(),
            'lows': (prices - np.abs(np.random.randn(252) * 0.2)).tolist(),
            'volumes': (1000000 + np.random.randint(-500000, 500000, 252)).tolist(),
            'timestamp': datetime.now().isoformat()
        }
    
    # For real symbols, would load from data lake
    # For now, return demo data
    return {
        'symbol': symbol,
        'dates': [],
        'closes': [],
        'timestamp': datetime.now().isoformat()
    }


def get_latest_price(symbol: str) -> Optional[float]:
    """Get the latest price for a symbol."""
    prices = load_prices(symbol)
    if prices.get('closes'):
        return prices['closes'][-1]
    return None
