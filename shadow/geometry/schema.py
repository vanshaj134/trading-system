# shadow/geometry/schema.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
from uuid import UUID


@dataclass(frozen=True)
class DivergenceVector:
    """Raw geometric disagreement between intent and execution."""
    direction_delta: str  # SAME | FLIP | STALL
    exposure_delta_usd: float  # signed
    fill_ratio_delta: float  # [0, 1]
    latency_delta_ms: int
    price_delta_bps: int


@dataclass(frozen=True)
class DivergenceNorms:
    """Secondary, derived measures of divergence."""
    l1_norm: float
    l_inf_norm: float
    directional_entropy: float  # 0.0 (pure) to 1.0 (chaotic)
    temporal_skew: float  # -1.0 (early) to +1.0 (late)


@dataclass(frozen=True)
class GeometryRecord:
    """Complete geometric snapshot of intent-execution disagreement."""
    run_id: str
    timestamp: str
    
    regime_label: str
    constraint_type: Optional[str]
    
    divergence_vector: DivergenceVector
    divergence_norms: DivergenceNorms
    
    determinism_hash: str
