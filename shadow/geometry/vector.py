# shadow/geometry/vector.py
from shadow.geometry.schema import DivergenceVector


def compute_vector(intent, shadow_execution, divergence_record) -> DivergenceVector:
    """
    Compute raw divergence vector from intent and shadow execution.
    
    This function does no thinking. It subtracts.
    """
    
    # Direction delta
    if intent.direction == shadow_execution.executed_direction:
        direction_delta = "SAME"
    elif shadow_execution.executed_direction == "FLAT":
        direction_delta = "STALL"
    else:
        direction_delta = "FLIP"
    
    # Exposure delta (already computed in divergence)
    exposure_delta_usd = divergence_record.exposure_delta_usd
    
    # Fill ratio delta
    fill_ratio_delta = 1.0 - shadow_execution.fill_percentage
    
    # Latency delta (assumed to be the modeled latency)
    latency_delta_ms = shadow_execution.latency_ms
    
    # Price delta (slippage in bps)
    price_delta_bps = shadow_execution.slippage_bps
    
    return DivergenceVector(
        direction_delta=direction_delta,
        exposure_delta_usd=exposure_delta_usd,
        fill_ratio_delta=fill_ratio_delta,
        latency_delta_ms=latency_delta_ms,
        price_delta_bps=price_delta_bps,
    )
