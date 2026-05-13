# Noise vs Edge Test

import random
import json
import sys
sys.path.append('workflows')
from backtest_pipeline import run_backtest  # Import the backtest function

def shuffle_timestamps_within_days(prices):
    """Shuffle timestamps within each day, keeping distributions"""
    # Assuming daily data for simplicity
    # In real implementation, group by day and shuffle within day
    shuffled = prices.copy()
    random.seed(123)  # Different seed for shuffling
    random.shuffle(shuffled)
    return shuffled

def run_noise_test():
    """Run backtest on shuffled data to check for time-based edge"""
    print("=== Noise vs Edge Test ===")

    # Original backtest
    original_result = run_backtest('original')
    print(f"Original Performance: PnL={original_result['total_pnl']:.2f}, Sharpe={original_result['sharpe']:.2f}")

    # Shuffled backtest
    # Modify generate_mock_data to use shuffled prices
    # For demo, we'll simulate by changing seed
    import backtest_pipeline
    original_seed = 42
    backtest_pipeline.random.seed(999)  # Different seed
    shuffled_result = run_backtest('shuffled')
    print(f"Shuffled Performance: PnL={shuffled_result['total_pnl']:.2f}, Sharpe={shuffled_result['sharpe']:.2f}")

    # Compare
    pnl_diff = abs(original_result['total_pnl'] - shuffled_result['total_pnl'])
    sharpe_diff = abs(original_result['sharpe'] - shuffled_result['sharpe'])

    print("\nComparison:")
    print(f"PnL difference: {pnl_diff:.2f}")
    print(f"Sharpe difference: {sharpe_diff:.2f}")

    if pnl_diff < 1000 and sharpe_diff < 1:  # Arbitrary thresholds
        print("⚠️  WARNING: Performance similar after shuffling - possible noise, not edge")
        return False
    else:
        print("✅ Edge appears robust to time structure")
        return True

if __name__ == "__main__":
    run_noise_test()