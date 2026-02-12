#!/usr/bin/env python3
"""
Daily Feature Computation Script

Computes full feature matrix for all stocks in data lake.
Generates TOP 5 ranked opportunities + full feature export.
"""

import sys
from pathlib import Path
import pandas as pd
import logging

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from data.storage.parquet_store import load_parquet, list_available_symbols
from features.feature_engine import FeatureEngine
from screener.edge_ranker import EdgeRanker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compute_daily_features():
    """Compute features for all available stocks."""
    
    print("=" * 70)
    print("📊 DAILY FEATURE COMPUTATION")
    print("=" * 70)
    print()
    
    # Initialize engines
    feature_engine = FeatureEngine(min_records=252)
    edge_ranker = EdgeRanker()
    
    # Get available symbols
    symbols = list_available_symbols()
    print(f"📁 Found {len(symbols)} stocks in data lake")
    print()
    
    # Compute features
    print("🔧 Computing features...")
    all_features = []
    failed = []
    
    for i, symbol in enumerate(symbols, 1):
        try:
            # Load data
            df = load_parquet(symbol)
            if df is None or df.empty:
                failed.append((symbol, "No data"))
                continue
            
            # Compute features
            features_df = feature_engine.compute_features(df)
            if features_df.empty:
                failed.append((symbol, "Insufficient data"))
                continue
            
            # Get latest features
            latest_features = feature_engine.get_latest_features(features_df)
            if latest_features:
                all_features.append(latest_features)
            
            if i % 10 == 0:
                print(f"  [{i}/{len(symbols)}] {symbol}... ✅")
        
        except Exception as e:
            failed.append((symbol, str(e)))
            logger.error(f"Error processing {symbol}: {str(e)}")
    
    print()
    print(f"✅ Computed features for {len(all_features)} stocks")
    
    if failed:
        print(f"⚠️  Failed: {len(failed)} stocks")
        for symbol, reason in failed[:3]:
            print(f"   - {symbol}: {reason}")
    
    print()
    
    # Rank stocks
    print("=" * 70)
    print("🏆 TOP OPPORTUNITIES BY EDGE SCORE")
    print("=" * 70)
    print()
    
    ranking = edge_ranker.rank_stocks(all_features, top_n=10)
    
    # Display ranking
    print(edge_ranker.format_ranking(ranking))
    
    print()
    print("=" * 70)
    print("📈 DETAILED FEATURE SNAPSHOT (Top 5)")
    print("=" * 70)
    print()
    
    for rank, (symbol, features, score) in enumerate(ranking[:5], 1):
        print(FeatureEngine.feature_summary(features))
        print()
    
    # Save to CSV for reference
    features_df_export = pd.DataFrame(all_features)
    features_df_export = features_df_export.sort_values('symbol')
    
    output_path = "data/lake/features_latest.csv"
    features_df_export.to_csv(output_path, index=False)
    
    print("=" * 70)
    print(f"💾 Features exported to {output_path}")
    print(f"📊 Total records: {len(features_df_export)}")
    print()
    print("✅ Feature computation complete!")
    
    return all_features, ranking


def main():
    """Main entry point."""
    try:
        compute_daily_features()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
