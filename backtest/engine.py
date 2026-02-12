"""
Backtest Engine

Core event-driven simulation loop:
1. For each day in history:
   a) Compute features (no lookahead)
   b) Rank top 5 stocks
   c) Generate trade specs
   d) Enter at next day open
   e) Check exits on current day
   f) Update portfolio equity

Timeline:
- Day D: Features computed, specs generated (PENDING)
- Day D+1: Entry at open, exits checked during [D+1 high, D+1 low]
- Day D+2+: Continue checking exits, update equity
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import json

import sys
sys.path.insert(0, '/workspaces/trading-system')

from data.storage.parquet_store import load_parquet, list_available_symbols
from features.feature_engine import FeatureEngine
from screener.edge_ranker import EdgeRanker
from screener.instrument_decider import InstrumentDecider
from backtest.config import *
from backtest.portfolio import Portfolio
from backtest.trade import Trade, TradeStatus
from backtest.execution_model import ExecutionModel


class BacktestEngine:
    """
    Event-driven backtest engine for historical simulation.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize backtest engine.
        
        Args:
            config: Override default config
        """
        self.config = config or {
            'start_capital': START_CAPITAL,
            'risk_per_trade': RISK_PER_TRADE,
            'commission': COMMISSION,
            'slippage': SLIPPAGE,
            'start_date': START_DATE,
            'end_date': END_DATE,
            'max_open_trades': MAX_OPEN_TRADES,
            'max_portfolio_risk': MAX_PORTFOLIO_RISK,
        }
        
        # Components
        self.store = ParquetStore()
        self.feature_engine = FeatureEngine()
        self.edge_ranker = EdgeRanker()
        self.instrument_decider = InstrumentDecider()
        self.execution = ExecutionModel(
            commission=self.config['commission'],
            slippage=self.config['slippage']
        )
        
        # Portfolio
        self.portfolio = Portfolio(self.config['start_capital'])
        
        # History
        self.all_data: Dict[str, pd.DataFrame] = {}  # symbol -> full history
        self.trade_log: List[Dict] = []
        self.daily_log: List[Dict] = []
        
        print("✓ Backtest engine initialized")
    
    def load_data(self) -> bool:
        """Load historical data for all symbols."""
        print("\n📊 Loading historical data...")
        
        try:
            symbols = self.store.list_available_symbols()
            print(f"   Found {len(symbols)} symbols")
            
            for symbol in symbols:
                df = self.store.load_parquet(symbol)
                if df is not None and len(df) > 0:
                    self.all_data[symbol] = df
            
            print(f"   ✓ Loaded {len(self.all_data)} complete histories")
            return True
        
        except Exception as e:
            print(f"   ✗ Error loading data: {e}")
            return False
    
    def get_historical_slice(self, symbol: str, up_to_date: str) -> Optional[pd.DataFrame]:
        """
        Get historical data available UP TO a specific date.
        
        This prevents lookahead bias - we only use data known at that time.
        
        Args:
            symbol: Stock symbol
            up_to_date: Cutoff date (YYYY-MM-DD)
        
        Returns:
            DataFrame with only dates <= up_to_date
        """
        if symbol not in self.all_data:
            return None
        
        df = self.all_data[symbol]
        if df.index.name != 'date':
            df = df.set_index('date') if 'date' in df.columns else df
        
        # Filter to dates up to and including up_to_date
        cutoff = pd.to_datetime(up_to_date)
        df_slice = df[df.index <= cutoff]
        
        return df_slice if len(df_slice) > 0 else None
    
    def run(self) -> Dict:
        """
        Run backtest simulation.
        
        Returns:
            Results dictionary with metrics and trade log
        """
        print("\n🚀 Starting backtest simulation...")
        print(f"   From {self.config['start_date']} to {self.config['end_date']}")
        print(f"   Initial capital: ₹{self.config['start_capital']:,.0f}")
        
        # Load data
        if not self.load_data():
            print("✗ Failed to load data")
            return {}
        
        # Get date range
        all_dates = set()
        for df in self.all_data.values():
            all_dates.update(df.index if hasattr(df.index, '__iter__') else df['date'])
        
        dates = sorted(pd.to_datetime(list(all_dates)))
        dates = [d for d in dates if pd.to_datetime(self.config['start_date']) <= d <= pd.to_datetime(self.config['end_date'])]
        
        print(f"   Trading {len(dates)} days")
        
        # Simulation loop
        pending_entries: List[tuple] = []  # (symbol, spec, generated_date)
        trades_entered_today: List[int] = []
        
        for i, current_date in enumerate(dates):
            current_str = pd.Timestamp(current_date).strftime('%Y-%m-%d')
            
            # Progress
            if (i + 1) % 250 == 0:
                print(f"   Day {i+1}/{len(dates)} ({current_str}): "
                      f"Capital ₹{self.portfolio.capital:,.0f}, "
                      f"Open trades: {len(self.portfolio.open_trades)}")
            
            # ============ PHASE 1: Check exits on open trades ============
            trades_to_close = []
            
            for trade_id, trade in list(self.portfolio.open_trades.items()):
                if trade.entry_date is None:
                    continue
                
                # Get today's OHLCV for this symbol
                symbol_data = self.get_historical_slice(trade.symbol, current_str)
                if symbol_data is None or len(symbol_data) == 0:
                    continue
                
                try:
                    today_candle = symbol_data.loc[pd.to_datetime(current_str)]
                    if isinstance(today_candle, pd.Series):
                        high = today_candle.get('high', today_candle.get('High', 0))
                        low = today_candle.get('low', today_candle.get('Low', 0))
                    else:
                        continue
                except:
                    continue
                
                # Check exit condition
                exit_info = self.execution.simulate_day(trade, {
                    'high': high,
                    'low': low,
                })
                
                if exit_info:
                    exit_price, exit_reason = exit_info
                    trades_to_close.append((trade_id, exit_price, exit_reason, current_str))
            
            # Close trades
            for trade_id, exit_price, exit_reason, exit_date in trades_to_close:
                self.portfolio.close_trade(
                    trade_id, exit_price, exit_date, exit_reason,
                    self.config['commission']
                )
            
            # ============ PHASE 2: Check entries for yesterday's pending trades ============
            new_trades_entered = []
            
            for symbol, spec, generated_date in pending_entries[:]:
                # Get next day open (i.e., current day open)
                symbol_data = self.get_historical_slice(symbol, current_str)
                if symbol_data is None or len(symbol_data) == 0:
                    continue
                
                try:
                    today_candle = symbol_data.loc[pd.to_datetime(current_str)]
                    if isinstance(today_candle, pd.Series):
                        open_price = today_candle.get('open', today_candle.get('Open', 0))
                    else:
                        continue
                except:
                    continue
                
                if open_price <= 0:
                    continue
                
                # Enter trade
                entry_price = self.execution.get_entry_price(open_price)
                self.portfolio.open_trade(spec['trade_obj'], entry_price, current_str)
                
                new_trades_entered.append(symbol)
                pending_entries.remove((symbol, spec, generated_date))
            
            # ============ PHASE 3: Generate new signals ============
            # Only if portfolio risk allows new trades
            if (len(self.portfolio.open_trades) < self.config['max_open_trades'] and
                self.portfolio.get_total_open_risk() < self.portfolio.capital * self.config['max_portfolio_risk']):
                
                # Compute features for all symbols (only history up to TODAY)
                features_today = {}
                
                for symbol in self.all_data.keys():
                    symbol_data_slice = self.get_historical_slice(symbol, current_str)
                    if symbol_data_slice is None or len(symbol_data_slice) < 252:
                        continue
                    
                    try:
                        features = self.feature_engine.compute_features(symbol_data_slice)
                        if features is not None and len(features) > 0:
                            latest_features = self.feature_engine.get_latest_features(features)
                            if latest_features is not None:
                                features_today[symbol] = latest_features
                    except:
                        continue
                
                # Rank
                if len(features_today) > 0:
                    features_list = list(features_today.values())
                    ranking = self.edge_ranker.rank_stocks(features_list, top_n=5)
                    
                    # Generate specs
                    for i, (symbol, features, edge_score) in enumerate(ranking[:3]):  # Top 3 only
                        if symbol not in [p[0] for p in pending_entries]:  # Avoid duplicate entries
                            try:
                                # Get current price for entry planning
                                symbol_data = self.get_historical_slice(symbol, current_str)
                                if symbol_data is None or len(symbol_data) == 0:
                                    continue
                                
                                current_close = symbol_data.iloc[-1].get('close', symbol_data.iloc[-1].get('Close', 0))
                                
                                spec = self.instrument_decider.generate_trade_spec(features, edge_score)
                                
                                # Store trade object for later entry
                                trade = self.portfolio.create_trade(
                                    symbol=symbol,
                                    date_generated=current_str,
                                    entry_price=current_close,
                                    stop_loss=spec.stop_loss,
                                    take_profit=spec.take_profit,
                                    risk_amount=spec.risk_per_trade,
                                    position_size=int(spec.position_size_units),
                                    leverage=spec.leverage
                                )
                                
                                spec_dict = spec.__dict__.copy()
                                spec_dict['trade_obj'] = trade
                                
                                pending_entries.append((symbol, spec_dict, current_str))
                            
                            except Exception as e:
                                continue
            
            # Update daily equity
            self.portfolio.update_daily_equity()
            
            # Log daily state
            self.daily_log.append({
                'date': current_str,
                'capital': round(self.portfolio.capital, 2),
                'open_trades': len(self.portfolio.open_trades),
                'total_risk': round(self.portfolio.get_total_open_risk(), 2),
            })
        
        print(f"   ✓ Simulation complete")
        
        # Compile trade log
        for trade in self.portfolio.trades:
            self.trade_log.append(trade.to_dict())
        
        return self._compile_results()
    
    def _compile_results(self) -> Dict:
        """Compile final results."""
        metrics = self.portfolio.get_metrics()
        
        return {
            'config': self.config,
            'metrics': metrics,
            'trades': self.trade_log,
            'daily_log': self.daily_log,
            'equipment': {
                'total_trades_executed': len(self.trade_log),
                'total_days_simulated': len(self.daily_log),
            }
        }
    
    def print_results(self):
        """Print summary results."""
        results = self.portfolio.get_metrics()
        
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Capital:        ₹{self.config['start_capital']:>15,.0f}")
        print(f"Final Capital:          ₹{results['total_capital']:>15,.0f}")
        print(f"Total Return:           {results['total_return']:>15.2%}")
        print(f"CAGR:                   {results['cagr']:>15.2%}")
        print(f"Annual Volatility:      {results['ann_volatility']:>15.2%}")
        print(f"Sharpe Ratio:           {results['sharpe_ratio']:>15.2f}")
        print(f"Max Drawdown:           {results['max_drawdown']:>15.2%}")
        print("-"*60)
        print(f"Total Trades:           {results['total_trades']:>15}")
        print(f"Winning Trades:         {results['winning_trades']:>15}")
        print(f"Losing Trades:          {results['losing_trades']:>15}")
        print(f"Win Rate:               {results['win_rate']:>15.2%}")
        print(f"Avg R-Multiple:         {results['avg_r_multiple']:>15.2f}")
        print(f"Profit Factor:          {results['profit_factor']:>15.2f}")
        print(f"Total Fees:             ₹{results['total_fees']:>15,.0f}")
        print("="*60)
        
        # Validation vs benchmarks
        print("\n✓ BENCHMARK VALIDATION:")
        print(f"  CAGR > 18%?             {'✓ PASS' if results['cagr'] > 0.18 else '✗ FAIL'} ({results['cagr']:.2%})")
        print(f"  Sharpe > 1.3?           {'✓ PASS' if results['sharpe_ratio'] > 1.3 else '✗ FAIL'} ({results['sharpe_ratio']:.2f})")
        print(f"  Max DD < 25%?           {'✓ PASS' if results['max_drawdown'] < 0.25 else '✗ FAIL'} ({results['max_drawdown']:.2%})")
        print(f"  Win Rate > 48%?         {'✓ PASS' if results['win_rate'] > 0.48 else '✗ FAIL'} ({results['win_rate']:.2%})")
        print("="*60 + "\n")


if __name__ == "__main__":
    engine = BacktestEngine()
    results = engine.run()
    engine.print_results()
    
    # Save results
    with open('/workspaces/trading-system/backtest/results.json', 'w') as f:
        def serialize(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            if isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat()
            return str(obj)
        
        json.dump(results, f, indent=2, default=serialize)
    
    print("✓ Results saved to backtest/results.json")
