# shadow/divergence_report.py

def compute_divergence(live_fills, shadow_fills):
    divergence = []

    for live, shadow in zip(live_fills, shadow_fills):
        divergence.append({
            "symbol": live["symbol"],
            "price_diff": live["fill_price"] - shadow["fill_price"],
            "slippage_diff": live["slippage"] - shadow["slippage"],
        })

    return divergence