"""
Edge Ranker & Scorer

Converts feature vectors into composite edge scores.
Ranks stocks by trading opportunity quality.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class EdgeRanker:
    """
    Composite edge scoring system.
    
    Combines multiple feature signals into single edge score (0-100).
    """
    
    def __init__(self):
        """Initialize edge ranker with scoring weights."""
        self.weights = {
            'trend_strength': 0.25,        # ADX-based trend
            'volatility_expansion': 0.20,  # ATR expansion
            'momentum': 0.20,               # RSI + price momentum
            'volume_quality': 0.15,         # Volume z-score
            'risk_efficiency': 0.20,        # Reward/risk ratio
        }
    
    
    def score_trend_strength(self, features: Dict) -> float:
        """
        Score trend strength (0-100).
        
        Based on ADX: 0-25 weak, 25-50 moderate, 50+ strong.
        """
        adx = features['adx']
        
        if adx < 20:
            return 20  # Weak trend
        elif adx < 30:
            return 50  # Moderate
        elif adx < 50:
            return 75  # Strong
        else:
            return 95  # Very strong
    
    
    def score_volatility_expansion(self, features: Dict) -> float:
        """
        Score volatility expansion (0-100).
        
        Favors expanding volatility (ATR rising).
        """
        expansion = features['vol_expansion']
        
        if expansion < 0.8:
            return 20  # Contracting
        elif expansion < 1.0:
            return 40  # Baseline
        elif expansion < 1.2:
            return 60  # Mild expansion
        elif expansion < 1.5:
            return 80  # Good expansion
        else:
            return 95  # Strong expansion
    
    
    def score_momentum(self, features: Dict) -> float:
        """
        Score momentum (0-100).
        
        Based on RSI + price momentum combined.
        """
        rsi = features['rsi']
        momentum = features['momentum']
        
        # RSI scoring
        if rsi < 30 or rsi > 70:
            rsi_score = 30  # Extreme
        elif rsi < 40 or rsi > 60:
            rsi_score = 60  # Intermediate
        else:
            rsi_score = 40  # Neutral
        
        # Momentum scoring (strong if >0)
        if momentum > 5:
            momentum_score = 85
        elif momentum > 0:
            momentum_score = 60
        elif momentum > -5:
            momentum_score = 40
        else:
            momentum_score = 20
        
        # Combined
        return 0.5 * rsi_score + 0.5 * momentum_score
    
    
    def score_volume_quality(self, features: Dict) -> float:
        """
        Score volume quality (0-100).
        
        Favors above-average volume.
        """
        zscore = features['volume_zscore']
        percentile = features['vol_percentile']
        
        # High volume good
        if zscore > 2:
            zscore_score = 90
        elif zscore > 1:
            zscore_score = 75
        elif zscore > 0:
            zscore_score = 60
        else:
            zscore_score = 30
        
        # Use percentile as secondary
        if percentile > 0.75:
            percentile_score = 80
        elif percentile > 0.5:
            percentile_score = 60
        else:
            percentile_score = 40
        
        return 0.6 * zscore_score + 0.4 * percentile_score
    
    
    def score_risk_efficiency(self, features: Dict) -> float:
        """
        Score risk efficiency (reward/risk ratio).
        
        Intraday range should be reasonable relative to momentum.
        """
        momentum = abs(features['momentum'])
        intraday_range = features['intraday_range_pct']
        
        # Risk efficiency = momentum / range
        if intraday_range > 0:
            efficiency = momentum / intraday_range
        else:
            efficiency = 0
        
        if efficiency > 3:
            return 90  # High reward/risk
        elif efficiency > 1:
            return 70
        elif efficiency > 0.5:
            return 50
        else:
            return 30
    
    
    def compute_edge_score(self, features: Dict) -> float:
        """
        Compute composite edge score (0-100).
        
        Args:
            features: Feature dictionary
        
        Returns:
            Edge score 0-100
        """
        scores = {
            'trend_strength': self.score_trend_strength(features),
            'volatility_expansion': self.score_volatility_expansion(features),
            'momentum': self.score_momentum(features),
            'volume_quality': self.score_volume_quality(features),
            'risk_efficiency': self.score_risk_efficiency(features),
        }
        
        # Weighted composite
        edge_score = sum(scores[key] * self.weights[key] for key in scores)
        
        return edge_score
    
    
    def rank_stocks(self, features_list: List[Dict], top_n: int = 5) -> List[Tuple[str, Dict, float]]:
        """
        Rank stocks by edge score.
        
        Args:
            features_list: List of feature dictionaries
            top_n: Return top N stocks
        
        Returns:
            List of tuples (symbol, features, edge_score) sorted by score descending
        """
        scored = []
        
        for features in features_list:
            if not features:
                continue
            
            score = self.compute_edge_score(features)
            scored.append((features['symbol'], features, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[2], reverse=True)
        
        return scored[:top_n]
    
    
    @staticmethod
    def format_ranking(ranking: List[Tuple[str, Dict, float]]) -> str:
        """
        Format ranking for display.
        
        Args:
            ranking: Ranked list from rank_stocks()
        
        Returns:
            Formatted string
        """
        lines = ["EDGE RANKING", "=" * 60]
        
        for rank, (symbol, features, score) in enumerate(ranking, 1):
            lines.append(f"\n#{rank} | {symbol} | Edge Score: {score:.1f}/100")
            lines.append(f"  Price: {features['close']:.2f} | ADX: {features['adx']:.1f} | RSI: {features['rsi']:.1f}")
            lines.append(f"  Momentum: {features['momentum']:.2f}% | Vol Expansion: {features['vol_expansion']:.2f}x")
            lines.append(f"  Volume Z-score: {features['volume_zscore']:.2f}")
        
        return "\n".join(lines)
