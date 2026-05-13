# Single-Trade Forensic Replay Tool

import json
import argparse

def load_trade_data(trade_id):
    """Mock load trade data - replace with actual DB query"""
    # Simulate trade data
    return {
        'trade_id': trade_id,
        'symbol': 'AAPL',
        'entry_time': '2023-01-01 10:00:00',
        'entry_price': 150.0,
        'exit_time': '2023-01-01 15:00:00',
        'exit_price': 152.0,
        'quantity': 100,
        'pnl': 200.0
    }

def trace_signal_generation(trade_data):
    """Step 1: What data triggered the signal?"""
    symbol = trade_data['symbol']
    entry_time = trade_data['entry_time']

    # Mock market data query
    market_data = {
        'timestamp': entry_time,
        'price': 149.5,
        'volume': 1000000,
        'indicators': {'rsi': 65, 'macd': 0.5}
    }

    print("1. Market Data at Signal Time:")
    print(json.dumps(market_data, indent=2))

    # Mock signal logic
    signal = {
        'action': 'BUY',
        'score': 0.75,
        'confidence': 0.8,
        'features_used': ['rsi', 'macd', 'volume'],
        'threshold_crossed': 'momentum > 0.02'
    }

    print("\n2. Signal Generation:")
    print(json.dumps(signal, indent=2))

    return market_data, signal

def trace_risk_application(signal, trade_data):
    """Step 2: How risk scaled the position"""
    account_value = 100000
    risk_budget = 0.01  # 1%
    volatility = 0.02
    price = trade_data['entry_price']

    raw_size = (risk_budget * account_value) / (volatility * price)
    adjusted_size = min(raw_size, 1000)  # Liquidity limit

    risk_calc = {
        'account_value': account_value,
        'risk_budget_pct': risk_budget,
        'volatility': volatility,
        'raw_position_size': raw_size,
        'adjusted_size': adjusted_size,
        'final_quantity': trade_data['quantity']
    }

    print("\n3. Risk Engine Application:")
    print(json.dumps(risk_calc, indent=2))

    return risk_calc

def trace_execution(trade_data):
    """Step 3: Execution details"""
    execution = {
        'order_type': 'MARKET',
        'intended_price': trade_data['entry_price'],
        'actual_avg_price': trade_data['entry_price'] + 0.1,  # Slippage
        'slippage': 0.1,
        'execution_time': trade_data['entry_time'],
        'full_fill': True
    }

    print("\n4. Execution Details:")
    print(json.dumps(execution, indent=2))

    return execution

def trace_exit_logic(trade_data):
    """Step 4: Exit reasoning"""
    exit_logic = {
        'exit_signal': 'target_hit',
        'target_price': 152.0,
        'stop_loss': 148.0,
        'time_based_exit': False,
        'reason': 'Profit target reached'
    }

    print("\n5. Exit Logic:")
    print(json.dumps(exit_logic, indent=2))

    return exit_logic

def replay_trade(trade_id):
    """Full forensic replay"""
    print(f"=== Forensic Replay for Trade {trade_id} ===\n")

    trade_data = load_trade_data(trade_id)

    market_data, signal = trace_signal_generation(trade_data)
    risk_calc = trace_risk_application(signal, trade_data)
    execution = trace_execution(trade_data)
    exit_logic = trace_exit_logic(trade_data)

    summary = {
        'trade_id': trade_id,
        'total_pnl': trade_data['pnl'],
        'trace_complete': True,
        'explanation_level': 'detailed'  # vs 'model_decided'
    }

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--trade_id', required=True)
    args = parser.parse_args()
    replay_trade(args.trade_id)