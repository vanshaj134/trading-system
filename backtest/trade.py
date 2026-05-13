"""
Trade State Machine

Represents a single trade's lifecycle.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class TradeStatus(Enum):
    """Trade lifecycle states."""
    PENDING = "PENDING"        # Generated but not entered
    OPEN = "OPEN"              # Entered at next day open
    STOPPED_OUT = "STOPPED_OUT"
    TARGET_HIT = "TARGET_HIT"
    TIMEOUT_EXIT = "TIMEOUT_EXIT"
    CLOSED = "CLOSED"


@dataclass
class Trade:
    """
    Represents one trade from inception to exit.
    """
    # Identification
    trade_id: int
    symbol: str
    date_generated: str
    
    # Entry
    entry_price: float
    entry_date: Optional[str] = None
    
    # Execution Parameters
    stop_loss: float = 0.0
    take_profit: float = 0.0
    position_size: int = 0
    leverage: float = 1.0
    risk_amount: float = 0.0
    
    # Pricing
    highest_price: float = 0.0
    lowest_price: float = 0.0
    
    # Exit
    exit_price: Optional[float] = None
    exit_date: Optional[str] = None
    exit_reason: Optional[TradeStatus] = None
    
    # P&L
    gross_pnl: float = 0.0
    costs: float = 0.0
    net_pnl: float = 0.0
    r_multiple: float = 0.0
    
    # State
    status: TradeStatus = TradeStatus.PENDING
    days_held: int = 0
    
    def mark_entered(self, entry_price: float, entry_date: str):
        """Record actual entry execution."""
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.status = TradeStatus.OPEN
        self.highest_price = entry_price
        self.lowest_price = entry_price
    
    def update_price_range(self, high: float, low: float):
        """Update intraday high/low."""
        self.highest_price = max(self.highest_price, high)
        self.lowest_price = min(self.lowest_price, low)
    
    def calculate_pnl(self, exit_price: float, commission: float):
        """Calculate P&L at exit."""
        self.exit_price = exit_price
        
        # Gross P&L
        price_change = exit_price - self.entry_price
        self.gross_pnl = price_change * self.position_size
        
        # Costs
        self.costs = (abs(self.entry_price) + abs(exit_price)) * self.position_size * commission
        
        # Net
        self.net_pnl = self.gross_pnl - self.costs
        
        # R-multiple
        if self.risk_amount > 0:
            self.r_multiple = self.net_pnl / self.risk_amount
    
    def check_stops(self, high: float, low: float) -> Optional[TradeStatus]:
        """Check if SL or TP hit intraday."""
        if low <= self.stop_loss:
            return TradeStatus.STOPPED_OUT
        if high >= self.take_profit:
            return TradeStatus.TARGET_HIT
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'date_generated': self.date_generated,
            'entry_date': self.entry_date,
            'exit_date': self.exit_date,
            'entry_price': round(self.entry_price, 2),
            'exit_price': round(self.exit_price or 0, 2),
            'stop_loss': round(self.stop_loss, 2),
            'take_profit': round(self.take_profit, 2),
            'position_size': self.position_size,
            'leverage': round(self.leverage, 2),
            'gross_pnl': round(self.gross_pnl, 2),
            'costs': round(self.costs, 2),
            'net_pnl': round(self.net_pnl, 2),
            'r_multiple': round(self.r_multiple, 2),
            'exit_reason': self.exit_reason.value if self.exit_reason else None,
            'days_held': self.days_held,
        }
