# backend/silos/silo_registry.py

STRATEGY_SILOS = {
    "trend_following_v1": {
        "capital_fraction": 0.4,
        "max_leverage": 1.2,
        "risk_budget": 0.01,
        "max_drawdown": 0.08,
    },
    "mean_reversion_v1": {
        "capital_fraction": 0.3,
        "max_leverage": 1.0,
        "risk_budget": 0.008,
        "max_drawdown": 0.05,
    },
    "stat_arb_v1": {
        "capital_fraction": 0.3,
        "max_leverage": 1.5,
        "risk_budget": 0.012,
        "max_drawdown": 0.06,
    },
}