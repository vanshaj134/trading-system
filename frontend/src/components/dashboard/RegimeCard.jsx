import React from 'react';

export default function RegimeCard({ regime }) {
  const getRegimeExplanation = (label) => {
    const explanations = {
      'UNKNOWN': 'Volatility and trend signals are insufficiently distinct.',
      'LOW_VOL_TREND': 'Low volatility with strong directional trend detected.',
      'HIGH_VOL_CHOP': 'High volatility with choppy, range-bound price action.',
      'MEAN_REVERSION': 'Mean reversion regime with pullback opportunities.',
      'EVENT_RISK': 'Elevated event risk; caution recommended.'
    };
    return explanations[label] || 'Market regime unclear.';
  };

  const confidenceColor = (conf) => {
    if (conf >= 0.7) return 'high';
    if (conf >= 0.4) return 'medium';
    return 'low';
  };

  return (
    <div className="regime-card">
      <h3>Market Regime</h3>
      
      <div className="regime-label">
        <span className="label-text">{regime.label}</span>
      </div>
      
      <div className="confidence-bar">
        <div 
          className={`confidence-fill ${confidenceColor(regime.confidence)}`}
          style={{ width: `${(regime.confidence || 0) * 100}%` }}
        />
        <span className="confidence-text">
          {((regime.confidence || 0) * 100).toFixed(0)}%
        </span>
      </div>
      
      <p className="regime-explanation">
        {getRegimeExplanation(regime.label)}
      </p>
      
      {regime.confidence < 0.3 && (
        <div className="warning">
          ⚠ Low confidence — system awaiting clarity
        </div>
      )}
    </div>
  );
}
