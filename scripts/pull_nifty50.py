#!/usr/bin/env python3
"""
NIFTY 50 Data Pull Script

Fetches full historical daily data for all 50 stocks and stores as Parquet.
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from data.loaders.yahoo_loader import fetch_batch
from data.storage.parquet_store import save_parquet, get_data_coverage
from data.universe import NIFTY_50


def main():
    """Main execution function."""
    print("=" * 60)
    print("🚀 NIFTY 50 DATA PULL")
    print("=" * 60)
    print(f"Symbols: {len(NIFTY_50)}")
    print()
    
    # Fetch data
    print("📥 Fetching data from Yahoo Finance...")
    print()
    
    results = fetch_batch(NIFTY_50, verbose=True)
    
    print()
    print("=" * 60)
    
    # Save to Parquet
    saved_count = 0
    print("💾 Saving to Parquet data lake...")
    
    for symbol, df in results.items():
        try:
            save_parquet(symbol, df)
            saved_count += 1
        except Exception as e:
            print(f"  ❌ Error saving {symbol}: {str(e)}")
    
    print(f"✅ Saved {saved_count}/{len(results)} files")
    print()
    
    # Summary
    print("=" * 60)
    print("📊 DATA LAKE COVERAGE")
    print("=" * 60)
    
    coverage = get_data_coverage()
    
    if coverage:
        total_records = sum(c["records"] for c in coverage.values())
        avg_years = sum(c["years"] for c in coverage.values()) / len(coverage)
        
        print(f"Symbols loaded: {len(coverage)}")
        print(f"Total records: {total_records:,}")
        print(f"Avg years per symbol: {avg_years:.1f}")
        print()
        
        print("Sample coverage:")
        for symbol in sorted(coverage.keys())[:5]:
            c = coverage[symbol]
            print(f"  {symbol}: {c['records']} records ({c['start_date']} → {c['end_date']})")
    
    print()
    print("✅ Data pull complete!")


if __name__ == "__main__":
    main()
