# Shadow Execution Engine — Phase 1

This subsystem simulates execution in parallel to Phase 0.

## Rules (Immutable)

- No interaction with Phase 0 state
- No randomness
- Deterministic outputs only
- Append-only storage
- Divergence is the signal, not profit
- Calibration observes; it does not tune

## Failure Modes

If this engine ever:
- Mutates past data
- Depends on wall-clock time
- Produces non-reproducible output
- Allows parameter tuning

**Phase 1 is invalidated.**

## Structure

- `schemas.py`: Data contracts (frozen, immutable)
- `tables.py`: Fixed assumptions (regime-aware)
- `determinism.py`: Hash verification
- `engine.py`: Execution logic (total function)
- `calibration.py`: Survival classification
- `storage.py`: Append-only persistence
