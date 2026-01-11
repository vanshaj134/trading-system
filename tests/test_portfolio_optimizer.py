# Test Portfolio Optimizer

import pytest
from backend.core.portfolio_optimizer import PortfolioOptimizer

def test_allocation_is_deterministic():
    optimizer = PortfolioOptimizer(
        risk_budget=0.01,
        gross_exposure_limit=0.5,
        instrument_cap=0.1,
    )

    signals = {"AAPL": 0.8, "GOOGL": 0.6}
    volatilities = {"AAPL": 0.02, "GOOGL": 0.03}
    prices = {"AAPL": 150.0, "GOOGL": 2500.0}
    equity = 100000.0

    result1 = optimizer.allocate(signals, volatilities, prices, equity)
    result2 = optimizer.allocate(signals, volatilities, prices, equity)

    assert result1 == result2

def test_respects_instrument_cap():
    optimizer = PortfolioOptimizer(
        risk_budget=0.01,
        gross_exposure_limit=1.0,
        instrument_cap=0.05,  # 5% of equity
    )

    signals = {"AAPL": 1.0}
    volatilities = {"AAPL": 0.01}  # Low vol, high allocation
    prices = {"AAPL": 100.0}
    equity = 100000.0

    result = optimizer.allocate(signals, volatilities, prices, equity)

    max_cap = 0.05 * equity
    assert abs(result["AAPL"]) <= max_cap

def test_respects_gross_exposure_limit():
    optimizer = PortfolioOptimizer(
        risk_budget=0.01,
        gross_exposure_limit=0.2,  # 20% total exposure
        instrument_cap=1.0,
    )

    signals = {"AAPL": 1.0, "GOOGL": 1.0}
    volatilities = {"AAPL": 0.01, "GOOGL": 0.01}
    prices = {"AAPL": 100.0, "GOOGL": 100.0}
    equity = 100000.0

    result = optimizer.allocate(signals, volatilities, prices, equity)

    gross_exposure = sum(abs(p) for p in result.values())
    max_gross = 0.2 * equity
    assert gross_exposure <= max_gross

def test_zero_volatility_produces_zero_position():
    optimizer = PortfolioOptimizer(
        risk_budget=0.01,
        gross_exposure_limit=1.0,
        instrument_cap=1.0,
    )

    signals = {"AAPL": 1.0}
    volatilities = {"AAPL": 0.0}
    prices = {"AAPL": 100.0}
    equity = 100000.0

    result = optimizer.allocate(signals, volatilities, prices, equity)

    assert result["AAPL"] == 0.0

def test_zero_signal_produces_zero_position():
    optimizer = PortfolioOptimizer(
        risk_budget=0.01,
        gross_exposure_limit=1.0,
        instrument_cap=1.0,
    )

    signals = {"AAPL": 0.0}
    volatilities = {"AAPL": 0.02}
    prices = {"AAPL": 100.0}
    equity = 100000.0

    result = optimizer.allocate(signals, volatilities, prices, equity)

    assert result["AAPL"] == 0.0