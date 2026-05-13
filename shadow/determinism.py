# shadow/determinism.py
import json
import hashlib
from dataclasses import asdict
from uuid import UUID


def _canonical_json(obj) -> str:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def compute_determinism_hash(
    intent,
    market_snapshot,
    logic_version: str,
    table_versions: dict,
) -> str:
    payload = {
        "intent": asdict(intent),
        "market_snapshot": asdict(market_snapshot),
        "logic_version": logic_version,
        "table_versions": table_versions,
    }

    canonical = _canonical_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
