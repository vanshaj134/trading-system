"""
PHASE 3 — COGNITIVE ARCHETYPE CLASSIFICATION

This module assigns exactly ONE archetype to each geometry record.
It does not judge, optimize, or recommend action.

Archetypes describe STRUCTURE and FAILURE MODE RISK.
They exist to prevent self-deception, not to improve returns.

Rule:
- Deterministic
- Total (every record gets exactly one label)
- Honest (explicit STRUCTURAL_BLIND_SPOT when uncertain)
"""

from dataclasses import dataclass
from typing import Optional
from shadow.geometry.schema import GeometryRecord


# ----------------------------
# Archetype Classification Record
# ----------------------------

@dataclass(frozen=True)
class ArchetypeClassification:
    """
    Result of classifying a single geometry record into a cognitive archetype.
    """
    run_id: str
    archetype: str
    confidence: float                # [0.0, 1.0] epistemic confidence, NOT market confidence
    rationale: str                   # Why this archetype
    cognitive_risk: str              # What mistake humans tend to make here
    blind_spot: Optional[str]        # Explicit unknown, if any


# ----------------------------
# Archetype Set (LOCKED)
# ----------------------------

ARCHETYPES = {
    "CLEAN_EXECUTION",              # A1: Intent and execution aligned, low divergence
    "FRAGILE_ALIGNMENT",            # A2: Aligned direction but high variance
    "VOLATILITY_STALL",             # B1: Execution blocked by vol constraints
    "LIQUIDITY_FADE",               # B2: Fill degraded without direction flip
    "LATENCY_SLIP",                 # B3: Direction preserved, price distortion high
    "DIRECTIONAL_FLIP",             # C1: Direction inverted from intent
    "PARTIAL_REALITY",              # C2: Same direction, reduced exposure
    "HARD_BLOCK",                   # D1: Constraint fully blocks execution
    "SOFT_CEILING",                 # D2: Exposure clipped at limit
    "SHAPE_DRIFT",                  # E1: Geometry changing over time
    "REGIME_FRACTURE",              # E2: Inconsistent geometry within regime
    "STRUCTURAL_BLIND_SPOT",        # F1: Unknown, uncertain, honest
}


# ----------------------------
# Deterministic Classification Rules
# ----------------------------

