#!/usr/bin/env python3
"""
Daily Trade Generation Script

Creates ready-to-trade specifications for top 5 opportunities.
Outputs:
  - Trade specs with instrument type, sizing, leverage
  - Entry/exit levels based on technical analysis
  - Risk/reward metrics
"""

import sys
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from data.storage.parquet_store import load_parquet, list_available_symbols
from features.feature_engine import FeatureEngine
from screener.edge_ranker import EdgeRanker
from screener.instrument_decider import InstrumentDecider, TradeSpec

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_daily_trades(total_capital: float = 10_00_000):
    """Generate daily trade specifications."""
    
    print("=" * 80)
    print("🤖 DAILY TRADE GENERATION SYSTEM")
    print("=" * 80)
    print(f"Capital Base: ₹{total_capital:,.0f}")
    print()
    
    # Initialize engines
    feature_engine = FeatureEngine(min_records=252)
    edge_ranker = EdgeRanker()
    instrument_decider = InstrumentDecider(
        total_capital=total_capital,
        max_risk_per_trade=0.02,  # 2% risk per trade
        max_leverage=3.0
    )
    
    # Get available symbols
    symbols = list_available_symbols()
    
    # Compute features
    all_features = []
    for symbol in symbols:
        try:
            df = load_parquet(symbol)
            if df is None or df.empty:
                continue
            
            features_df = feature_engine.compute_features(df)
            if features_df.empty:
                continue
            
            latest_features = feature_engine.get_latest_features(features_df)
            if latest_features:
                all_features.append(latest_features)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {str(e)}")
    
    # Rank stocks
    ranking = edge_ranker.rank_stocks(all_features, top_n=5)
    
    # Generate trade specs
    print("=" * 80)
    print("📋 GENERATING TRADE SPECS FOR TOP 5")
    print("=" * 80)
    print()
    
    specs = instrument_decider.generate_specs_for_rankings(ranking)
    
    # Display specs
    for i, spec in enumerate(specs, 1):
        print(f"\n{'='*80}")
        print(f"TRADE #{i}: {spec.symbol}")
        print(f"{'='*80}")
        print(f"📊 Edge Score:        {spec.edge_score:.1f}/100")
        print(f"💵 Current Price:     ₹{spec.close_price:.2f}")
        print()
        print(f"🎯 INSTRUMENT & SIZING")
        print(f"   Type:              {spec.instrument.value}")
        print(f"   Direction:         {spec.direction}")
        print(f"   Leverage:          {spec.leverage:.2f}x")
        print(f"   Position Size:     ₹{spec.position_size_value:,.0f} ({spec.position_size_units:,} units)")
        print()
        print(f"📍 ENTRY/EXIT LEVELS")
        print(f"   Entry Price:       ₹{spec.entry_price:.2f}")
        print(f"   Stop Loss:         ₹{spec.stop_loss:.2f}")
        print(f"   Take Profit:       ₹{spec.take_profit:.2f}")
        print()
        print(f"💰 RISK/REWARD")
        print(f"   Risk per Trade:    ₹{spec.risk_per_trade:,.0f} ({spec.risk_percent:.2f}% of capital)")
        print(f"   Expected Reward:   ₹{spec.expected_reward:,.0f}")
        print(f"   Reward:Risk Ratio: {spec.reward_risk_ratio:.2f}:1")
        print()
        print(f"💡 RATIONALE")
        print(f"   {spec.rationale}")
    
    # Summary table
    print()
    print("=" * 80)
    print("📊 TRADE SUMMARY TABLE")
    print("=" * 80)
    print()
    
    # Create DataFrame for display
    summary_data = []
    for spec in specs:
        summary_data.append({
            'Symbol': spec.symbol,
            'Edge': f"{spec.edge_score:.1f}",
            'Instrument': spec.instrument.value,
            'Dir': spec.direction,
            'Entry (₹)': f"{spec.entry_price:.2f}",
            'SL (₹)': f"{spec.stop_loss:.2f}",
            'TP (₹)': f"{spec.take_profit:.2f}",
            'Position (₹)': f"{spec.position_size_value/1000:.0f}K",
            'Risk (%)': f"{spec.risk_percent:.2f}",
            'R:R': f"{spec.reward_risk_ratio:.2f}",
        })
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    # Export to JSON for API integration
    specs_dict = [spec.to_dict() for spec in specs]
    
    import json
    export_path = "data/lake/trades_ready.json"
    with open(export_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_capital': total_capital,
            'trades': specs_dict
        }, f, indent=2)
    
    # Export to CSV
    csv_data = [spec.to_dict() for spec in specs]
    csv_df = pd.DataFrame(csv_data)
    csv_path = "data/lake/trades_ready.csv"
    csv_df.to_csv(csv_path, index=False)
    
    print()
    print("=" * 80)
    print("💾 EXPORT COMPLETE")
    print(f"   JSON: {export_path}")
    print(f"   CSV:  {csv_path}")
    print()
    print("✅ Daily trade generation complete!")
    print()
    
    return specs


def main():
    """Main entry point."""
    try:
        # Use command-line arg for capital if provided
        capital = float(sys.argv[1]) if len(sys.argv) > 1 else 10_00_000
        generate_daily_trades(total_capital=capital)
    except ValueError:
        print("Usage: python scripts/generate_daily_trades.py [capital]")
        print("Example: python scripts/generate_daily_trades.py 1000000")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
