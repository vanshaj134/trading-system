# shadow/geometry/storage.py
import json
from pathlib import Path
from dataclasses import asdict

BASE = Path("shadow/geometry/records")


def persist_geometry(geometry_record):
    """
    Append-only storage for geometry records.
    
    If file exists: fail loudly.
    """
    day = geometry_record.timestamp.split("T")[0]
    path = BASE / day / f"geometry_{geometry_record.run_id}.json"
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.exists():
        raise RuntimeError(f"Immutable violation: {path} already exists")
    
    path.write_text(json.dumps(asdict(geometry_record), indent=2, default=str))
