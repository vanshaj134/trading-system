"""
Yahoo Finance Data Loader

Fetches full historical daily OHLCV data for Indian equities (NSE).
"""

import yfinance as yf
import pandas as pd
from typing import Optional


def fetch_full_history(symbol: str, max_retries: int = 3) -> pd.DataFrame:
    """
    Fetch complete historical data from Yahoo Finance.
    
    Args:
        symbol: NSE symbol (e.g., "RELIANCE.NS")
        max_retries: Number of retry attempts on failure
    
    Returns:
        DataFrame with columns: [date, symbol, Open, High, Low, Close, Volume]
    
    Raises:
        ValueError: If no data returned after retries
    """
    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="max", interval="1d", auto_adjust=True)
            
            if df.empty:
                if attempt < max_retries - 1:
                    print(f"  ⚠️  Empty data for {symbol}, retrying...")
                    continue
                else:
                    raise ValueError(f"No data returned for {symbol} after {max_retries} attempts")
            
            # Clean and standardize
            df = df.reset_index()
            df["symbol"] = symbol
            df["date"] = pd.to_datetime(df["Date"]).dt.date
            
            df = df[["date", "symbol", "Open", "High", "Low", "Close", "Volume"]].copy()
            df = df.sort_values("date").reset_index(drop=True)
            
            # Basic validation
            if len(df) < 252:  # Less than 1 year of data
                print(f"  ⚠️  Only {len(df)} trading days for {symbol}")
            
            return df
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️  Error fetching {symbol}: {str(e)}, retrying...")
            else:
                raise ValueError(f"Failed to fetch {symbol}: {str(e)}")
    
    raise ValueError(f"Could not fetch data for {symbol}")


def fetch_batch(symbols: list, verbose: bool = True) -> dict:
    """
    Fetch data for multiple symbols.
    
    Args:
        symbols: List of NSE symbols
        verbose: Print progress
    
    Returns:
        Dictionary mapping symbol -> DataFrame
    """
    results = {}
    failed = []
    
    for i, symbol in enumerate(symbols, 1):
        try:
            if verbose:
                print(f"[{i}/{len(symbols)}] Fetching {symbol}...", end=" ")
            
            df = fetch_full_history(symbol)
            results[symbol] = df
            
            if verbose:
                print(f"✅ ({len(df)} days)")
        
        except Exception as e:
            failed.append((symbol, str(e)))
            if verbose:
                print(f"❌ {str(e)}")
    
    if verbose and failed:
        print(f"\n⚠️  Failed to fetch {len(failed)} symbols")
    
    return results
