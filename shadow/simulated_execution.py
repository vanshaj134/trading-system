# shadow/simulated_execution.py

def simulate_execution(orders, market_data, slippage_model):
    fills = []

    for order in orders:
        mid_price = market_data[order["symbol"]]["mid"]
        if slippage_model == "fixed_0.001":
            slippage = 0.001
        else:
            slippage = 0.0  # Default

        fill_price = mid_price + slippage * order["side"]
        fills.append({
            "symbol": order["symbol"],
            "qty": order["qty"],
            "fill_price": fill_price,
            "slippage": abs(slippage),
        })

    return {
        "fills": fills,
        "execution_type": "shadow"
    }