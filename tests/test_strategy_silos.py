# Test Strategy Silos

import sys
sys.path.append('backend')
from backend.silos.silo_allocator import initialize_silos
from backend.silos.silo_enforcer import enforce_silo_limits
from backend.silos.silo_state import SiloState

def test_silo_initialization():
    total_equity = 100000
    silos = initialize_silos(total_equity)
    assert len(silos) == 3
    assert "trend_following_v1" in silos
    total_fraction = sum(s.capital_fraction for s in silos.values())
    assert abs(total_fraction - 1.0) < 1e-6

def test_silo_capital_allocation():
    config = {
        "capital_fraction": 0.5,
        "max_leverage": 1.0,
        "risk_budget": 0.01,
        "max_drawdown": 0.1,
    }
    silo = SiloState(config, 100000)
    assert silo.capital == 50000

def test_silo_enforcement_freezes_on_drawdown():
    config = {
        "capital_fraction": 0.5,
        "max_leverage": 1.0,
        "risk_budget": 0.01,
        "max_drawdown": 0.1,
    }
    silo = SiloState(config, 100000)
    silo.drawdown = 0.15  # Above limit
    try:
        enforce_silo_limits(silo)
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "frozen" in str(e)
        assert silo.status == "FROZEN"

def test_silo_isolation():
    # Test that silos don't affect each other
    silos = initialize_silos(100000)
    silos["trend_following_v1"].drawdown = 0.15
    try:
        enforce_silo_limits(silos["trend_following_v1"])
    except RuntimeError:
        pass
    # Other silos should remain active
    assert silos["mean_reversion_v1"].status == "ACTIVE"