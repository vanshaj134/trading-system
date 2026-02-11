# shadow/storage.py
import json
from pathlib import Path
from dataclasses import asdict

BASE = Path("shadow_data")


def _write_once(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f"Immutable violation: {path} already exists")
    path.write_text(json.dumps(payload, indent=2, default=str))


def persist_shadow_run(execution, divergence, calibration, geometry=None):
    day = execution.execution_timestamp.split("T")[0]

    _write_once(
        BASE / "executions" / day / f"{execution.intent_id}.json",
        asdict(execution),
    )
    _write_once(
        BASE / "divergence" / day / f"{divergence.run_id}.json",
        asdict(divergence),
    )
    _write_once(
        BASE / "calibration" / day / f"calibration_{calibration.run_id}.json",
        asdict(calibration),
    )
    
    if geometry:
        from shadow.geometry.storage import persist_geometry
        persist_geometry(geometry)
