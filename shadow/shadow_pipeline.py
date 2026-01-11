# shadow/shadow_pipeline.py

from shadow.simulated_execution import simulate_execution

def run_shadow_pipeline(orders, market_data, slippage_model):
    return simulate_execution(
        orders=orders,
        market_data=market_data,
        slippage_model=slippage_model,
    )