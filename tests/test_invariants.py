# Test Invariants

import pytest
from backend.support.assertion_guards import (
    assert_position_limits,
    assert_risk_limits,
    assert_execution_limits,
    InvariantViolation,
)

def test_position_limit_violation_raises():
    positions = {"AAPL": 10000}  # $10k position
    prices = {"AAPL": 100}
    equity = 100000
    max_leverage = 1.0  # Limit $100k

    with pytest.raises(InvariantViolation):
        assert_position_limits(positions, prices, equity, max_leverage)

def test_drawdown_violation_raises():
    current_drawdown = 0.15  # 15%
    max_drawdown = 0.1  # 10%
    var = 0.02
    var_limit = 0.05

    with pytest.raises(InvariantViolation):
        assert_risk_limits(current_drawdown, max_drawdown, var, var_limit)

def test_var_violation_raises():
    current_drawdown = 0.05
    max_drawdown = 0.1
    var = 0.06  # 6%
    var_limit = 0.05  # 5%

    with pytest.raises(InvariantViolation):
        assert_risk_limits(current_drawdown, max_drawdown, var, var_limit)

def test_slippage_violation_raises():
    orders = [{"qty": 100}]
    fills = [{"filled_qty": 100, "slippage": 0.02}]  # 2%
    slippage_cap = 0.01  # 1%

    with pytest.raises(InvariantViolation):
        assert_execution_limits(orders, fills, slippage_cap)