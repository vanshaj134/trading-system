# backend/core/portfolio_optimizer.py

from typing import Dict

class PortfolioOptimizer:
    def __init__(
        self,
        risk_budget: float,
        gross_exposure_limit: float,
        instrument_cap: float,
    ):
        self.risk_budget = risk_budget
        self.gross_exposure_limit = gross_exposure_limit
        self.instrument_cap = instrument_cap

    def allocate(
        self,
        signals: Dict[str, float],
        volatilities: Dict[str, float],
        prices: Dict[str, float],
        account_equity: float,
    ) -> Dict[str, float]:
        """
        Returns target dollar positions per instrument.
        Deterministic. Bounded. Capital-safe.
        """

        raw_positions = {}

        for symbol, weight in signals.items():
            vol = volatilities.get(symbol)
            price = prices.get(symbol)

            if vol is None or vol <= 0:
                raw_positions[symbol] = 0.0
                continue

            raw_positions[symbol] = (
                account_equity
                * self.risk_budget
                * weight
                / vol
            )

        # Apply per-instrument cap
        capped_positions = {}
        cap_value = self.instrument_cap * account_equity

        for symbol, pos in raw_positions.items():
            capped_positions[symbol] = max(
                -cap_value,
                min(cap_value, pos)
            )

        # Enforce gross exposure
        gross_exposure = sum(abs(p) for p in capped_positions.values())
        max_gross = self.gross_exposure_limit * account_equity

        if gross_exposure > max_gross and gross_exposure > 0:
            scale = max_gross / gross_exposure
            for symbol in capped_positions:
                capped_positions[symbol] *= scale

        return capped_positions


def optimize(positions: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Optimize portfolio allocation.
    
    Args:
        positions: Position dictionary
    
    Returns:
        Optimized position targets
    """
    if not positions:
        return {}
    
    # Simple optimization: scale by confidence
    total_confidence = sum(p.get('confidence', 0.0) for p in positions.values())
    
    if total_confidence == 0:
        return {symbol: {'target': 0.0, 'weight': 0.0} for symbol in positions.keys()}
    
    result = {}
    for symbol, position in positions.items():
        confidence = position.get('confidence', 0.0)
        weight = confidence / total_confidence if total_confidence > 0 else 0.0
        result[symbol] = {
            'target': position.get('size', 0.0) * weight,
            'weight': weight,
            'direction': position.get('direction', 'NEUTRAL')
        }
    
    return result
