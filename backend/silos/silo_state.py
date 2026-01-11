# backend/silos/silo_state.py

class SiloState:
    def __init__(self, config, total_equity):
        self.capital_fraction = config["capital_fraction"]
        self.capital = config["capital_fraction"] * total_equity
        self.max_leverage = config["max_leverage"]
        self.risk_budget = config["risk_budget"]
        self.max_drawdown = config["max_drawdown"]

        self.equity = self.capital
        self.drawdown = 0.0
        self.status = "ACTIVE"  # ACTIVE | FROZEN | SHUTDOWN