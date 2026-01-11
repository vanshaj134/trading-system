# Test Pipeline Consistency

import sys
sys.path.append('backend')
from pipelines.trading_pipeline import TradingPipeline

def test_pipeline_consistency():
    """Test that live and backtest modes produce same target_positions for same inputs"""
    config = {
        "risk_budget": 0.01,
        "gross_exposure_limit": 0.5,
        "instrument_cap": 0.1,
    }

    # Same inputs
    market_data = {"price": 100.0}
    state = type('State', (), {
        'volatility': {"AAPL": 0.02},
        'prices': {"AAPL": 100.0},
        'equity': 100000.0,
        'positions': {},
    })()

    # Live mode
    live_pipeline = TradingPipeline(config, "live")
    live_report = live_pipeline.run(market_data, state)

    # Backtest mode
    backtest_pipeline = TradingPipeline(config, "backtest")
    backtest_report = backtest_pipeline.run(market_data, state)

    # For now, since execution differs, check target_positions if accessible
    # But since run returns execution_report, and target_positions is internal,
    # This is a placeholder. In real implementation, expose target_positions.

    print("Live report:", live_report)
    print("Backtest report:", backtest_report)
    # Assert something, but for now, just run

if __name__ == "__main__":
    test_pipeline_consistency()