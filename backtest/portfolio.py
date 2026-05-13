"""
Portfolio Management

Capital tracking, position management, risk accounting.
"""

from typing import List, Dict, Optional
import pandas as pd
from backtest.trade import Trade, TradeStatus


class Portfolio:
    """
    Manages trading capital, positions, and performance metrics.
    """
    
    def __init__(self, initial_capital: float):
        """
        Initialize portfolio.
        
        Args:
            initial_capital: Starting capital in ₹
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.equity_curve = [initial_capital]  # Track daily equity
        self.trades: List[Trade] = []
        self.open_trades: Dict[int, Trade] = {}  # trade_id -> Trade
        self.trade_counter = 0
        
        # Metrics
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_fees = 0.0
        self.max_drawdown = 0.0
        self.peak_equity = initial_capital
    
    def create_trade(self, symbol: str, date_generated: str,
                    entry_price: float, stop_loss: float, take_profit: float,
                    risk_amount: float, position_size: int,
                    leverage: float = 1.0) -> Trade:
        """
        Create a new trade (pending state).
        
        Args:
            symbol: Stock symbol
            date_generated: Date signal was generated
            entry_price: Entry price (next day open)
            stop_loss: Stop loss level
            take_profit: Take profit level
            risk_amount: Capital at risk (₹)
            position_size: Number of units/shares
            leverage: Leverage multiplier
        
        Returns:
            Trade object
        """
        self.trade_counter += 1
        
        trade = Trade(
            trade_id=self.trade_counter,
            symbol=symbol,
            date_generated=date_generated,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            leverage=leverage,
            risk_amount=risk_amount,
        )
        
        return trade
    
    def open_trade(self, trade: Trade, entry_price: float, entry_date: str):
        """Execute trade entry."""
        trade.mark_entered(entry_price, entry_date)
        self.open_trades[trade.trade_id] = trade
    
    def close_trade(self, trade_id: int, exit_price: float, exit_date: str,
                   exit_reason: TradeStatus, commission: float):
        """Exit a position."""
        if trade_id not in self.open_trades:
            return
        
        trade = self.open_trades[trade_id]
        trade.exit_date = exit_date
        trade.exit_reason = exit_reason
        if exit_date is not None and trade.entry_date is not None:
            trade.days_held = (pd.to_datetime(exit_date) - pd.to_datetime(trade.entry_date)).days
        
        # Calculate P&L
        trade.calculate_pnl(exit_price, commission)
        
        # Update capital
        self.capital += trade.net_pnl
        self.total_fees += trade.costs
        
        # Track
        if trade.net_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Move to closed
        self.trades.append(trade)
        del self.open_trades[trade_id]
    
    def update_daily_equity(self):
        """Record daily equity (mark-to-market open trades)."""
        mtm_loss = 0  # For unrealized losses
        self.equity_curve.append(self.capital)
        
        # Track max drawdown
        if self.capital > self.peak_equity:
            self.peak_equity = self.capital
        
        dd = (self.peak_equity - self.capital) / self.peak_equity if self.peak_equity > 0 else 0
        self.max_drawdown = max(self.max_drawdown, dd)
    
    def get_total_open_risk(self) -> float:
        """Calculate total capital at risk across open positions."""
        total_risk = sum(t.risk_amount for t in self.open_trades.values())
        return total_risk
    
    def get_metrics(self) -> Dict:
        """Calculate performance metrics."""
        equity = pd.Series(self.equity_curve)
        
        # Returns
        total_return = (self.capital - self.initial_capital) / self.initial_capital
        years = len(self.equity_curve) / 252.0
        cagr = ((self.capital / self.initial_capital) ** (1/years) - 1) if years > 0 else 0
        
        # Daily returns
        daily_returns = equity.pct_change().dropna()
        
        # Volatility
        ann_vol = daily_returns.std() * (252 ** 0.5) if len(daily_returns) > 0 else 0
        
        # Sharpe
        risk_free_rate = 0.06  # 6% annual
        excess_returns = daily_returns - risk_free_rate / 252
        sharpe = (excess_returns.mean() / excess_returns.std() * (252 ** 0.5)) if excess_returns.std() > 0 else 0
        
        # Win metrics
        total_trades = self.winning_trades + self.losing_trades
        win_rate = self.winning_trades / total_trades if total_trades > 0 else 0
        
        # R-multiple stats
        r_multiples = [t.r_multiple for t in self.trades if t.r_multiple != 0]
        avg_r = sum(r_multiples) / len(r_multiples) if r_multiples else 0
        profit_factor = (
            sum(t.net_pnl for t in self.trades if t.net_pnl > 0) /
            abs(sum(t.net_pnl for t in self.trades if t.net_pnl < 0))
            if any(t.net_pnl < 0 for t in self.trades) else 0
        )
        
        return {
            'total_capital': round(self.capital, 2),
            'total_return': round(total_return, 4),
            'cagr': round(cagr, 4),
            'ann_volatility': round(ann_vol, 4),
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown': round(self.max_drawdown, 4),
            'total_trades': total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': round(win_rate, 4),
            'avg_r_multiple': round(avg_r, 2),
            'profit_factor': round(profit_factor, 2),
            'total_fees': round(self.total_fees, 2),
        }
