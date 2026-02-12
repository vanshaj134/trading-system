"""
Regime Detection

Detects market regimes and evaluates system confidence.
"""

from typing import Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime


class RegimeType(Enum):
    """Market regime types."""
    TRENDING = "TRENDING"
    MEAN_REVERT = "MEAN_REVERT"
    HIGH_VOL = "HIGH_VOL"
    CHOPPY = "CHOPPY"
    UNKNOWN = "UNKNOWN"


class RegimeDetector:
    """
    Detects current market regime based on technical indicators.
    """
    
    def __init__(self):
        """Initialize regime detector."""
        self.current_regime = RegimeType.UNKNOWN
        self.regime_history: Dict[str, RegimeType] = {}
    
    def detect_regime(self, 
                     prices: Dict[str, Any], 
                     volumes: Dict[str, Any]) -> Tuple[RegimeType, float]:
        """
        Detect current market regime.
        
        Args:
            prices: Price data
            volumes: Volume data
        
        Returns:
            Tuple of (Regime, confidence)
        """
        # Simple heuristic-based detection
        if not prices or not volumes:
            return RegimeType.UNKNOWN, 0.0
        
        # Dummy implementation: randomly assign based on price movement
        closes = prices.get('closes', [])
        if len(closes) < 20:
            return RegimeType.UNKNOWN, 0.3
        
        recent_change = (closes[-1] - closes[-20]) / closes[-20]
        
        if abs(recent_change) > 0.05:
            regime = RegimeType.TRENDING
            confidence = min(0.9, 0.5 + abs(recent_change) * 5)
        elif abs(recent_change) < 0.01:
            regime = RegimeType.CHOPPY
            confidence = 0.6
        else:
            regime = RegimeType.MEAN_REVERT
            confidence = 0.5
        
        self.current_regime = regime
        return regime, confidence
    
    def get_current_regime(self) -> RegimeType:
        """Get current detected regime."""
        return self.current_regime
    
    def record_regime(self, symbol: str, regime: RegimeType):
        """Record regime for a specific symbol."""
        self.regime_history[symbol] = regime


class ConfidenceScorer:
    """
    Evaluates system confidence in its own signals and positions.
    
    Not market confidence, but epistemic confidence: how much do we trust our analysis?
    """
    
    def __init__(self):
        """Initialize confidence scorer."""
        self.scores: Dict[str, float] = {}
    
    def score_signal_confidence(self, 
                               signal_strength: float,
                               data_points: int,
                               regime_fit: float) -> float:
        """
        Score confidence in a signal.
        
        Higher score = higher confidence this signal is reliable.
        Not market confidence, but epistemic: is our signal methodology working?
        
        Args:
            signal_strength: Raw signal magnitude
            data_points: Number of data points used
            regime_fit: How well signal fits current regime (0-1)
        
        Returns:
            Confidence score (0-1)
        """
        # Less data = less confidence
        data_confidence = min(data_points / 252, 1.0)  # 1 year = full confidence
        
        # Signal strength reflects agreement (magnitude = consensus)
        signal_confidence = min(abs(signal_strength) / 2.0, 1.0)
        
        # Regime fit shows if signal makes sense in context
        regime_confidence = regime_fit
        
        # Combined score (average with weights)
        confidence = (
            0.3 * data_confidence +
            0.4 * signal_confidence +
            0.3 * regime_confidence
        )
        
        return confidence
    
    def score_position_confidence(self,
                                 position_size: float,
                                 drawdown: float,
                                 volatility: float) -> float:
        """
        Score confidence in a position.
        
        Args:
            position_size: Position size as % of capital
            drawdown: Current drawdown
            volatility: Portfolio volatility
        
        Returns:
            Confidence score (0-1)
        """
        # Size confidence: smaller positions = more confident
        size_confidence = 1.0 - min(abs(position_size), 1.0)
        
        # Drawdown confidence: less drawdown = more confident
        drawdown_confidence = max(0.0, 1.0 - drawdown * 10)
        
        # Volatility confidence: lower vol = more confident
        vol_confidence = max(0.0, 1.0 - volatility * 5)
        
        confidence = (
            0.5 * size_confidence +
            0.3 * drawdown_confidence +
            0.2 * vol_confidence
        )
        
        return confidence
    
    def record_score(self, symbol: str, score: float):
        """Record confidence score for a symbol."""
        self.scores[symbol] = score
    
    def get_scores(self) -> Dict[str, float]:
        """Get all recorded scores."""
        return self.scores
