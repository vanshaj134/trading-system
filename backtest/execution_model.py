"""
Execution Model

Handles trade entry/exit logic with no lookahead bias.
- Entry: Next day open price
- Exit: Intraday high/low against SL/TP
- Hold: Continue until SL/TP or timeout
"""

import pandas as pd
from typing import Optional, Tuple
from backtest.trade import Trade, TradeStatus


class ExecutionModel:
    """
    Simulates trade execution in historical context.
    """
    
    def __init__(self, commission: float, slippage: float):
        """
        Initialize execution parameters.
        
        Args:
            commission: Round-trip commission (0.0005 = 0.05%)
            slippage: Execution slippage (0.001 = 0.1%)
        """
        self.commission = commission
        self.slippage = slippage
    
    def get_entry_price(self, next_day_open: float) -> float:
        """
        Get entry price with slippage.
        
        Args:
            next_day_open: Next day opening price
        
        Returns:
            Realistic entry price considering slippage
        """
        return next_day_open * (1 + self.slippage)
    
    def get_exit_price(self, exit_price: float, direction: str = "LONG") -> float:
        """
        Get exit price with slippage.
        
        Args:
            exit_price: Base exit price (SL or TP)
            direction: LONG or SHORT (all long in v1)
        
        Returns:
            Realistic exit price
        """
        if direction == "LONG":
            # SL: exit better, TP: exit worse
            return exit_price * (1 - self.slippage)
        else:
            return exit_price * (1 + self.slippage)
    
    def check_exit_condition(self, trade: Trade, high: float, low: float) -> Optional[Tuple[float, TradeStatus]]:
        """
        Check if trade should exit intraday.
        
        Entry was yesterday. Today we check:
        - If low <= SL → stopped out
        - If high >= TP → target hit
        
        Args:
            trade: Trade object (must be OPEN)
            high: Today's high
            low: Today's low
        
        Returns:
            (exit_price, reason) if exit triggered, else None
        """
        if trade.status != TradeStatus.OPEN:
            return None
        
        # Check stop loss first (priority)
        if low <= trade.stop_loss:
            exit_price = self.get_exit_price(trade.stop_loss, "LONG")
            return (exit_price, TradeStatus.STOPPED_OUT)
        
        # Check take profit
        if high >= trade.take_profit:
            exit_price = self.get_exit_price(trade.take_profit, "LONG")
            return (exit_price, TradeStatus.TARGET_HIT)
        
        return None
    
    def simulate_day(self, trade: Trade, data: dict) -> Optional[Tuple[float, TradeStatus]]:
        """
        Simulate one day of holding a trade.
        
        Args:
            trade: Trade object (must be OPEN)
            data: Dict with 'open', 'high', 'low', 'close' for today
        
        Returns:
            (exit_price, reason) if trade exits, else None
        """
        return self.check_exit_condition(trade, data.get('high', 0), data.get('low', 0))
