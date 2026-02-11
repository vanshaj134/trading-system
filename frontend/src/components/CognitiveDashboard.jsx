import React, { useState, useEffect } from 'react';
import { getDashboardState } from '../services/dashboard_service';
import SystemConsciousnessBar from './dashboard/SystemConsciousnessBar';
import RegimeCard from './dashboard/RegimeCard';
import BeliefStack from './dashboard/BeliefStack';
import PortfolioSnapshot from './dashboard/PortfolioSnapshot';
import ConstraintStatus from './dashboard/ConstraintStatus';
import SilenceExplanation from './dashboard/SilenceExplanation';
import '../styles/cognitive-dashboard.css';

/*
 * CONSTITUTIONAL PRINCIPLE
 * 
 * This dashboard is not a control surface.
 * It is a truth surface.
 * 
 * Interactions may change perspective,
 * never system state.
 * 
 * If this UI ever causes a different run record,
 * an order to be generated, or an invariant to fail,
 * the UI is wrong. Fix the UI.
 * 
 * The system is the authority.
 * The dashboard witnesses.
 * The user observes.
 * 
 * Anything else violates Phase 0.
 */

export default function CognitiveDashboard() {
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchState = async () => {
      try {
        setLoading(true);
        const dashboardState = await getDashboardState();
        setState(dashboardState);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchState();

    // Poll for updates every 5 seconds (read-only, safe)
    const interval = setInterval(fetchState, 5000);

    return () => clearInterval(interval);
  }, []);

  if (loading && !state) {
    return <div className="cognitive-dashboard loading">Loading system state...</div>;
  }

  if (error && !state) {
    return <div className="cognitive-dashboard error">Error: {error}</div>;
  }

  if (!state) {
    return <div className="cognitive-dashboard error">No state available</div>;
  }

  return (
    <div className="cognitive-dashboard">
      <SystemConsciousnessBar system={state.system} />
      
      <div className="dashboard-grid">
        <div className="left-column">
          <RegimeCard regime={state.regime} />
        </div>
        
        <div className="center-column">
          <BeliefStack beliefs={state.belief_stack} />
        </div>
        
        <div className="right-column">
          <PortfolioSnapshot portfolio={state.portfolio} />
        </div>
      </div>
      
      <div className="bottom-row">
        <div className="constraints-panel">
          <ConstraintStatus constraints={state.constraints} />
        </div>
        
        <div className="silence-panel">
          <SilenceExplanation reason={state.silence_reason} />
        </div>
      </div>
    </div>
  );
}
