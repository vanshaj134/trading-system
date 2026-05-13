"""
Parquet Data Lake Storage

Handles local storage and retrieval of OHLCV data in Parquet format.
Fast, compressed, column-oriented storage suitable for analytics.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Optional


BASE_PATH = "data/lake/equities"


def ensure_lake_exists():
    """Create data lake directory if it doesn't exist."""
    os.makedirs(BASE_PATH, exist_ok=True)


def _get_parquet_path(symbol: str) -> str:
    """Get normalized parquet file path for a symbol."""
    clean_symbol = symbol.replace(".NS", "").replace(".BO", "")
    return f"{BASE_PATH}/{clean_symbol}.parquet"


def save_parquet(symbol: str, df: pd.DataFrame) -> str:
    """
    Save DataFrame to Parquet format.
    
    Args:
        symbol: Stock symbol
        df: DataFrame with OHLCV data
    
    Returns:
        Path to saved file
    """
    ensure_lake_exists()
    file_path = _get_parquet_path(symbol)
    
    df.to_parquet(file_path, index=False, compression="snappy")
    
    return file_path


def load_parquet(symbol: str) -> Optional[pd.DataFrame]:
    """
    Load DataFrame from Parquet format.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        DataFrame if file exists, None otherwise
    """
    file_path = _get_parquet_path(symbol)
    
    if not os.path.exists(file_path):
        return None
    
    return pd.read_parquet(file_path)


def list_available_symbols() -> list:
    """
    List all available symbols in data lake.
    
    Returns:
        List of symbols with available data
    """
    if not os.path.exists(BASE_PATH):
        return []
    
    files = os.listdir(BASE_PATH)
    symbols = [f.replace(".parquet", "") for f in files if f.endswith(".parquet")]
    
    return sorted(symbols)


def get_data_coverage() -> dict:
    """
    Get summary of data lake coverage.
    
    Returns:
        Dictionary with coverage statistics
    """
    symbols = list_available_symbols()
    coverage = {}
    
    for symbol in symbols:
        df = load_parquet(symbol)
        if df is not None and len(df) > 0:
            coverage[symbol] = {
                "records": len(df),
                "start_date": str(df["date"].min()),
                "end_date": str(df["date"].max()),
                "years": round((df["date"].max() - df["date"].min()).days / 365.25, 1)
            }
    
    return coverage


def delete_parquet(symbol: str) -> bool:
    """
    Delete parquet file for a symbol.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        True if deleted, False if didn't exist
    """
    file_path = _get_parquet_path(symbol)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    
    return False
