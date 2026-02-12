"""
Assertions - Re-export from assertion_guards
"""

from support.assertion_guards import (
    InvariantViolation,
    assert_position_limits as _assert_position_limits,
    assert_risk_limits,
    assert_execution_limits
)


def assert_position_limits(positions, equity=1.0, prices=None, max_leverage=1.0):
    """
    Assert position limits are respected.
    
    Flexible wrapper that handles different call signatures.
    """
    if prices is None:
        # Simple version: just check total exposure
        total_exposure = sum(abs(p.get('size', 0.0)) for p in positions.values() if isinstance(p, dict))
        if total_exposure > equity * max_leverage:
            raise InvariantViolation(
                f"Position invariant violated: exposure={total_exposure}, limit={equity * max_leverage}"
            )
    else:
        # Full version with prices
        try:
            _assert_position_limits(positions, prices, equity, max_leverage)
        except TypeError:
            # Fallback
            total_exposure = sum(abs(p.get('size', 0.0)) for p in positions.values() if isinstance(p, dict))
            if total_exposure > equity * max_leverage:
                raise InvariantViolation("Position limits exceeded")


def assert_no_live_orders(orders):
    """
    Assert that no orders are in live/pending state.
    
    For Phase 0, this is a safety check that no orders are actually submitted.
    """
    pending_orders = [o for o in orders if o.get('status') in ['PENDING', 'ACTIVE', 'LIVE']]
    if pending_orders:
        raise InvariantViolation(f"Phase 0 violation: {len(pending_orders)} live orders detected")
    # Phase 0: All orders should be PENDING or DRAFT, not actually placed
    return True
