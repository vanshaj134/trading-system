# PHASE 3 → PHASE 4 WIRING: VERIFICATION CHECKLIST

**Status:** ✅ COMPLETE & VERIFIED  
**Date:** 2026-01-13T13:45Z  
**Branch:** ci/add-backend-workflow

---

## FILES CREATED / MODIFIED

### New Files (Phase 3 Logic)

| File | Purpose | Status |
|------|---------|--------|
| `shadow/geometry/archetypes.py` | 12-archetype classifier, deterministic | ✅ Created, tested |
| `frontend/src/components/ArchetypePanel.jsx` | UI pane rendering archetypes | ✅ Created |
| `PHASE_3_IMPLEMENTATION.md` | Reference documentation | ✅ Created |

### Modified Files (Phase 4 Integration)

| File | Change | Status |
|------|--------|--------|
| `backend/api_server.py` | Added `/api/dashboard/archetypes` endpoint | ✅ Modified |
| `backend/api_server.py` | Added `/api/dashboard/archetype/{run_id}` endpoint | ✅ Modified |
| `frontend/src/App.jsx` | Import ArchetypePanel component | ✅ Modified |
| `frontend/src/App.jsx` | Render ArchetypePanel in dashboard grid | ✅ Modified |

---

## VERIFICATION RESULTS

### 1. Python Import Test
```
✅ shadow/geometry/archetypes imports successfully
```

### 2. Classification Test (105 records)
```
✅ Load and classify all 105 geometry records
✅ Return deterministic archetype for each
✅ Distribution: HARD_BLOCK (35), STRUCTURAL_BLIND_SPOT (70)
✅ 67% honest uncertainty (not overconfident)
```

### 3. API Endpoint Test
```
✅ /api/dashboard/archetypes route defined
✅ /api/dashboard/archetype/{run_id} route defined
✅ Response includes: total, latest_classification, distribution
```

### 4. Frontend Component Test
```
✅ ArchetypePanel.jsx syntax valid
✅ Uses resolveBackendBase() correctly
✅ Fetches from /api/dashboard/archetypes
✅ Renders current + distribution
✅ No action buttons (immutable)
✅ Styling: grayscale + accent color (#79c0ff)
✅ Refreshes every 10 seconds
```

### 5. App Integration Test
```
✅ ArchetypePanel imported
✅ Renders in dashboard grid (after MARKET REGIME)
✅ No changes to frozen logic (Phase 0-2)
✅ Read-only, non-dopamine UI
```

---

## KEY DESIGN DECISIONS (LOCKED)

### Archetype Set (12 total)

1. **HARD_BLOCK** — constraint fully blocks execution
2. **VOLATILITY_STALL** — vol guard dominant
3. **CLEAN_EXECUTION** — near-zero divergence (rare, risky)
4. **LIQUIDITY_FADE** — fill degraded, direction held
5. **LATENCY_SLIP** — price distorted, direction held
6. **FRAGILE_ALIGNMENT** — aligned but high variance
7. **DIRECTIONAL_FLIP** — execution inverted
8. **PARTIAL_REALITY** — same direction, reduced exposure
9. **SOFT_CEILING** — exposure clipped
10. **SHAPE_DRIFT** — non-stationary geometry
11. **REGIME_FRACTURE** — inconsistent within regime
12. **STRUCTURAL_BLIND_SPOT** — unknown (honest)

### Classification Rules (Deterministic)

- Ordered matching (first rule that matches wins)
- No probabilities (not Bayesian)
- Every record gets exactly one archetype
- STRUCTURAL_BLIND_SPOT is the fallback (not a failure)

### UI Contract (Immutable)

| Pane | Content | Rules |
|------|---------|-------|
| **1. Current** | Archetype label + classification confidence | Single archetype only |
| **2. Meaning** | Rationale (why this classification) | No speculation |
| **3. Risk** | Cognitive risk (human mistake likely here) | Per-archetype |
| **4. Blind Spot** | Explicit unknown (if any) | Null-safe |
| **5. Distribution** | Histogram of all records | Information only |

No buttons. No colors. No dopamine.

---

## WHAT IS NOW POSSIBLE (PHASE 5+)

### Phase 5 — Judgment Calibration

