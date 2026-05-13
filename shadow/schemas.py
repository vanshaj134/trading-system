from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class Intent:
    intent_id: UUID
    timestamp: str
    regime: str
    signal_confidence: float
    direction: str  # LONG | SHORT | FLAT
    notional_usd: float
    leverage: float
    constraints_applied: bool
    silence_reason: Optional[str]


@dataclass(frozen=True)
class MarketSnapshot:
    timestamp: str
    bid: float
    ask: float
    volume: int
    volatility: float


@dataclass(frozen=True)
class ShadowExecution:
    intent_id: UUID
    execution_timestamp: str
    executed_direction: str
    executed_notional: float
    entry_price: float
    fill_percentage: float
    slippage_bps: int
    latency_ms: int
    shadow_exposure_usd: float
    mark_to_market_pnl: float
    determinism_hash: str


@dataclass(frozen=True)
class DivergenceRecord:
    run_id: UUID
    timestamp: str
    exposure_delta_usd: float
    exposure_delta_pct: float
    direction_flip: bool


@dataclass(frozen=True)
class CalibrationRecord:
    run_id: str
    timestamp: str
    confidence_bucket: str
    signal_confidence: float
    survived_execution: bool
    failure_reason: Optional[str]
    regime: str
