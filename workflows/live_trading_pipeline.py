# Live Trading Pipeline

import sys
sys.path.append('backend')
from pipelines.trading_pipeline import TradingPipeline

def run_live_trading(config):
    """Run live trading pipeline"""
    pipeline = TradingPipeline(config=config, mode="live")

    # Mock live feed
    while True:  # market_is_open()
        market_data = {"price": 100.0}  # live_feed.read()
        state = type('State', (), {
            'volatility': {"AAPL": 0.02},
            'prices': {"AAPL": 100.0},
            'equity': 100000.0,
            'positions': {},
            'run_id': 'live_001',
            'timestamp': 'now'
        })()
        report = pipeline.run(market_data, state)
        print(f"Live execution report: {report}")
        break  # For demo

if __name__ == "__main__":
    config = {
        "risk_budget": 0.01,
        "gross_exposure_limit": 0.5,
        "instrument_cap": 0.1,
        "max_leverage": 1.0,
        "max_drawdown": 0.1,
        "var_limit": 0.05,
        "slippage_cap": 0.01
    }
    run_live_trading(config)