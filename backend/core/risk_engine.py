"""
Risk Engine

Manages position sizing and risk scaling.
"""

from typing import Dict, Any


def scale_position(signal: Dict[str, Any], risk_budget: float = 1.0) -> Dict[str, Any]:
    """
    Scale position size based on signal and risk budget.
    
    Args:
        signal: Signal dictionary
        risk_budget: Available risk budget (0-1)
    
    Returns:
        Position dictionary with size and exposure
    """
    confidence = signal.get('confidence', 0.0)
    momentum = signal.get('signal', 0.0)
    
    # Position size = confidence * risk_budget * abs(momentum)
    position_size = abs(confidence * risk_budget * momentum) if momentum != 0 else 0.0
    
    return {
        'symbol': signal.get('symbol', 'UNKNOWN'),
        'direction': signal.get('direction', 'NEUTRAL'),
        'size': max(0.0, min(position_size, risk_budget)),
        'confidence': confidence,
        'leverage': 1.0
    }


def validate_risk_limits(positions: Dict[str, Dict], equity: float) -> bool:
    """
    Validate that positions respect risk limits.
    
    Args:
        positions: Position dictionary
        equity: Current equity
    
    Returns:
        True if within limits, False otherwise
    """
    total_exposure = sum(p.get('size', 0.0) for p in positions.values())
    return total_exposure <= equity
