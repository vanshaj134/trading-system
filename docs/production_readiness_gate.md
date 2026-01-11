# Production Readiness Gate

## Pre-Production Checklist
All items must be GREEN before deploying to live capital.

### 1. Determinism ✅
- [ ] Backtest runs twice with identical outputs
- [ ] No random seeds or timestamps in production code
- [ ] All data pipelines are deterministic

### 2. Module Health ✅
- [ ] All modules produce output and are consumed downstream
- [ ] All critical paths are logged
- [ ] All modules have unit tests passing
- [ ] No dead logic or unused code

### 3. Invariants ✅
- [ ] Position invariants asserted in all position changes
- [ ] Risk invariants monitored continuously
- [ ] Execution invariants validated post-trade
- [ ] Zero violations in shadow mode testing

### 4. Shadow Mode ✅
- [ ] Full pipeline runs without order submission
- [ ] Simulated orders match expected behavior
- [ ] Slippage estimates within 10% of historical
- [ ] No position drift in simulation

### 5. Traceability ✅
- [ ] Every trade can be fully explained end-to-end
- [ ] No "model decided" black boxes
- [ ] Feature values logged for every decision
- [ ] Decision thresholds are explicit

### 6. Edge Validation ✅
- [ ] Time-shuffled backtest shows performance collapse
- [ ] No data leakage or lookahead bias
- [ ] Edge is robust to parameter changes

### 7. Metrics Monitoring ✅
- [ ] Equity, risk, and density curves plotted
- [ ] Alerts for metric deviations
- [ ] Historical comparison available
- [ ] Regime change detection

### 8. Architecture ✅
- [ ] Modules can be removed/swapped predictably
- [ ] No tight coupling between strategies and risk
- [ ] Parameter freezing doesn't break explanations
- [ ] Scaling path is clear

### 9. Operational ✅
- [ ] System health dashboard operational
- [ ] Alerting for all failure modes
- [ ] Rollback procedures tested
- [ ] Monitoring covers all components

## Gate Decision
- If ALL above are ✅: Proceed to production
- If ANY are ❌: Fix before proceeding
- If ⚠️: Review risk and decide

## Sign-off
- Engineer: _______________ Date: _______________
- Risk Officer: ___________ Date: _______________