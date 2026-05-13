import React from 'react';

export default function ConstraintStatus({ constraints }) {
  const getConstraintDescription = (name) => {
    const descriptions = {
      'POSITION_LIMIT': 'Maximum position size constraint',
      'DRAWDOWN_LIMIT': 'Maximum drawdown constraint',
      'INVARIANTS': 'System invariants check',
      'SLIPPAGE_LIMIT': 'Slippage limit constraint'
    };
    return descriptions[name] || name;
  };

  return (
    <div className="constraint-status">
      <h3>Constraint Status</h3>
      
      <div className="constraints-list">
        {constraints && constraints.map((constraint) => (
          <div key={constraint.name} className={`constraint-item ${constraint.status.toLowerCase()}`}>
            <div className="constraint-indicator">
              <span className={`status-badge ${constraint.status.toLowerCase()}`}>
                {constraint.status}
              </span>
            </div>
            <div className="constraint-info">
              <span className="constraint-name">{constraint.name.replace(/_/g, ' ')}</span>
              <span className="constraint-desc">
                {getConstraintDescription(constraint.name)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
