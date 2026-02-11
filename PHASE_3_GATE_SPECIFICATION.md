# PHASE 3 GATE SPECIFICATION

**Document Status:** Formal, Locked  
**Date:** 2026-01-12  
**Scope:** Determines when Phase 3 (Interpretive Geometry) unlocks from Phase 2 (Geometry Accumulation)

---

## 1. PHASE 3 STATE MODEL

### 🔒 LOCKED (Default)

- Geometry accumulating only
- Phase 2 continues
- No interpretation allowed
- No UI changes

### 🔓 UNLOCKED

- Stability or non-stationarity proven
- Phase 3 becomes eligible
- No execution logic changes

### ▶️ ACTIVE

- Phase 3 interpretation permitted
- Execution logic **remains frozen**
- UI allowed to expose taxonomy only

---

## 2. ENTRY PREREQUISITES (Hard Gate)

Phase 3 **cannot unlock** unless **all** are true:

- [ ] Geometry records ≥ **250**
- [ ] ≥ **70 records per regime** (minimum)
- [ ] Schema unchanged since Phase 2 start
- [ ] Determinism hashes verified (random 10% sample)
- [ ] Phase 2.5 re-run with identical criteria (no threshold drift)

**If any fail:** Phase 2 continues accumulating.

---

## 3. STABILITY CRITERIA (Unlock Path A: Stabilized)

Geometry is **STABILIZED** if **ALL** hold:

### A. Envelope Convergence

**Criterion:** Change in mean and variance of L1 and L∞ norms between first 40% and last 40% of records **≤ 10%**

- Calculate: first_40_percent = records[0:int(0.4*n)]
- Calculate: last_40_percent = records[int(0.6*n):]
- Metric: |mean(last_40) - mean(first_40)| / mean(first_40) ≤ 0.10
- Metric: |var(last_40) - var(first_40)| / max(var(first_40), 0.01) ≤ 0.10
- Both L1 and L∞ must pass

**Status:** ✅ if both norms ≤ 10% drift

---

### B. Shape Closure

**Criterion:** No new divergence shape classes appear after record index ≥ 40%

- Shape classes: {SAME, STALL, PARTIAL, FLIP, ...}
- Baseline: set of classes in first 40% of records
- Check: does last 60% introduce any class not in baseline?

**Status:** ✅ if no new classes in final 60%

---

### C. Regime Locality

**Criterion:** Geometry envelopes remain regime-bounded

For each regime:
- Early window: first 50% of regime-specific records
- Late window: last 50% of regime-specific records
- Envelope: (min L∞, max L∞) for that regime in each window
- Range expansion: (late_range - early_range) / early_range

**Status:** ✅ if all regimes have ≤ 20% envelope expansion

---

### UNLOCK PATH A VERDICT

If A + B + C all pass:

```
Status: PHASE 3 UNLOCKED (STABLE GEOMETRY)
Interpretation permitted.
Execution logic remains frozen.
```

---

## 4. PERSISTENT NON-STATIONARITY CRITERIA (Unlock Path B)

Non-stationarity is **DECLARED** if **ANY** hold:

### A. Envelope Drift (Asymptotic Failure)

**Criterion:** Geometry envelopes continue expanding/oscillating beyond 250 records

- Track: max L∞ value seen so far
- Windows: records [1:100], [100:150], [150:200], [200:250]
- Check: is max value increasing across all windows?
- Pattern: no asymptotic behavior

**Status:** ✓ if max continues rising (no plateau)

---

### B. Shape Mutation (New Classes)

**Criterion:** New divergence shape classes appear after record 200

- Baseline: classes in records [1:200]
- Check: do records [201:250+] introduce new classes?

**Status:** ✓ if new shapes emerge late

---

### C. Regime Leakage (Boundary Erosion)

**Criterion:** Geometry distributions overlap across regimes

For each pair of regimes:
- Regime A envelope: (min, max) L∞
- Regime B envelope: (min, max) L∞
- Overlap: max(min_A, min_B) < min(max_A, max_B)?

**Status:** ✓ if envelope overlap detected

---

### UNLOCK PATH B VERDICT

If **any** of A, B, or C are true:

```
Status: PHASE 3 UNLOCKED (NON-STATIONARY GEOMETRY)
Non-stationarity declared, not failure.
Becomes object of Phase 3 analysis.
Execution logic remains frozen.
```

---

## 5. PHASE 3 SCOPE (Explicit Limits)

### ✅ Phase 3 IS ALLOWED TO

- Classify divergence shapes
- Compute frequency distributions
- Map regime → geometry profiles
- Declare stability vs instability
- Measure confidence misalignment patterns (descriptive)
- Build static atlases

### ❌ Phase 3 IS STRICTLY FORBIDDEN TO

- Change execution parameters
- Adjust thresholds
- Tune weights
- Suggest strategies
- Map geometry → action
- Claim alpha or edge
- Modify backend, workflows, or frontend control surfaces

**Phase 3 is epistemic, not operational.**

---

## 6. RE-CHECK PROTOCOL

### Primary Re-check: 250 Records

**Trigger:** When geometry file count ≥ 250

**Action:**
1. Run Phase 2.5 stability check (identical criteria, no threshold drift)
2. Evaluate Unlock Path A OR Unlock Path B
3. Log outcome (one sentence only):

   - "Geometry stabilized."
   - "Geometry did not stabilize."

4. No interpretation. No re-negotiation. No hedging.

### Continued Accumulation (If Inconclusive)

If at 250 records neither stabilization nor non-stationarity is conclusive:

- Phase 2 continues
- Next re-check at 350 records
- Maximum waiting period: 500 records (at which point decision is forced)

---

## 7. PHASE 2.5 RE-CHECK (Identical to Phase 2.5)

**Unchanged criteria from Phase 2.5:**

```
Criterion 1: Norm Convergence
  L1 mean change < 10%
  L1 var change < 10%
  L∞ mean change < 10%
  L∞ var change < 10%
  
Criterion 2: Envelope Saturation
  No new max L∞ after first 40% of records
  
Criterion 3: Shape Recurrence
  Direction delta class proportions change < 15%
  
Criterion 4: Regime Locality
  Envelope expansion per regime < 20%
```

If all four pass → **STABILIZED**  
If any two fail → **NOT STABILIZED**

---

## 8. FORBIDDEN ACTIONS DURING PHASE 2

Until one of the unlock paths triggers:

- ❌ No Phase 3 code changes
- ❌ No UI modifications
- ❌ No interpretation documents
- ❌ No strategy proposals
- ❌ No "what if" experiments
- ❌ No narrative building

**Silence is correct. Restraint is progress.**

---

## 9. WHAT HAPPENS AFTER UNLOCK

### If Path A (Stabilized)

1. Phase 3 becomes ACTIVE
2. Divergence atlas generated (static)
3. Shape taxonomy defined
4. Regime profiles documented
5. Confidence miscalibration patterns surfaced (descriptive)
6. Next gate: Phase 4 (Confidence Calibration)

### If Path B (Non-Stationary)

1. Phase 3 becomes ACTIVE
2. Non-stationarity modes analyzed
3. Root cause investigation (epistemic only)
4. May trigger redesign of geometry or regime definitions
5. OR may declare system unfit for capital
6. Next gate: Redesign decision or Phase 4

---

## 10. IMPLEMENTATION CHECKPOINT

This specification is **locked in place** and constitutes the sole gate for Phase 3 unlock.

No changes to thresholds, criteria, or timing without explicit override.

**Next event:** 250 geometry records accumulated, Phase 2.5 re-run, one sentence logged.

---

**End of Specification**
