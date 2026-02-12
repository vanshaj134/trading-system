"""
Instrument Decision Engine

Determines optimal instrument type (Spot/Futures/Options) for each opportunity.
Calculates position sizing, leverage, and risk parameters.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InstrumentType(Enum):
    """Supported instrument types."""
    SPOT = "SPOT"
    FUTURES = "FUTURES"
    CALL_LONG = "CALL_LONG"
    PUT_SHORT = "PUT_SHORT"
    CALL_SPREAD = "CALL_SPREAD"
    PUT_SPREAD = "PUT_SPREAD"


@dataclass
class TradeSpec:
    """Complete trade specification."""
    symbol: str
    date: str
    close_price: float
    edge_score: float
    instrument: InstrumentType
    direction: str  # LONG / SHORT
    position_size_value: float  # ₹ notional
    position_size_units: int  # Number of shares/contracts
    leverage: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_per_trade: float  # ₹
    risk_percent: float  # % of capital
    expected_reward: float  # ₹
    reward_risk_ratio: float
    rationale: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'date': self.date,
            'close_price': self.close_price,
            'edge_score': self.edge_score,
            'instrument': self.instrument.value,
            'direction': self.direction,
            'position_size_value': round(self.position_size_value, 2),
            'position_size_units': self.position_size_units,
            'leverage': round(self.leverage, 2),
            'entry_price': round(self.entry_price, 2),
            'stop_loss': round(self.stop_loss, 2),
            'take_profit': round(self.take_profit, 2),
            'risk_per_trade': round(self.risk_per_trade, 2),
            'risk_percent': round(self.risk_percent, 2),
            'expected_reward': round(self.expected_reward, 2),
            'reward_risk_ratio': round(self.reward_risk_ratio, 2),
            'rationale': self.rationale,
        }


class InstrumentDecider:
    """
    Decides instrument type and generates trade specifications.
    """
    
    def __init__(self, 
                 total_capital: float = 10_00_000,  # ₹10 lakhs default
                 max_risk_per_trade: float = 0.02,  # 2% risk per trade
                 max_leverage: float = 3.0):
        """
        Initialize decider.
        
        Args:
            total_capital: Total trading capital (₹)
            max_risk_per_trade: Max risk per trade as % of capital
            max_leverage: Maximum allowed leverage
        """
        self.total_capital = total_capital
        self.max_risk_per_trade = max_risk_per_trade
        self.max_leverage = max_leverage
    
    
    def decide_instrument(self, features: Dict) -> Tuple[InstrumentType, str]:
        """
        Decide instrument type based on features.
        
        Args:
            features: Feature dictionary
        
        Returns:
            Tuple of (InstrumentType, rationale)
        """
        adx = features['adx']
        rsi = features['rsi']
        atr_pct = features['atr_pct']
        vol_expansion = features['vol_expansion']
        vol_percentile = features['vol_percentile']
        momentum = features['momentum']
        
        # Rule 1: Strong trend + Expanding volatility → Futures
        if adx > 40 and vol_expansion > 1.15 and abs(momentum) > 5:
            return InstrumentType.FUTURES, "Strong directional trend with volatility expansion"
        
        # Rule 2: Strong trend (ADX > 35) → Futures
        if adx > 35 and vol_expansion > 1.0:
            return InstrumentType.FUTURES, "Strong trend detected, directional setup"
        
        # Rule 3: High RSI + Breakout + Rising vol → Long Call
        if rsi > 70 and vol_percentile > 0.7 and vol_expansion > 1.1 and momentum > 3:
            return InstrumentType.CALL_LONG, "Overbought with breakout, call option indicated"
        
        # Rule 4: High IV + Range-bound → Put Sell (Short Put)
        if 30 < adx < 35 and 55 < rsi < 75 and vol_percentile > 0.6:
            return InstrumentType.PUT_SHORT, "Range expectation, premium capture strategy"
        
        # Rule 5: Moderate trend + Low volatility → Spot
        if adx < 25 and vol_expansion < 1.1:
            return InstrumentType.SPOT, "Weak trend, conservative spot holding"
        
        # Rule 6: Oversold with expansion → Call Long
        if rsi < 30 and vol_percentile > 0.5 and vol_expansion > 1.0:
            return InstrumentType.CALL_LONG, "Oversold with recovery setup"
        
        # Default: Conservative spot
        return InstrumentType.SPOT, "Default conservative instrument"
    
    
    def calculate_leverage(self, features: Dict, instrument: InstrumentType) -> float:
        """
        Calculate appropriate leverage based on volatility.
        
        Args:
            features: Feature dictionary
            instrument: Selected instrument type
        
        Returns:
            Leverage multiplier (1.0 to max_leverage)
        """
        atr_pct = features['atr_pct']
        adx = features['adx']
        vol_expansion = features['vol_expansion']
        
        # Less volatile = more leverage possible
        # More volatile = less leverage needed
        
        if atr_pct > 4:  # Very volatile
            base_lev = 1.0  # No leverage
        elif atr_pct > 3:
            base_lev = 1.2
        elif atr_pct > 2:
            base_lev = 1.5
        else:
            base_lev = 2.0  # Low vol, can lever
        
        # ADX adjustment (strong trends can support more leverage)
        if adx > 50:
            adx_mult = 1.5
        elif adx > 40:
            adx_mult = 1.3
        elif adx > 30:
            adx_mult = 1.0
        else:
            adx_mult = 0.8
        
        leverage = base_lev * adx_mult
        
        # Cap at max
        leverage = min(leverage, self.max_leverage)
        
        # Options: no leverage multiplier applied
        if instrument in [InstrumentType.CALL_LONG, InstrumentType.PUT_SHORT]:
            leverage = 1.0
        
        return leverage
    
    
    def calculate_position_size(self, 
                                features: Dict, 
                                instrument: InstrumentType,
                                leverage: float) -> Tuple[float, int]:
        """
        Calculate position size (notional ₹ and units).
        
        Args:
            features: Feature dictionary
            instrument: Instrument type
            leverage: Leverage multiplier
        
        Returns:
            Tuple of (notional_value, unit_count)
        """
        close_price = features['close']
        atr_pct = features['atr_pct']
        
        # Risk per trade
        risk_value = self.total_capital * self.max_risk_per_trade
        
        # Position size based on ATR stop loss
        # If ATR is 2%, stop is roughly 2.5% below entry
        stop_loss_pct = atr_pct * 1.25
        
        # Position size = Risk / Stop loss %
        notional = (risk_value / (stop_loss_pct / 100)) * leverage
        
        # Cap at reasonable level
        max_notional = self.total_capital * 0.3  # Max 30% of capital
        notional = min(notional, max_notional)
        
        # Unit count
        units = int(notional / close_price)
        
        # Options: 1 lot = 75 shares, so scale by 75
        if instrument in [InstrumentType.CALL_LONG, InstrumentType.PUT_SHORT]:
            units = max(1, units // 75) * 75
        
        return notional, units
    
    
    def calculate_exits(self, 
                       features: Dict,
                       close_price: float,
                       direction: str) -> Tuple[float, float]:
        """
        Calculate stop loss and take profit levels.
        
        Args:
            features: Feature dictionary
            close_price: Current close price
            direction: LONG or SHORT
        
        Returns:
            Tuple of (stop_loss, take_profit)
        """
        atr = features['atr']
        ema50 = features['ema50']
        ema200 = features['ema200']
        adx = features['adx']
        
        if direction == "LONG":
            # Stop loss below key support (EMA50 or 1.5x ATR)
            sl_level1 = ema50
            sl_level2 = close_price - (1.5 * atr)
            stop_loss = max(sl_level1, sl_level2)  # Use higher support
            
            # Take profit: ATR multiples or resistance
            if adx > 50:
                tp_multiplier = 2.0  # Strong trend, extend TP
            elif adx > 35:
                tp_multiplier = 1.5
            else:
                tp_multiplier = 1.0
            
            take_profit = close_price + (tp_multiplier * atr)
        
        else:  # SHORT
            # Stop loss above key resistance
            sl_level1 = ema50
            sl_level2 = close_price + (1.5 * atr)
            stop_loss = min(sl_level1, sl_level2)
            
            # Take profit
            if adx > 50:
                tp_multiplier = 2.0
            elif adx > 35:
                tp_multiplier = 1.5
            else:
                tp_multiplier = 1.0
            
            take_profit = close_price - (tp_multiplier * atr)
        
        return stop_loss, take_profit
    
    
    def generate_trade_spec(self, 
                           features: Dict,
                           edge_score: float) -> TradeSpec:
        """
        Generate complete trade specification.
        
        Args:
            features: Feature dictionary
            edge_score: Edge score (0-100)
        
        Returns:
            TradeSpec object
        """
        symbol = features['symbol']
        date = features['date']
        close_price = features['close']
        rsi = features['rsi']
        momentum = features['momentum']
        
        # Decide instrument
        instrument, rationale = self.decide_instrument(features)
        
        # Decide direction (based on momentum/RSI)
        if rsi > 60 or momentum > 3:
            direction = "LONG"
        elif rsi < 40 or momentum < -3:
            direction = "SHORT"
        else:
            direction = "LONG"  # Default
        
        # Calculate leverage
        leverage = self.calculate_leverage(features, instrument)
        
        # Calculate position size
        notional, units = self.calculate_position_size(features, instrument, leverage)
        
        # Calculate exits
        stop_loss, take_profit = self.calculate_exits(features, close_price, direction)
        
        # Risk/Reward calculations
        if direction == "LONG":
            risk = abs(close_price - stop_loss) * units
            reward = abs(take_profit - close_price) * units
        else:
            risk = abs(stop_loss - close_price) * units
            reward = abs(close_price - take_profit) * units
        
        risk_percent = (risk / self.total_capital) * 100
        reward_risk_ratio = reward / risk if risk > 0 else 0
        
        # Create spec
        spec = TradeSpec(
            symbol=symbol,
            date=str(date),
            close_price=close_price,
            edge_score=edge_score,
            instrument=instrument,
            direction=direction,
            position_size_value=notional,
            position_size_units=units,
            leverage=leverage,
            entry_price=close_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_per_trade=risk,
            risk_percent=risk_percent,
            expected_reward=reward,
            reward_risk_ratio=reward_risk_ratio,
            rationale=rationale,
        )
        
        return spec
    
    
    def generate_specs_for_rankings(self, 
                                   ranking: List[Tuple[str, Dict, float]]) -> List[TradeSpec]:
        """
        Generate trade specs for top-ranked stocks.
        
        Args:
            ranking: Ranking from edge_ranker.rank_stocks()
        
        Returns:
            List of TradeSpec objects
        """
        specs = []
        
        for symbol, features, edge_score in ranking:
            try:
                spec = self.generate_trade_spec(features, edge_score)
                specs.append(spec)
            except Exception as e:
                logger.error(f"Error generating spec for {symbol}: {str(e)}")
        
        return specs
