# backend/silos/silo_enforcer.py

def enforce_silo_limits(silo):
    if silo.drawdown > silo.max_drawdown:
        silo.status = "FROZEN"
        raise RuntimeError(
            f"Silo frozen due to drawdown: {silo.drawdown}"
        )