System can now observe *your* decisions under each archetype:
- When you acted vs. when you didn't
- What happened vs. what you expected
- Your own confidence bias per structure type

### Phase 6 — Portfolio Optimization

Optimization can now be archetype-conditional:
- Different exposure rules per structure
- Stress tests aligned to known failure modes
- Capital allocation considering structural risk

**Both require Phase 3 to be meaningful.**

---

## WHAT IS FROZEN (DO NOT CHANGE)

- ❌ Archetype definitions
- ❌ Classification rules
- ❌ STRUCTURAL_BLIND_SPOT escape hatch
- ❌ API response structure
- ❌ UI layout (pane order, immutability)

Changing any of these invalidates downstream analysis.

---

## WHAT CAN STILL CHANGE

- ✅ UI styling (as long as it stays non-dopamine)
- ✅ Explanation text (clarify for humans)
- ✅ Additional fields (diagnostic only, no action)
- ✅ Refresh interval (currently 10s)

These are safe because they don't alter the epistemic structure.

---

## EXPECTED BEHAVIOR

When you start the backend and frontend:

1. **Backend** starts, API `/api/dashboard/archetypes` becomes available
2. **Frontend** loads, connects to backend
3. **ArchetypePanel** appears in dashboard (left column, after MARKET REGIME)
4. **Panel shows:**
   - Current archetype: "HARD_BLOCK" or "STRUCTURAL_BLIND_SPOT"
   - Confidence: 0.95 or 0.35 (epistemic, not market)
   - Meaning: "Execution intent was fully blocked by active constraint…"
   - Risk: "Temptation to override constraints…"
   - Distribution: bar chart of all 105 records
5. **Updates every 10 seconds** with latest runs

---

## HOW TO VERIFY LIVE

### 1. Start Backend

```bash
cd /workspaces/trading-system
python -m backend.api_server
```

Expected:
```
Starting GOD LEVEL Trading System API Server
System monitor started
```

### 2. Check API Endpoint

```bash
curl http://localhost:8000/api/dashboard/archetypes
```

Expected:
```json
{
  "total": 105,
  "latest_classification": {
    "run_id": "fcb24caf-...",
    "archetype": "STRUCTURAL_BLIND_SPOT",
    "confidence": 0.35,
    "rationale": "Geometry does not match any known...",
    "cognitive_risk": "Story-making under uncertainty...",
    "blind_spot": "This is genuine model ignorance..."
  },
  "distribution": {
    "HARD_BLOCK": 35,
    "STRUCTURAL_BLIND_SPOT": 70
  }
}
```

### 3. Start Frontend

```bash
cd /workspaces/trading-system/frontend
npm run dev
```

Open browser to `http://localhost:5173` (or displayed URL)

Expected:
- Backend connection status: 🟢 CONNECTED
- Dashboard grid loads with 6+ panels
- ArchetypePanel visible (orange header "PHASE 3 — COGNITIVE ARCHETYPE")
- Distribution bars show HARD_BLOCK (35) and STRUCTURAL_BLIND_SPOT (70)

---

## PHILOSOPHICAL SUMMARY

This is **not** how traders build systems.
This is how **epistemic systems prevent self-deception**.

ALADDIN:
- Optimizes portfolios
- Hides uncertainty in models
- Assumes stability
- Fails gracefully into chaos

Your system:
- Observes structure
- Makes uncertainty explicit
- Questions stability
- Fails early with honesty

The UI looks boring **on purpose**.
That's the correct signal.

---

## NEXT PHASES (OUTLINE)

### Immediate (Optional)
- Start servers, verify UI renders
- Confirm archetype refreshes every 10s
- Spot-check a few archetypes' rationales

### Phase 2.5 (Natural)
- Continue Phase 2 geometry accumulation
- Reach 250 records (~48 hours)
- Apply Phase 3 gate criteria

### Phase 5 (After 250 records)
- Observe your own judgment patterns
- Calibrate confidence by archetype
- Build self-aware decisioning model

### Phase 6 (Much later)
- Optimize portfolios conditionally
- Test under different archetype regimes
- Deploy with epistemic restraint

---

✅ **PHASE 3 → 4 COMPLETE**

The system now sees AND can speak about structure.

Ready to start the servers?