def classify_geometry(g: GeometryRecord) -> ArchetypeClassification:
    """
    Deterministically map geometry record → single archetype.
    
    Order of rules matters. First match wins.
    This ensures determinism and epistemic honesty.
    """

    # ============================================================
    # TIER 1: Constraint-Dominant (Execution Completely Blocked)
    # ============================================================

    # Hard block: execution entirely suppressed by constraint
    if (g.divergence_vector.direction_delta == "STALL" and 
        g.divergence_norms.l_inf_norm >= 0.9 and 
        g.constraint_type is not None):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="HARD_BLOCK",
            confidence=0.95,
            rationale="Execution intent was fully blocked by active constraint under this regime.",
            cognitive_risk="Temptation to override constraints to 'force' execution.",
            blind_spot=None,
        )

    # Volatility stall: high constraint pressure but labeled
    if (g.divergence_vector.direction_delta == "STALL" and 
        g.divergence_norms.l_inf_norm > 0.7 and
        g.constraint_type == "VOLATILITY_GUARD"):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="VOLATILITY_STALL",
            confidence=0.92,
            rationale="Intent is suppressed due to volatility guard constraint.",
            cognitive_risk="Misinterpreting blocked execution as weak signal.",
            blind_spot="Unable to measure what execution would be under relaxed constraints.",
        )

    # ============================================================
    # TIER 2: Clean Execution (Rare, Dangerous)
    # ============================================================

    # Clean alignment: near-zero divergence across all dimensions
    if (g.divergence_norms.l1_norm <= 0.15 and 
        g.divergence_norms.l_inf_norm <= 0.15 and
        g.divergence_vector.direction_delta == "SAME" and
        abs(g.divergence_vector.exposure_delta_usd) < 0.05):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="CLEAN_EXECUTION",
            confidence=0.90,
            rationale="Intent translated to execution with minimal distortion.",
            cognitive_risk="Extreme overconfidence from apparent smoothness.",
            blind_spot="Smoothness may mask regime instability not yet visible in microstructure.",
        )

    # ============================================================
    # TIER 3: Direction Preserved, Size/Timing Friction
    # ============================================================

    # Liquidity fade: same direction, degraded fill
    if (g.divergence_vector.direction_delta == "SAME" and
        g.divergence_vector.fill_ratio_delta > 0.3 and
        g.divergence_norms.l1_norm <= 0.5):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="LIQUIDITY_FADE",
            confidence=0.85,
            rationale="Direction preserved but execution size was reduced by liquidity constraints.",
            cognitive_risk="Assuming partial fills indicate weak conviction rather than structural liquidity.",
            blind_spot="Order book dynamics unavailable; slippage attribution to market vs. algorithm unclear.",
        )

    # Latency slip: direction preserved, price distortion high
    if (g.divergence_vector.direction_delta == "SAME" and
        g.divergence_vector.price_delta_bps > 10 and
        g.divergence_norms.l_inf_norm > 0.4):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="LATENCY_SLIP",
            confidence=0.80,
            rationale="Execution direction held but price execution was significantly distorted.",
            cognitive_risk="Blaming signal logic for microstructure fills.",
            blind_spot="Tick-level execution data unavailable; latency attribution uncertain.",
        )

    # Fragile alignment: same direction but high variance
    if (g.divergence_vector.direction_delta == "SAME" and
        g.divergence_norms.l1_norm <= 0.4 and
        g.divergence_norms.l_inf_norm > 0.5):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="FRAGILE_ALIGNMENT",
            confidence=0.82,
            rationale="Direction stable but execution variance is high; alignment is brittle.",
            cognitive_risk="Over-sizing into apparent momentum.",
            blind_spot="Temporal structure of divergence not fully characterized.",
        )

    # ============================================================
    # TIER 4: Intent Failure
    # ============================================================

    # Directional flip: execution inverted
    if g.divergence_vector.direction_delta == "FLIP":
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="DIRECTIONAL_FLIP",
            confidence=0.88,
            rationale="Execution direction diverged fundamentally from intent.",
            cognitive_risk="Narrative anchoring to original conviction despite execution reversal.",
            blind_spot="Order book imbalance dynamics not observable.",
        )

    # Partial reality: same direction but exposure significantly reduced
    if (g.divergence_vector.direction_delta == "SAME" and
        g.divergence_vector.exposure_delta_usd < -0.2):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="PARTIAL_REALITY",
            confidence=0.80,
            rationale="Direction intent preserved but executed exposure is materially lower.",
            cognitive_risk="Operating with phantom position belief (thinking size matches intent).",
            blind_spot="Execution mechanics uncertain; unclear if due to liquidity, timing, or constraints.",
        )

    # ============================================================
    # TIER 5: Soft Constraints
    # ============================================================

    # Soft ceiling: same direction, exposure clipped at limit
    if (g.divergence_vector.direction_delta == "SAME" and
        0.05 < g.divergence_vector.exposure_delta_usd < 0.3 and
        g.constraint_type == "SIZE_LIMIT"):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="SOFT_CEILING",
            confidence=0.85,
            rationale="Intent direction held, but execution size was capped by position limit.",
            cognitive_risk="Incremental overreach: testing limits repeatedly.",
            blind_spot="Future constraint evolution under stress unknown.",
        )

    # ============================================================
    # TIER 6: Structural Instability
    # ============================================================

    # Shape drift: geometry statistics changing over time
    if g.divergence_norms.temporal_skew != 0.0 and abs(g.divergence_norms.temporal_skew) > 0.5:
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="SHAPE_DRIFT",
            confidence=0.75,
            rationale="Geometry is non-stationary; divergence characteristics shifting over observation window.",
            cognitive_risk="Model staleness blindness; assuming stable relationships across regime boundaries.",
            blind_spot="Regime transition boundaries unclear; drift rate unknown.",
        )

    # Regime fracture: inconsistent geometry within single regime
    if (g.divergence_norms.directional_entropy > 0.6 and
        g.divergence_vector.direction_delta in ["FLIP", "STALL"]):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="REGIME_FRACTURE",
            confidence=0.70,
            rationale="Geometry inconsistent within labeled regime; regime classification questionable.",
            cognitive_risk="False confidence in regime definition.",
            blind_spot="Sub-regime structure undetected; geometry drivers are plural.",
        )

    # ============================================================
    # TIER 7: Low Information (Ambiguous)
    # ============================================================

    # Low information: geometry exists but structure is weak
    if (g.divergence_norms.l1_norm < 0.2 and 
        g.divergence_norms.directional_entropy > 0.5):
        return ArchetypeClassification(
            run_id=g.run_id,
            archetype="STRUCTURAL_BLIND_SPOT",
            confidence=0.45,
            rationale="Geometry present but signal-to-structure ratio is too weak to classify.",
            cognitive_risk="Forcing meaning onto noise.",
            blind_spot="Too much entropy relative to magnitude; structural drivers obscured.",
        )

    # ============================================================
    # TIER 8: Default / Escape Hatch
    # ============================================================

    # Structural blind spot: nothing matched cleanly
    return ArchetypeClassification(
        run_id=g.run_id,
        archetype="STRUCTURAL_BLIND_SPOT",
        confidence=0.35,
        rationale="Geometry does not match any known stable archetype pattern.",
        cognitive_risk="Story-making under uncertainty; retrofitting narrative to unclassified behavior.",
        blind_spot="This is genuine model ignorance. The archetype signature is novel or our rules are incomplete.",
    )


