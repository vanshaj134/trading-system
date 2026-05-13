# backend/pipelines/trading_pipeline.py

import logging
from backend.core.portfolio_optimizer import PortfolioOptimizer
from backend.core.signal_generators import generate_signals
from backend.core.risk_engine import apply_risk
from backend.core.order_management import build_orders
from backend.core.execution_engine import execute_orders
from backend.support.assertion_guards import (
    assert_position_limits,
    assert_risk_limits,
    assert_execution_limits,
    InvariantViolation,
)
from shadow.shadow_pipeline import run_shadow_pipeline
from shadow.divergence_report import compute_divergence
from backend.support.capital_governor import CapitalGovernor
from backend.silos.silo_allocator import initialize_silos
from backend.silos.silo_enforcer import enforce_silo_limits

logger = logging.getLogger(__name__)

class TradingPipeline:
    def __init__(self, config, mode: str):
        self.mode = mode  # "live" | "backtest"
        self.config = config

        self.optimizer = PortfolioOptimizer(
            risk_budget=config["risk_budget"],
            gross_exposure_limit=config["gross_exposure_limit"],
            instrument_cap=config["instrument_cap"],
        )

        self.capital_governor = CapitalGovernor(
            max_capital=config["deploy_capital"],
            max_leverage=config["deploy_max_leverage"],
            max_positions=config["deploy_max_positions"],
        )

        # Initialize silos
        self.silos = initialize_silos(config["deploy_capital"])

    def run(self, market_data, state):
        # Assert system is running
        if hasattr(state, 'system_state'):
            state.system_state.assert_running()

        try:
            # 1. Signals (assume grouped by strategy)
            signals_by_strategy = generate_signals(market_data, state)

            orders = []

            for strategy_id, strategy_signals in signals_by_strategy.items():
                silo = self.silos.get(strategy_id)
                if not silo or silo.status != "ACTIVE":
                    continue

                enforce_silo_limits(silo)

                # 2. Risk filtering / scaling
                approved_signals = apply_risk(
                    signals=strategy_signals,
                    state=state,
                    config=self.config,
                )

                # 3. Portfolio allocation (FCSD Gate 2)
                target_positions = self.optimizer.allocate(
                    signals=approved_signals,
                    volatilities=state.volatility,
                    prices=state.prices,
                    account_equity=silo.equity,
                )

                # Enforce capital governor (global, but per silo)
                # For simplicity, apply per silo
                total_exposure = sum(abs(p) for p in target_positions.values())
                if total_exposure > silo.capital * silo.max_leverage:
                    scale = (silo.capital * silo.max_leverage) / total_exposure
                    for k in target_positions:
                        target_positions[k] *= scale

                # Assert position limits
                assert_position_limits(
                    positions=target_positions,
                    prices=state.prices,
                    equity=silo.equity,
                    max_leverage=silo.max_leverage,
                )

                # Audit logging
                gross_exposure = sum(abs(p) for p in target_positions.values())
                audit_record = {
                    "run_id": getattr(state, 'run_id', 'unknown'),
                    "timestamp": getattr(state, 'timestamp', 'unknown'),
                    "strategy_id": strategy_id,
                    "signals": strategy_signals,
                    "approved_signals": approved_signals,
                    "volatilities": state.volatility,
                    "target_positions": target_positions,
                    "gross_exposure": gross_exposure
                }
                logger.info(f"AUDIT: {audit_record}")

                # 4. Orders
                strategy_orders = build_orders(
                    current_positions=getattr(state, 'positions', {}).get(strategy_id, {}),
                    target_positions=target_positions,
                    prices=state.prices,
                )
                orders.extend(strategy_orders)

            # Shadow execution
            shadow_report = run_shadow_pipeline(
                orders=orders,
                market_data=market_data,
                slippage_model=self.config["shadow_slippage_model"],
            )

            # 5. Execution
            execution_report = execute_orders(
                orders=orders,
                mode=self.mode,
            )

            # Compute divergence
            divergence = compute_divergence(
                live_fills=execution_report.get("fills", []),
                shadow_fills=shadow_report["fills"],
            )

            # Log shadow and divergence
            logger.info(f"SHADOW: {shadow_report}")
            logger.info(f"DIVERGENCE: {divergence}")

            # Assert execution limits after execution
            assert_execution_limits(
                orders=orders,
                fills=execution_report.get("fills", []),
                slippage_cap=self.config["slippage_cap"],
            )

            # Assert risk limits (simplified)
            assert_risk_limits(
                current_drawdown=getattr(state, 'drawdown', 0),
                max_drawdown=self.config["max_drawdown"],
                var=getattr(state, 'var', 0),
                var_limit=self.config["var_limit"],
            )

            return execution_report

        except InvariantViolation as e:
            logger.critical(str(e))
            # state.freeze(reason=str(e))  # Assume state has freeze method
            if hasattr(state, 'system_state'):
                state.system_state.freeze(str(e))
            raise