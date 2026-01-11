# Test Shadow Mode

import sys
sys.path.append('backend')
sys.path.append('shadow')
from shadow.simulated_execution import simulate_execution
from shadow.divergence_report import compute_divergence

def test_shadow_execution_is_deterministic():
    orders = [{"symbol": "AAPL", "qty": 100, "side": 1}]
    market_data = {"AAPL": {"mid": 150.0}}
    slippage_model = lambda o, md: 0.001  # Constant slippage

    result1 = simulate_execution(orders, market_data, slippage_model)
    result2 = simulate_execution(orders, market_data, slippage_model)

    assert result1 == result2

def test_shadow_vs_live_divergence_detected():
    live_fills = [{"symbol": "AAPL", "fill_price": 150.1, "slippage": 0.001}]
    shadow_fills = [{"symbol": "AAPL", "fill_price": 150.0, "slippage": 0.0}]

    divergence = compute_divergence(live_fills, shadow_fills)

    assert len(divergence) == 1
    assert abs(divergence[0]["price_diff"] - 0.1) < 1e-10
    assert abs(divergence[0]["slippage_diff"] - 0.001) < 1e-10

def test_shadow_violation_triggers_alert():
    # Placeholder: in real test, check if divergence > threshold triggers alert
    pass