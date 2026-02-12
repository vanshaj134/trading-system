"""
NIFTY 50 Universe Definition

Core equity universe for the financial intelligence system.
"""

NIFTY_50 = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TCS.NS",
    "INFY.NS", "HINDUNILVR.NS", "ITC.NS", "LT.NS",
    "SBIN.NS", "AXISBANK.NS", "BAJFINANCE.NS", "KOTAKBANK.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS",
    "HCLTECH.NS", "WIPRO.NS", "ONGC.NS", "NTPC.NS",
    "POWERGRID.NS", "JSWSTEEL.NS", "TATASTEEL.NS",
    "ADANIPORTS.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
    "GRASIM.NS", "DRREDDY.NS", "COALINDIA.NS",
    "CIPLA.NS", "HDFCLIFE.NS", "BAJAJFINSV.NS",
    "TECHM.NS", "DIVISLAB.NS", "BRITANNIA.NS",
    "EICHERMOT.NS", "BPCL.NS", "INDUSINDBK.NS",
    "HEROMOTOCO.NS", "APOLLOHOSP.NS", "TATAMOTORS.NS",
    "SHREECEM.NS", "UPL.NS", "SBILIFE.NS",
    "M&M.NS", "BAJAJ-AUTO.NS", "ADANIENT.NS",
    "HINDALCO.NS", "ICICIPRULI.NS", "LTIM.NS"
]

# Metadata
NIFTY_50_METADATA = {
    "count": len(NIFTY_50),
    "exchange": "NSE",
    "suffix": ".NS",
    "description": "Top 50 Indian equities by market cap"
}
