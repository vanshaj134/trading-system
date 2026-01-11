# backend/support/assertion_guards.py

class InvariantViolation(Exception):
    """Raised when a capital safety invariant is violated."""
    pass


def assert_position_limits(
    positions: dict,
    prices: dict,
    equity: float,
    max_leverage: float,
):
    gross_exposure = sum(
        abs(positions[symbol] * prices.get(symbol, 0))
        for symbol in positions
    )

    if gross_exposure > equity * max_leverage:
        raise InvariantViolation(
            f"Position invariant violated: "
            f"gross_exposure={gross_exposure}, "
            f"limit={equity * max_leverage}"
        )


def assert_risk_limits(
    current_drawdown: float,
    max_drawdown: float,
    var: float,
    var_limit: float,
):
    if current_drawdown > max_drawdown:
        raise InvariantViolation(
            f"Drawdown invariant violated: "
            f"{current_drawdown} > {max_drawdown}"
        )

    if var > var_limit:
        raise InvariantViolation(
            f"VaR invariant violated: "
            f"{var} > {var_limit}"
        )


def assert_execution_limits(
    orders: list,
    fills: list,
    slippage_cap: float,
):
    for order, fill in zip(orders, fills):
        if fill["filled_qty"] > order["qty"]:
            raise InvariantViolation(
                "Execution invariant violated: filled_qty > order_qty"
            )

        if fill["slippage"] > slippage_cap:
            raise InvariantViolation(
                f"Slippage invariant violated: "
                f"{fill['slippage']} > {slippage_cap}"
            )