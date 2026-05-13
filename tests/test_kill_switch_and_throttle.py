# Test Kill Switch and Throttle

import sys
sys.path.append('backend')
from backend.state.system_state import SystemState
from backend.support.capital_governor import CapitalGovernor

def test_manual_kill_switch_stops_pipeline():
    state = SystemState()
    state.shutdown("test")
    try:
        state.assert_running()
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "not running" in str(e)

def test_capital_throttle_limits_exposure():
    governor = CapitalGovernor(max_capital=1000, max_leverage=1.0, max_positions=2)
    positions = {"AAPL": 600, "GOOGL": 600}  # Total 1200 > 1000
    result = governor.enforce(positions)
    total = sum(abs(p) for p in result.values())
    assert total <= 1000

def test_too_many_positions_raises():
    governor = CapitalGovernor(max_capital=1000, max_leverage=1.0, max_positions=1)
    positions = {"AAPL": 100, "GOOGL": 100}
    try:
        governor.enforce(positions)
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "too many positions" in str(e)

def test_system_freeze_blocks_new_orders():
    state = SystemState()
    state.freeze("test")
    try:
        state.assert_running()
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "not running" in str(e)