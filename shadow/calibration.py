# shadow/calibration.py
from shadow.schemas import CalibrationRecord


def bucket_confidence(c: float) -> str:
    if c < 0.3:
        return "0.0–0.3"
    if c < 0.6:
        return "0.3–0.6"
    if c < 0.8:
        return "0.6–0.8"
    return "0.8–1.0"


def calibrate(intent, execution, divergence):
    survived = (
        execution.fill_percentage >= 0.8
        and not divergence.direction_flip
        and execution.executed_notional > 0
    )

    if survived:
        failure = None
    elif execution.executed_notional == 0:
        failure = "CONSTRAINT_BLOCK"
    elif divergence.direction_flip:
        failure = "DIRECTION_FLIP"
    else:
        failure = "PARTIAL_FILL"

    return CalibrationRecord(
        run_id=str(intent.intent_id),
        timestamp=intent.timestamp,
        confidence_bucket=bucket_confidence(intent.signal_confidence),
        signal_confidence=intent.signal_confidence,
        survived_execution=survived,
        failure_reason=failure,
        regime=intent.regime,
    )
