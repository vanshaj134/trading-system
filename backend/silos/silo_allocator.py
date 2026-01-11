# backend/silos/silo_allocator.py

from backend.silos.silo_state import SiloState
from backend.silos.silo_registry import STRATEGY_SILOS

def initialize_silos(total_equity):
    silos = {}
    for strategy_id, config in STRATEGY_SILOS.items():
        silos[strategy_id] = SiloState(config, total_equity)
    return silos