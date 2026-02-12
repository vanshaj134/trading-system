"""
Signal Generators

Generates trading signals from market data.
"""

from typing import Dict, Any, List


def generate_signal(prices: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate trading signals from price data.
    
    Args:
        prices: Price data dictionary
    
    Returns:
        Signal dictionary with direction and confidence
    """
    if not prices.get('closes') or len(prices['closes']) < 2:
        return {
            'symbol': prices.get('symbol', 'UNKNOWN'),
            'signal': 0.0,  # No signal
            'confidence': 0.0,
            'direction': 'NEUTRAL'
        }
    
    # Simple momentum signal
    closes = prices['closes']
    momentum = (closes[-1] - closes[-20]) / closes[-20] if len(closes) >= 20 else 0
    
    return {
        'symbol': prices.get('symbol', 'UNKNOWN'),
        'signal': momentum,
        'confidence': 0.5,
        'direction': 'LONG' if momentum > 0 else 'SHORT'
    }


def generate_multiple_signals(price_dict: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Generate signals for multiple symbols.
    
    Args:
        price_dict: Dictionary mapping symbols to price data
    
    Returns:
        Dictionary mapping symbols to signals
    """
    return {symbol: generate_signal(prices) for symbol, prices in price_dict.items()}