# ----------------------------
# Batch Classification Utility
# ----------------------------

def classify_geometry_batch(records: list[GeometryRecord]) -> list[ArchetypeClassification]:
    """
    Classify a batch of geometry records deterministically.
    """
    return [classify_geometry(g) for g in records]


# ----------------------------
# Utility: Load and Classify All Persisted Records
# ----------------------------

def load_and_classify_all_geometries():
    """
    Load all persisted geometry records and classify each.
    Used by Phase 4 UI to render cognitive state.
    """
    from pathlib import Path
    import json
    
    geometry_path = Path("shadow_data/geometry")
    
    if not geometry_path.exists():
        return []
    
    classifications = []
    
    # Traverse all date directories
    for date_dir in sorted(geometry_path.iterdir()):
        if not date_dir.is_dir():
            continue
        
        # Load each geometry file
        for geo_file in sorted(date_dir.glob("geometry_*.json")):
            try:
                data = json.loads(geo_file.read_text())
                
                # Reconstruct GeometryRecord from JSON
                record = GeometryRecord(
                    run_id=data["run_id"],
                    timestamp=data["timestamp"],
                    regime_label=data["regime_label"],
                    constraint_type=data.get("constraint_type"),
                    divergence_vector=__reconstruct_divergence_vector(data["divergence_vector"]),
                    divergence_norms=__reconstruct_divergence_norms(data["divergence_norms"]),
                    determinism_hash=data["determinism_hash"],
                )
                
                # Classify it
                classification = classify_geometry(record)
                classifications.append(classification)
                
            except Exception as e:
                # Log error but continue
                print(f"Error classifying {geo_file}: {e}")
                continue
    
    return classifications


def __reconstruct_divergence_vector(data):
    """Helper to reconstruct DivergenceVector from JSON."""
    from shadow.geometry.schema import DivergenceVector
    return DivergenceVector(
        direction_delta=data["direction_delta"],
        exposure_delta_usd=data["exposure_delta_usd"],
        fill_ratio_delta=data["fill_ratio_delta"],
        latency_delta_ms=data["latency_delta_ms"],
        price_delta_bps=data["price_delta_bps"],
    )


def __reconstruct_divergence_norms(data):
    """Helper to reconstruct DivergenceNorms from JSON."""
    from shadow.geometry.schema import DivergenceNorms
    return DivergenceNorms(
        l1_norm=data["l1_norm"],
        l_inf_norm=data["l_inf_norm"],
        directional_entropy=data["directional_entropy"],
        temporal_skew=data["temporal_skew"],
    )
