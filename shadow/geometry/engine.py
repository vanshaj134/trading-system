# shadow/geometry/engine.py
from shadow.geometry.schema import GeometryRecord
from shadow.geometry.vector import compute_vector
from shadow.geometry.norms import compute_norms
from shadow.determinism import compute_determinism_hash

GEOMETRY_LOGIC_VERSION = "geometry_v1_stable"
GEOMETRY_TABLE_VERSIONS = {
    "vector": "v1_fixed",
    "norms": "v1_fixed",
}


def compute_geometry(intent, shadow_execution, divergence_record) -> GeometryRecord:
    """
    Pure function: compute complete geometric snapshot.
    
    Determinism rule: same inputs → identical output, byte-for-byte.
    """
    
    # Compute divergence vector (mechanical)
    vector = compute_vector(intent, shadow_execution, divergence_record)
    
    # Compute norms (pure math)
    norms = compute_norms(vector, intent.notional_usd)
    
    # Determine constraint context
    constraint_type = None
    if shadow_execution.executed_notional == 0 and intent.notional_usd > 0:
        constraint_type = "BLOCK"
    elif shadow_execution.fill_percentage < 1.0:
        constraint_type = "PARTIAL"
    
    # Compute determinism hash (includes execution hash for consistency)
    geometry_hash = shadow_execution.determinism_hash  # Use execution hash as geometry reference
    
    return GeometryRecord(
        run_id=str(intent.intent_id),
        timestamp=intent.timestamp,
        regime_label=intent.regime,
        constraint_type=constraint_type,
        divergence_vector=vector,
        divergence_norms=norms,
        determinism_hash=geometry_hash,
    )
