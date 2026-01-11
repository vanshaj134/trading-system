# backend/support/capital_governor.py

class CapitalGovernor:
    def __init__(
        self,
        max_capital: float,
        max_leverage: float,
        max_positions: int,
    ):
        self.max_capital = max_capital
        self.max_leverage = max_leverage
        self.max_positions = max_positions

    def enforce(self, target_positions: dict):
        if len([p for p in target_positions.values() if p != 0]) > self.max_positions:
            raise RuntimeError("Capital governor: too many positions")

        total_exposure = sum(abs(p) for p in target_positions.values())
        if total_exposure > self.max_capital * self.max_leverage:
            scale = (self.max_capital * self.max_leverage) / total_exposure
            for k in target_positions:
                target_positions[k] *= scale

        return target_positions