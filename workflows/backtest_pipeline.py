# Backtest Pipeline
import argparse
import json
import random
import sys
from datetime import datetime, timedelta

sys.path.append('backend')
from pipelines.trading_pipeline import TradingPipeline

def generate_mock_data(length=100):
    """Generate deterministic mock market data"""
    random.seed(42)  # Fixed seed for determinism
    base_price = 100.0
    prices = []
    for i in range(length):
        price = base_price + random.gauss(0, 2) + (i * 0.1)  # Trend + noise
        prices.append(round(price, 2))
    return prices

def generate_signals(prices):
    """Simple momentum signal generator"""
    signals = []
    for i in range(1, len(prices)):
        momentum = (prices[i] - prices[i-1]) / prices[i-1]
        if momentum > 0.01:
            signals.append({'action': 'BUY', 'price': prices[i], 'index': i})
        elif momentum < -0.01:
            signals.append({'action': 'SELL', 'price': prices[i], 'index': i})
        else:
            signals.append({'action': 'HOLD', 'price': prices[i], 'index': i})
    return signals

def apply_risk(signals, max_position=1000):
    """Apply basic risk management"""
    positions = []
    for signal in signals:
        if signal['action'] == 'BUY':
            position = min(max_position, 500)  # Simple sizing
        elif signal['action'] == 'SELL':
            position = -min(max_position, 500)
        else:
            position = 0
        positions.append({'position': position, **signal})
    return positions

def calculate_pnl(positions):
    """Calculate P&L from positions"""
    pnl = []
    prev_position = 0
    for pos in positions:
        if prev_position != 0 and pos['position'] != prev_position:
            # Close previous position
            pnl.append(prev_position * (pos['price'] - positions[positions.index(pos)-1]['price']))
        pnl.append(0)  # For simplicity
        prev_position = pos['position']
    return pnl

def run_backtest(run_id):
    """Run deterministic backtest"""
    print(f"Running backtest for run_id: {run_id}")

    # Generate data
    prices = generate_mock_data(100)
    signals = generate_signals(prices)
    positions = apply_risk(signals)
    pnl_series = calculate_pnl(positions)

    # Calculate metrics
    total_pnl = sum(pnl_series)
    sharpe = total_pnl / max(1, len(pnl_series))  # Simplified
    max_drawdown = 0
    peak = 0
    for p in pnl_series:
        peak = max(peak, p)
        max_drawdown = max(max_drawdown, peak - p)

    result = {
        'run_id': run_id,
        'total_pnl': total_pnl,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'signals_count': len(signals),
        'positions': positions[:5],  # Sample
        'pnl_trajectory': pnl_series[:10]
    }

    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_id', required=True)
    args = parser.parse_args()
    run_backtest(args.run_id)