# shadow/engine.py
from shadow.schemas import ShadowExecution, DivergenceRecord
from shadow.tables import (
    SLIPPAGE_BPS_BY_REGIME,
    LATENCY_MS_BY_REGIME,
    FILL_RATE_BY_REGIME,
    CONSTRAINT_BLOCK_REGIME,
)
from shadow.determinism import compute_determinism_hash

LOGIC_VERSION = "shadow_v2_divergence"
TABLE_VERSIONS = {
    "slippage": "v1_fixed",
    "latency": "v1_fixed",
    "fill": "v1_fixed",
    "constraints": "v1_fixed",
}


def shadow_execute(intent, market_snapshot):
    midpoint = (market_snapshot.bid + market_snapshot.ask) / 2.0

    slippage_bps = SLIPPAGE_BPS_BY_REGIME[intent.regime]
    latency_ms = LATENCY_MS_BY_REGIME[intent.regime]
    fill_rate = FILL_RATE_BY_REGIME[intent.regime]

    blocked_constraint = CONSTRAINT_BLOCK_REGIME.get(intent.regime)

    # Constraint blocks everything
    if blocked_constraint:
        executed_notional = 0.0
        executed_direction = "FLAT"
        fill_percentage = 0.0
    else:
        executed_notional = intent.notional_usd * fill_rate
        executed_direction = intent.direction
        fill_percentage = fill_rate

    entry_price = midpoint * (1 + slippage_bps / 10_000)

    determinism_hash = compute_determinism_hash(
        intent,
        market_snapshot,
        LOGIC_VERSION,
        TABLE_VERSIONS,
    )

    execution = ShadowExecution(
        intent_id=intent.intent_id,
        execution_timestamp=market_snapshot.timestamp,
        executed_direction=executed_direction,
        executed_notional=executed_notional,
        entry_price=entry_price,
        fill_percentage=fill_percentage,
        slippage_bps=slippage_bps,
        latency_ms=latency_ms,
        shadow_exposure_usd=executed_notional,
        mark_to_market_pnl=0.0,
        determinism_hash=determinism_hash,
    )

    exposure_delta = intent.notional_usd - executed_notional

    divergence = DivergenceRecord(
        run_id=intent.intent_id,
        timestamp=market_snapshot.timestamp,
        exposure_delta_usd=exposure_delta,
        exposure_delta_pct=(
            exposure_delta / intent.notional_usd
            if intent.notional_usd != 0
            else 0.0
        ),
        direction_flip=(intent.direction != executed_direction),
    )

    return execution, divergence
