# shadow/geometry/norms.py
from shadow.geometry.schema import DivergenceNorms
import math


def compute_norms(vector, intent_notional) -> DivergenceNorms:
    """
    Compute derived norms from divergence vector.
    
    No weighting. No scaling. Raw math.
    """
    
    # L1 norm: sum of absolute disagreements
    l1_norm = (
        abs(vector.exposure_delta_usd) / max(intent_notional, 1.0) +
        vector.fill_ratio_delta +
        (vector.latency_delta_ms / 100.0) +
        (vector.price_delta_bps / 100.0)
    )
    
    # L-infinity norm: worst-case stress
    l_inf_norm = max(
        abs(vector.exposure_delta_usd) / max(intent_notional, 1.0),
        vector.fill_ratio_delta,
        vector.latency_delta_ms / 100.0,
        vector.price_delta_bps / 100.0,
    )
    
    # Directional entropy
    # Pure alignment → 0.0
    # Chaotic flipping → 1.0
    direction_score = {
        "SAME": 0.0,
        "STALL": 0.5,
        "FLIP": 1.0,
    }.get(vector.direction_delta, 0.5)
    
    directional_entropy = direction_score
    
    # Temporal skew
    # Early execution (high latency) → negative
    # Late execution → positive
    # Normalized to [-1, 1]
    temporal_skew = (vector.latency_delta_ms - 50.0) / 100.0
    temporal_skew = max(-1.0, min(1.0, temporal_skew))
    
    return DivergenceNorms(
        l1_norm=l1_norm,
        l_inf_norm=l_inf_norm,
        directional_entropy=directional_entropy,
        temporal_skew=temporal_skew,
    )
