# System Health Dashboard Spec

## Overview
A real-time dashboard to monitor trading system health using the engineering checklist.

## Key Metrics Panels

### 1. Determinism Status
- Last determinism check timestamp
- Status: PASS/FAIL
- Details: Hash of outputs for comparison

### 2. Module Health Matrix
| Module | Output | Downstream | Logged | Tested | Status |
|--------|--------|------------|--------|--------|--------|
| Signal Gen | ✅ | ✅ | ❌ | ⚠️ | Needs Logging |
| Risk Engine | ✅ | ✅ | ❌ | ✅ | Needs Logging |
| Portfolio Opt | ❌ | ❌ | ❌ | ❌ | Stub |
| Execution | ✅ | ✅ | ❌ | ❌ | Needs Testing |

### 3. Invariant Violations
- Position Invariants: Σ|pos|×price ≤ equity×leverage
- Risk Invariants: Drawdown ≤ budget, VaR ≤ limit
- Execution Invariants: Filled ≤ Ordered, Price in range
- Alert count, last violation

### 4. Shadow Mode Comparison
- Simulated vs Live orders divergence %
- Slippage estimate accuracy
- Position drift

### 5. Performance Trifecta
- Equity Curve (chart)
- Risk Curve (VaR, Drawdown)
- Decision Density (trades/time)

### 6. Single Trade Forensic
- Select trade ID
- Show full trace: Data → Signal → Risk → Order → Execution

## Implementation
- Backend: Python/Flask API collecting metrics
- Frontend: React dashboard with charts
- Storage: Time-series DB for metrics history