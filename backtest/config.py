"""
Backtest Configuration

Parameters locked for v1 (conservative, long-only validation).
"""

# Capital
START_CAPITAL = 1_000_000  # ₹1M
RISK_PER_TRADE = 0.02      # 2% per trade

# Costs
COMMISSION = 0.0005         # 0.05% round trip (0.025% each leg)
SLIPPAGE = 0.001            # 0.1% execution slippage

# Execution
ATR_MULTIPLIER_SL = 1.5    # Stop loss at 1.5x ATR below entry
ATR_MULTIPLIER_TP = 2.0    # Take profit at 2.0x ATR above entry

# Position Limits
MAX_OPEN_TRADES = 5         # Max 5 concurrent positions
MAX_PORTFOLIO_RISK = 0.08   # Max 8% total capital at risk

# Instruments
INSTRUMENTS = ["SPOT", "FUTURES"]  # Long-only, no options, no shorts

# Backtest Dates
START_DATE = "2019-01-01"   # 5+ years of history
END_DATE = "2025-02-11"     # Today

# Leverage
MAX_LEVERAGE = 1.5          # Conservative: no extreme leverage
