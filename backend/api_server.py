"""
GOD LEVEL TRADING SYSTEM - Production API Server
FastAPI backend with comprehensive monitoring, logging, and safety controls.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import psutil
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market_data_ingestion import load_prices
from core.signal_generators import generate_signal
from core.risk_engine import scale_position
from core.portfolio_optimizer import optimize
from core.order_management import create_orders
from support.assertions import (
    assert_position_limits,
    assert_no_live_orders
)
from support.monitoring import SystemMonitor
from support.run_ledger import RunLedger
from support.regime import RegimeDetector, ConfidenceScorer

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
SYSTEM_HEALTH = Gauge('system_health_score', 'Overall system health score')

# Global state
system_monitor = SystemMonitor()
run_ledger = RunLedger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting GOD LEVEL Trading System API Server")

    # Startup
    system_monitor.start()
    logger.info("System monitor started")

    yield

    # Shutdown
    system_monitor.stop()
    logger.info("System monitor stopped")
    logger.info("GOD LEVEL Trading System API Server stopped")

# Create FastAPI app
app = FastAPI(
    title="GOD LEVEL Trading System API",
    description="Production-ready trading system with Phase 0 safety controls",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure for production

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Request logging and metrics middleware."""
    start_time = time.time()

    # Track active connections
    ACTIVE_CONNECTIONS.inc()

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log request
        logger.info(
            "Request processed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration=process_time
        )

        # Update metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=str(response.status_code)
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(process_time)

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            method=request.method,
            url=str(request.url),
            error=str(e),
            duration=process_time
        )
        raise
    finally:
        ACTIVE_CONNECTIONS.dec()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        url=str(request.url),
        error=str(exc),
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please check logs for details."
        }
    )

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with system heartbeat."""
    return """
    <html>
      <head>
        <title>GOD LEVEL Trading System</title>
        <style>
          body {
            font-family: monospace;
            background: #0e1117;
            color: #c9d1d9;
            padding: 40px;
            margin: 0;
          }
          .ok { color: #3fb950; }
          .warn { color: #d29922; }
          a { color: #58a6ff; text-decoration: none; }
          a:hover { text-decoration: underline; }
          pre {
            background: #161b22;
            padding: 15px;
            border-left: 3px solid #3fb950;
            overflow-x: auto;
          }
          ul { list-style: none; padding: 0; }
          li { margin: 8px 0; }
        </style>
      </head>
      <body>
        <h1 class="ok">⚡ SYSTEM ONLINE</h1>
        
        <h2>Core State</h2>
        <pre>Name:       GOD LEVEL Trading System
Phase:      PHASE_0 (IMMUTABLE)
Mode:       SHADOW
Status:     OPERATIONAL
Authority:  CODE > DASHBOARD > HUMAN</pre>

        <h2>Truth Endpoints</h2>
        <ul>
          <li><a href="/api/dashboard/state">→ /api/dashboard/state</a> (canonical state)</li>
          <li><a href="/api/dashboard/runs">→ /api/dashboard/runs</a> (run history)</li>
          <li><a href="/api/system/status">→ /api/system/status</a> (system health)</li>
        </ul>

        <h2>Philosophy</h2>
        <p class="warn">
          This system does not seek permission.<br/>
          It observes. It accumulates. It decides.
        </p>
      </body>
    </html>
    """

@app.get("/api/system/status")
async def get_system_status():
    """Get current system status and run Phase 0 pipeline."""
    try:
        start_time = time.time()

        # Run Phase 0 pipeline
        logger.info("Starting Phase 0 pipeline execution")

        prices = load_prices("DEMO")
        signal = generate_signal(prices)
        position = scale_position(signal, risk_budget=1.0)
        targets = optimize({"DEMO": position})
        orders = create_orders(targets)

        # Gate 1: Invariant assertions
        positions = {"DEMO": position}
        assert_position_limits(positions, equity=1.0)
        assert_no_live_orders(orders)

        execution_time = time.time() - start_time

        result = {
            "phase": "PHASE_0",
            "state": "RUNNING",
            "positions": positions,
            "orders": orders,
            "signal": signal,
            "timestamp": time.time(),
            "execution_time": execution_time,
            "invariants_passed": True,
            "mode": "SHADOW"
        }

        logger.info(
            "Phase 0 pipeline completed successfully",
            execution_time=execution_time,
            signal=signal,
            position=position
        )

        return result

    except Exception as e:
        logger.error(
            "Phase 0 pipeline failed",
            error=str(e),
            exc_info=True
        )

        return {
            "phase": "PHASE_0",
            "state": "ERROR",
            "error": str(e),
            "timestamp": time.time(),
            "invariants_passed": False,
            "mode": "SHADOW"
        }

@app.get("/api/dashboard/state")
async def get_dashboard_state():
    """
    Get dashboard state from latest run record.
    
    This is the primary read interface for the frontend.
    All data is sourced from the immutable run ledger.
    Frontend is a read-only mirror of this state.
    """
    try:
        latest_run = run_ledger.get_latest_run()
        
        if not latest_run:
            # No runs yet - return initialized empty state
            return {
                "system": {
                    "name": "GOD LEVEL Trading System",
                    "phase": "PHASE_0",
                    "mode": "SHADOW",
                    "status": "INITIALIZED",
                    "last_run": None,
                    "run_count": 0
                },
                "regime": {
                    "label": "UNKNOWN",
                    "confidence": 0.0
                },
                "belief_stack": [
                    {
                        "layer": "RAW_SIGNAL",
                        "data": {}
                    },
                    {
                        "layer": "FILTERED_SIGNAL",
                        "data": {}
                    },
                    {
                        "layer": "RISK_ADJUSTED_INTENT",
                        "data": {}
                    }
                ],
                "portfolio": {
                    "positions": {},
                    "gross_exposure": 0.0,
                    "net_exposure": 0.0
                },
                "constraints": [
                    {"name": "POSITION_LIMIT", "status": "PENDING"},
                    {"name": "DRAWDOWN_LIMIT", "status": "PENDING"}
                ],
                "forbidden_actions": ["LIVE_ORDER_SUBMISSION"],
                "silence_reason": "NO_RUNS_YET"
            }

        # Extract data from latest run
        run_id = latest_run.get("run_id", "unknown")
        timestamp = latest_run.get("timestamp_utc", None)
        regime = latest_run.get("regime", {"label": "UNKNOWN", "confidence": 0.0})
        signals = latest_run.get("signals", {})
        portfolio = latest_run.get("portfolio", {})
        invariants = latest_run.get("invariants", {})
        forbidden_actions = latest_run.get("forbidden_actions", ["LIVE_ORDER_SUBMISSION"])

        # Build belief stack from signal layers
        belief_stack = [
            {
                "layer": "RAW_SIGNAL",
                "data": signals.get("raw", {}),
                "confidence": {k: signals.get("confidence", {}).get(k, 0.0) for k in signals.get("raw", {})}
            },
            {
                "layer": "FILTERED_SIGNAL",
                "data": signals.get("processed", {}),
                "confidence": {k: signals.get("confidence", {}).get(k, 0.0) for k in signals.get("processed", {})}
            },
            {
                "layer": "RISK_ADJUSTED_INTENT",
                "data": portfolio.get("positions", {}),
                "confidence": {k: signals.get("confidence", {}).get(k, 0.0) for k in portfolio.get("positions", {})}
            }
        ]

        # Determine constraint statuses
        constraint_status = "PASS" if not invariants.get("violations") else "FAIL"
        constraints = [
            {"name": "POSITION_LIMIT", "status": constraint_status},
            {"name": "DRAWDOWN_LIMIT", "status": constraint_status},
            {"name": "INVARIANTS", "status": "PASS" if invariants.get("checked", False) else "UNCHECKED"}
        ]

        # Determine silence reason
        silence_reason = "NO_EDGE_CONFIRMED"
        if invariants.get("violations"):
            silence_reason = "INVARIANT_VIOLATION"
        elif regime.get("confidence", 0) < 0.3:
            silence_reason = "REGIME_CONFIDENCE_TOO_LOW"
        elif all(v == 0.0 for v in portfolio.get("positions", {}).values()):
            silence_reason = "NO_POSITION_SIGNAL"

        dashboard_state = {
            "system": {
                "name": "GOD LEVEL Trading System",
                "phase": latest_run.get("phase", "PHASE_0"),
                "mode": latest_run.get("mode", "SHADOW"),
                "status": "OPERATIONAL",
                "last_run": timestamp,
                "run_count": run_ledger.get_run_count()
            },
            "regime": {
                "label": regime.get("label", "UNKNOWN"),
                "confidence": float(regime.get("confidence", 0.0))
            },
            "belief_stack": belief_stack,
            "portfolio": {
                "positions": portfolio.get("positions", {}),
                "gross_exposure": float(portfolio.get("gross_exposure", 0.0)),
                "net_exposure": float(portfolio.get("net_exposure", 0.0))
            },
            "constraints": constraints,
            "forbidden_actions": forbidden_actions,
            "silence_reason": silence_reason
        }

        logger.info(
            "Dashboard state retrieved",
            run_id=run_id,
            regime=regime.get("label"),
            positions=len(portfolio.get("positions", {}))
        )

        return dashboard_state

    except Exception as e:
        logger.error("Dashboard state retrieval failed", error=str(e), exc_info=True)
        return {
            "system": {
                "name": "GOD LEVEL Trading System",
                "phase": "PHASE_0",
                "mode": "SHADOW",
                "status": "ERROR",
                "last_run": None,
                "run_count": 0
            },
            "error": str(e)
        }

@app.get("/api/dashboard/runs")
async def get_dashboard_runs(limit: int = 20):
    """
    Get list of recent runs for time-travel navigation.
    
    Args:
        limit: Number of recent runs to return (default 20)
    
    Returns:
        List of run summaries
    """
    try:
        runs = run_ledger.list_runs(limit=limit)
        
        run_summaries = []
        for run in runs:
            run_summaries.append({
                "run_id": run.get("run_id"),
                "timestamp_utc": run.get("timestamp_utc"),
                "phase": run.get("phase"),
                "mode": run.get("mode"),
                "regime_label": run.get("regime", {}).get("label"),
                "regime_confidence": run.get("regime", {}).get("confidence"),
                "gross_exposure": run.get("portfolio", {}).get("gross_exposure"),
                "net_exposure": run.get("portfolio", {}).get("net_exposure"),
                "invariant_violations": len(run.get("invariants", {}).get("violations", []))
            })
        
        return {
            "total_runs": run_ledger.get_run_count(),
            "returned": len(run_summaries),
            "runs": run_summaries
        }
    
    except Exception as e:
        logger.error("Failed to retrieve runs", error=str(e))
        return {
            "error": str(e),
            "total_runs": 0,
            "returned": 0,
            "runs": []
        }

@app.get("/api/dashboard/runs/{run_id}")
async def get_dashboard_run(run_id: str):
    """
    Get a specific run record by ID.
    
    Args:
        run_id: UUID or partial UUID of the run
    
    Returns:
        Full run record
    """
    try:
        run = run_ledger.get_run(run_id)
        
        if not run:
            return {
                "error": f"Run not found: {run_id}",
                "run_id": run_id
            }
        
        return run
    
    except Exception as e:
        logger.error("Failed to retrieve run", error=str(e), run_id=run_id)
        return {
            "error": str(e),
            "run_id": run_id
        }


async def get_system_health():
    """Get comprehensive system health metrics."""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Application metrics
        health_score = system_monitor.get_health_score()

        health_data = {
            "status": "healthy" if health_score > 0.8 else "degraded",
            "timestamp": time.time(),
            "uptime": time.time() - psutil.boot_time(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024
            },
            "application": {
                "health_score": health_score,
                "phase": "PHASE_0",
                "shadow_mode": True,
                "last_pipeline_run": getattr(system_monitor, 'last_pipeline_time', None)
            }
        }

        # Update Prometheus gauge
        SYSTEM_HEALTH.set(health_score)

        logger.info("Health check completed", health_score=health_score)

        return health_data

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@app.post("/api/system/run-pipeline")
async def run_pipeline():
    """Manually trigger pipeline run."""
    logger.info("Manual pipeline run requested")
    return await get_system_status()

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

@app.get("/api/system/config")
async def get_system_config():
    """Get system configuration (safe, no secrets)."""
    return {
        "phase": "PHASE_0",
        "shadow_mode": True,
        "risk_budget": 1.0,
        "max_position": 0.5,
        "invariants_enabled": True,
        "monitoring_enabled": True,
        "logging_level": "INFO"
    }

@app.get("/api/dashboard/compare/{run_id_a}/{run_id_b}")
async def compare_dashboard_runs(run_id_a: str, run_id_b: str):
    """
    Compare two runs (diff only, no re-execution).
    
    Epistemic interactivity: Understanding system change, not action.
    Returns only comparative analysis of run state.
    """
    try:
        run_a = run_ledger.get_run(run_id_a)
        run_b = run_ledger.get_run(run_id_b)
        
        if not run_a or not run_b:
            return {"error": "One or both runs not found"}
        
        regime_a = run_a.get("regime", {})
        regime_b = run_b.get("regime", {})
        portfolio_a = run_a.get("portfolio", {})
        portfolio_b = run_b.get("portfolio", {})
        
        # Calculate position deltas
        position_delta = {}
        all_symbols = set(list(portfolio_a.get("positions", {}).keys()) + 
                         list(portfolio_b.get("positions", {}).keys()))
        
        for symbol in all_symbols:
            pos_a = portfolio_a.get("positions", {}).get(symbol, 0)
            pos_b = portfolio_b.get("positions", {}).get(symbol, 0)
            delta = pos_b - pos_a
            if delta != 0:
                position_delta[symbol] = delta
        
        comparison = {
            "run_a_id": run_id_a,
            "run_b_id": run_id_b,
            "timestamp_a": run_a.get("timestamp_utc"),
            "timestamp_b": run_b.get("timestamp_utc"),
            "regime_delta": {
                "from": regime_a.get("label"),
                "to": regime_b.get("label"),
                "confidence_change": float(regime_b.get("confidence", 0) - regime_a.get("confidence", 0))
            },
            "position_delta": position_delta,
            "exposure_delta": {
                "gross": float(portfolio_b.get("gross_exposure", 0) - portfolio_a.get("gross_exposure", 0)),
                "net": float(portfolio_b.get("net_exposure", 0) - portfolio_a.get("net_exposure", 0))
            },
            "invariants_changed": run_a.get("invariants") != run_b.get("invariants")
        }
        
        logger.info("Run comparison generated", run_a=run_id_a, run_b=run_id_b)
        return comparison
    
    except Exception as e:
        logger.error("Run comparison failed", error=str(e), exc_info=True)
        return {"error": str(e)}

@app.get("/api/dashboard/explain/{run_id}")
async def explain_silence(run_id: str):
    """
    Explain why a run was silent or why action was taken.
    
    Epistemic interactivity: Make silence legible, not shameful.
    Returns clear explanation of system behavior.
    """
    try:
        run = run_ledger.get_run(run_id)
        
        if not run:
            return {"error": f"Run not found: {run_id}"}
        
        regime = run.get("regime", {})
        portfolio = run.get("portfolio", {})
        orders = run.get("orders", [])
        invariants = run.get("invariants", {})
        
        # Determine reason for behavior
        if invariants.get("violations"):
            reason = "INVARIANT_VIOLATION"
            blocker = invariants.get("violations", [None])[0]
        elif regime.get("confidence", 0) < 0.3:
            reason = "REGIME_CONFIDENCE_TOO_LOW"
            blocker = f"Confidence {regime.get('confidence', 0):.2f} < 0.3 threshold"
        elif all(v == 0.0 for v in portfolio.get("positions", {}).values()):
            reason = "NO_POSITION_SIGNAL"
            blocker = "All positions zero after risk adjustment"
        elif orders:
            reason = "ACTION_TAKEN"
            blocker = f"Executed {len(orders)} orders in shadow mode"
        else:
            reason = "NO_EDGE_CONFIRMED"
            blocker = "Signal magnitude insufficient for action"
        
        explanation = {
            "run_id": run_id,
            "timestamp": run.get("timestamp_utc"),
            "reason": reason,
            "primary_blocker": blocker,
            "details": {
                "regime_label": regime.get("label"),
                "regime_confidence": float(regime.get("confidence", 0)),
                "position_count": len(portfolio.get("positions", {})),
                "gross_exposure": float(portfolio.get("gross_exposure", 0)),
                "net_exposure": float(portfolio.get("net_exposure", 0)),
                "orders_generated": len(orders),
                "invariants_checked": invariants.get("checked", False),
                "invariant_violations": len(invariants.get("violations", []))
            }
        }
        
        logger.info("Silence explanation generated", run_id=run_id, reason=reason)
        return explanation
    
    except Exception as e:
        logger.error("Silence explanation failed", error=str(e), exc_info=True)
        return {"error": str(e)}

@app.get("/api/dashboard/regime/{run_id}")
async def regime_details(run_id: str):
    """
    Explain regime detection for a specific run.
    
    Epistemic interactivity: Make regime labels defensible.
    Returns detection logic and confidence computation.
    """
    try:
        run = run_ledger.get_run(run_id)
        
        if not run:
            return {"error": f"Run not found: {run_id}"}
        
        regime = run.get("regime", {})
        signals = run.get("signals", {})
        
        regime_label = regime.get("label", "UNKNOWN")
        confidence = float(regime.get("confidence", 0))
        
        details = {
            "run_id": run_id,
            "timestamp": run.get("timestamp_utc"),
            "regime": {
                "label": regime_label,
                "confidence": confidence
            },
            "confidence_interpretation": _interpret_confidence(confidence),
            "signals": {
                "raw": signals.get("raw", {}),
                "confidence": signals.get("confidence", {})
            },
            "regime_explanation": _regime_explanation(regime_label)
        }
        
        logger.info("Regime details retrieved", run_id=run_id, regime=regime_label)
        return details
    
    except Exception as e:
        logger.error("Regime details failed", error=str(e), exc_info=True)
        return {"error": str(e)}

def _interpret_confidence(conf: float) -> str:
    """Interpret confidence score for human understanding."""
    if conf >= 0.7:
        return "High confidence — regime is clear"
    elif conf >= 0.4:
        return "Medium confidence — regime is probabilistic"
    elif conf > 0.0:
        return "Low confidence — regime is uncertain"
    else:
        return "No confidence — regime is unknown"

def _regime_explanation(label: str) -> str:
    """Provide human-readable explanation of each regime."""
    explanations = {
        "UNKNOWN": "Market regime is unclear. The system observes but does not act.",
        "LOW_VOL_TREND": "Low volatility with clear directional trend. Favorable for trending strategies.",
        "HIGH_VOL_CHOP": "High volatility with choppy, range-bound action. Difficult environment.",
        "MEAN_REVERSION": "Mean-reverting behavior detected. Pullbacks offer entry points.",
        "EVENT_RISK": "Elevated event risk or gap risk. System assumes defensive posture."
    }
    return explanations.get(label, "Regime interpretation not available.")

# ============================================================
# PHASE 3 — ARCHETYPE ENDPOINTS (COGNITIVE SURFACE)
# ============================================================

@app.get("/api/dashboard/archetypes")
async def get_archetype_classifications():
    """
    Get Phase 3 archetype classifications for all persisted geometry records.
    
    This endpoint surfaces structural understanding without recommendation.
    Each archetype describes a failure mode risk, not a trading opportunity.
    """
    try:
        from shadow.geometry.archetypes import load_and_classify_all_geometries
        
        classifications = load_and_classify_all_geometries()
        
        if not classifications:
            return {
                "total": 0,
                "classifications": [],
                "message": "No geometry records classified yet. Phase 2 accumulation ongoing."
            }
        
        # Group by archetype for analysis (informational only, no optimization)
        archetype_distribution = {}
        for c in classifications:
            archetype_distribution[c.archetype] = archetype_distribution.get(c.archetype, 0) + 1
        
        # Return latest classification + distribution
        latest = classifications[-1] if classifications else None
        
        result = {
            "total": len(classifications),
            "latest_classification": {
                "run_id": latest.run_id,
                "archetype": latest.archetype,
                "confidence": latest.confidence,
                "rationale": latest.rationale,
                "cognitive_risk": latest.cognitive_risk,
                "blind_spot": latest.blind_spot,
            } if latest else None,
            "distribution": archetype_distribution,
            "message": f"Phase 3: {len(classifications)} geometry records classified",
        }
        
        logger.info("Archetype classifications retrieved", total=len(classifications))
        return result
        
    except Exception as e:
        logger.error("Archetype classification failed", error=str(e), exc_info=True)
        return {
            "error": str(e),
            "message": "Phase 3 classification service unavailable"
        }

@app.get("/api/dashboard/archetype/{run_id}")
async def get_archetype_for_run(run_id: str):
    """
    Get the cognitive archetype classification for a specific run's geometry.
    """
    try:
        from shadow.geometry.archetypes import load_and_classify_all_geometries
        
        classifications = load_and_classify_all_geometries()
        
        matching = [c for c in classifications if c.run_id == run_id]
        
        if not matching:
            return {"error": f"No archetype found for run_id: {run_id}"}
        
        c = matching[0]
        
        result = {
            "run_id": c.run_id,
            "archetype": c.archetype,
            "confidence": c.confidence,
            "rationale": c.rationale,
            "cognitive_risk": c.cognitive_risk,
            "blind_spot": c.blind_spot,
        }
        
        logger.info("Archetype retrieved", run_id=run_id, archetype=c.archetype)
        return result
        
    except Exception as e:
        logger.error("Archetype lookup failed", error=str(e), exc_info=True)
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn

    # Development server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )