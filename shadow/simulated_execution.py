# shadow/simulated_execution.py

def simulate_execution(orders, market_data, slippage_model):
    fills = []

    for order in orders:
        mid_price = market_data[order["symbol"]]["mid"]
        slippage = slippage_model(order, market_data)

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