import React, { useState, useEffect } from 'react';
import { fetchSystemStatus, runPipeline, fetchSystemHealth } from '../services/api_client';
import './Dashboard.css';

const Dashboard = () => {
  const [systemStatus, setSystemStatus] = useState({
    state: 'LOADING',
    phase: 'PHASE_0',
    positions: {},
    orders: [],
    signal: 0,
    invariants_passed: true,
    timestamp: null,
    execution_time: null
  });
  const [healthData, setHealthData] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const loadStatus = async () => {
    try {
      setError(null);
      const [status, health] = await Promise.all([
        fetchSystemStatus(),
        fetchSystemHealth()
      ]);

      if (status) {
        setSystemStatus(status);
        setLastUpdate(new Date());
      }

      if (health) {
        setHealthData(health);
      }
    } catch (err) {
      setError(`Failed to load system status: ${err.message}`);
      console.error('Dashboard load error:', err);
    }
  };

  const handleRunPipeline = async () => {
    try {
      setIsRunning(true);
      setError(null);
      const result = await runPipeline();
      if (result) {
        setSystemStatus(result);
        setLastUpdate(new Date());
        // Refresh health data after pipeline run
        const health = await fetchSystemHealth();
        if (health) {
          setHealthData(health);
        }
      }
    } catch (err) {
      setError(`Pipeline execution failed: ${err.message}`);
      console.error('Pipeline execution error:', err);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    loadStatus();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'running': return 'success';
      case 'error': return 'error';
      case 'loading': return 'warning';
      default: return 'neutral';
    }
  };

  const getHealthColor = (health) => {
    if (!health) return 'neutral';
    const score = health.application?.health_score || 0;
    if (score > 0.8) return 'success';
    if (score > 0.6) return 'warning';
    return 'error';
  };

  return (
    <div className="dashboard">
      {/* Header with controls */}
      <div className="dashboard-header">
        <div className="header-info">
          <h1>🏆 GOD LEVEL TRADING SYSTEM - Phase 0</h1>
          <div className="system-badges">
            <span className={`badge phase-${systemStatus.phase?.toLowerCase()}`}>
              {systemStatus.phase}
            </span>
            <span className={`badge status-${getStatusColor(systemStatus.state)}`}>
              {systemStatus.state}
            </span>
            <span className="badge shadow-mode">SHADOW MODE</span>
          </div>
        </div>
        <div className="header-controls">
          <button
            onClick={handleRunPipeline}
            disabled={isRunning}
            className={`run-button ${isRunning ? 'running' : ''}`}
          >
            {isRunning ? '🔄 Running Pipeline...' : '▶️ Run Pipeline'}
          </button>
          <button onClick={loadStatus} className="refresh-button">
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{error}</span>
          <button onClick={() => setError(null)} className="error-dismiss">✕</button>
        </div>
      )}

      {/* System Health Overview */}
      <div className="section system-health">
        <h2>🩺 System Health</h2>
        <div className="health-grid">
          <div className="health-card">
            <h3>Overall Status</h3>
            <div className={`health-status ${getHealthColor(healthData)}`}>
              <span className="status-indicator"></span>
              <span className="status-text">
                {healthData?.status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="health-score">
              Health Score: {(healthData?.application?.health_score * 100)?.toFixed(1) || 'N/A'}%
            </div>
          </div>

          <div className="health-card">
            <h3>System Resources</h3>
            <div className="resource-metrics">
              <div className="metric">
                <span className="label">CPU:</span>
                <span className="value">{healthData?.system?.cpu_percent?.toFixed(1) || 'N/A'}%</span>
              </div>
              <div className="metric">
                <span className="label">Memory:</span>
                <span className="value">{healthData?.system?.memory_percent?.toFixed(1) || 'N/A'}%</span>
              </div>
              <div className="metric">
                <span className="label">Disk:</span>
                <span className="value">{healthData?.system?.disk_percent?.toFixed(1) || 'N/A'}%</span>
              </div>
            </div>
          </div>

          <div className="health-card">
            <h3>Pipeline Metrics</h3>
            <div className="pipeline-metrics">
              <div className="metric">
                <span className="label">Last Run:</span>
                <span className="value">
                  {lastUpdate ? lastUpdate.toLocaleTimeString() : 'Never'}
                </span>
              </div>
              <div className="metric">
                <span className="label">Execution Time:</span>
                <span className="value">
                  {systemStatus.execution_time ? `${(systemStatus.execution_time * 1000).toFixed(0)}ms` : 'N/A'}
                </span>
              </div>
              <div className="metric">
                <span className="label">Invariants:</span>
                <span className={`value ${systemStatus.invariants_passed ? 'passed' : 'failed'}`}>
                  {systemStatus.invariants_passed ? 'PASSED' : 'FAILED'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section A: System Status */}
      <div className="section system-status">
        <h2>🔄 System Status</h2>
        <div className="status-grid">
          <div className="status-item">
            <span className="label">State:</span>
            <span className={`value ${getStatusColor(systemStatus.state)}`}>
              {systemStatus.state}
            </span>
          </div>
          <div className="status-item">
            <span className="label">Phase:</span>
            <span className="value">{systemStatus.phase}</span>
          </div>
          <div className="status-item">
            <span className="label">Invariants:</span>
            <span className={`value ${systemStatus.invariants_passed ? 'success' : 'error'}`}>
              {systemStatus.invariants_passed ? 'PASSED' : 'FAILED'}
            </span>
          </div>
          <div className="status-item">
            <span className="label">Last Update:</span>
            <span className="value">
              {systemStatus.timestamp ? new Date(systemStatus.timestamp * 1000).toLocaleTimeString() : 'Never'}
            </span>
          </div>
        </div>
      </div>

      {/* Section B: Current Positions */}
      <div className="section positions">
        <h2>📊 Current Positions</h2>
        {Object.keys(systemStatus.positions || {}).length > 0 ? (
          <div className="positions-table-container">
            <table className="positions-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Position</th>
                  <th>Status</th>
                  <th>Notional</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(systemStatus.positions).map(([symbol, position]) => (
                  <tr key={symbol}>
                    <td className="symbol-cell">{symbol}</td>
                    <td className={`position-cell ${position > 0 ? 'long' : position < 0 ? 'short' : 'flat'}`}>
                      {position.toFixed(6)}
                    </td>
                    <td className="status-cell">
                      {Math.abs(position) > 0.001 ? 'Active' : 'Flat'}
                    </td>
                    <td className="notional-cell">
                      ${(Math.abs(position) * 100000).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-data">
            <p>📭 No active positions</p>
          </div>
        )}
      </div>

      {/* Section C: Pending Orders */}
      <div className="section orders">
        <h2>📋 Pending Orders (Shadow Mode)</h2>
        {(systemStatus.orders || []).length > 0 ? (
          <div className="orders-table-container">
            <table className="orders-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Side</th>
                  <th>Quantity</th>
                  <th>Mode</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {systemStatus.orders.map((order, i) => (
                  <tr key={i}>
                    <td className="symbol-cell">{order.symbol || order.Symbol || 'UNKNOWN'}</td>
                    <td className={`side-cell ${order.side?.toLowerCase()}`}>
                      {order.side?.toUpperCase() || 'UNKNOWN'}
                    </td>
                    <td className="quantity-cell">
                      {(order.quantity || order.qty || order.Quantity || 0).toFixed(6)}
                    </td>
                    <td className="mode-cell">SHADOW</td>
                    <td className="status-cell">PENDING</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-data">
            <p>📭 No pending orders</p>
          </div>
        )}
      </div>

      {/* Section D: Signal Information */}
      <div className="section signals">
        <h2>📈 Signal Information</h2>
        <div className="signal-dashboard">
          <div className="signal-main">
            <div className="signal-gauge">
              <div className="gauge-container">
                <div
                  className="gauge-fill"
                  style={{
                    transform: `rotate(${(systemStatus.signal || 0) * 90}deg)`
                  }}
                ></div>
                <div className="gauge-center">
                  <span className="signal-value">
                    {(systemStatus.signal || 0).toFixed(4)}
                  </span>
                </div>
              </div>
            </div>
            <div className="signal-details">
              <div className="signal-item">
                <span className="label">Latest Signal:</span>
                <span className={`value ${systemStatus.signal > 0 ? 'bullish' : systemStatus.signal < 0 ? 'bearish' : 'neutral'}`}>
                  {systemStatus.signal?.toFixed(4) || '0.0000'}
                </span>
              </div>
              <div className="signal-item">
                <span className="label">Direction:</span>
                <span className={`value ${systemStatus.signal > 0 ? 'bullish' : systemStatus.signal < 0 ? 'bearish' : 'neutral'}`}>
                  {systemStatus.signal > 0.01 ? '🚀 BULLISH' :
                   systemStatus.signal < -0.01 ? '📉 BEARISH' : '⚖️ NEUTRAL'}
                </span>
              </div>
              <div className="signal-item">
                <span className="label">Strength:</span>
                <span className="value">
                  {Math.abs(systemStatus.signal || 0) > 0.1 ? 'STRONG' :
                   Math.abs(systemStatus.signal || 0) > 0.05 ? 'MODERATE' : 'WEAK'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section E: Phase 0 Safety Summary */}
      <div className="section safety-summary">
        <h2>🛡️ Phase 0 Safety Controls</h2>
        <div className="safety-grid">
          <div className="safety-item">
            <span className="safety-icon">👻</span>
            <div className="safety-content">
              <h4>Shadow Mode Active</h4>
              <p>All orders simulated - no real trading executed</p>
            </div>
          </div>
          <div className="safety-item">
            <span className="safety-icon">🔒</span>
            <div className="safety-content">
              <h4>Invariant Enforcement</h4>
              <p>System halts immediately on any safety violation</p>
            </div>
          </div>
          <div className="safety-item">
            <span className="safety-icon">🎯</span>
            <div className="safety-content">
              <h4>Deterministic Operation</h4>
              <p>Same inputs always produce identical outputs</p>
            </div>
          </div>
          <div className="safety-item">
            <span className="safety-icon">📏</span>
            <div className="safety-content">
              <h4>Risk Limits</h4>
              <p>Position sizes capped at safe maximum levels</p>
            </div>
          </div>
          <div className="safety-item">
            <span className="safety-icon">🚫</span>
            <div className="safety-content">
              <h4>No Live Execution</h4>
              <p>Only shadow mode allowed in Phase 0</p>
            </div>
          </div>
          <div className="safety-item">
            <span className="safety-icon">📊</span>
            <div className="safety-content">
              <h4>Comprehensive Monitoring</h4>
              <p>Real-time health tracking and alerting</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;