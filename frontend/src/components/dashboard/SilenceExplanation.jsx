import React from 'react';

export default function SilenceExplanation({ reason }) {
  const explanations = {
    'NO_EDGE_CONFIRMED': 'The system has not confirmed a statistically significant edge. Inactivity is earned, not accidental.',
    'NO_RUNS_YET': 'System has not yet run. Awaiting initialization.',
    'REGIME_CONFIDENCE_TOO_LOW': 'Market regime confidence is too low for confident decisions. System is observing, not acting.',
    'RISK_BUDGET_CONSTRAINED': 'Risk budget exhausted. The system respects its allocation.',
    'INVARIANT_VIOLATION': 'An invariant violation was detected. This is a circuit-breaker event.',
    'NO_POSITION_SIGNAL': 'Market signals do not warrant any position. Patience is discipline.'
  };

  const explanation = explanations[reason] || 'System is silent by design.';

  return (
    <div className="silence-explanation">
      <h3>System State</h3>
      
      <div className="silence-box">
        <div className="silence-reason">
          {reason}
        </div>
        
        <p className="silence-text">
          {explanation}
        </p>
        
        <div className="silence-note">
          ℹ Inactivity is not failure. It is evidence of discipline.
        </div>
      </div>
    </div>
  );
}
