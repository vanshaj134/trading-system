import React from 'react';

export default function BeliefStack({ beliefs }) {
  const getLayerDescription = (layer) => {
    const descriptions = {
      'RAW_SIGNAL': 'Raw signal directly from market data',
      'FILTERED_SIGNAL': 'Signal after filtering and risk adjustment',
      'RISK_ADJUSTED_INTENT': 'Final execution intent with portfolio constraints'
    };
    return descriptions[layer] || layer;
  };

  const confidenceColor = (conf) => {
    if (conf >= 0.7) return 'high';
    if (conf >= 0.4) return 'medium';
    return 'low';
  };

  return (
    <div className="belief-stack">
      <h3>Signal Transformation Layers</h3>
      
      <div className="layers">
        {beliefs && beliefs.map((layer, idx) => (
          <div key={idx} className="layer">
            <div className="layer-header">
              <span className="layer-name">{layer.layer.replace(/_/g, ' ')}</span>
              <span className="layer-description">
                {getLayerDescription(layer.layer)}
              </span>
            </div>
            
            <div className="layer-data">
              {Object.keys(layer.data || {}).length > 0 ? (
                Object.entries(layer.data).map(([symbol, value]) => {
                  const conf = layer.confidence?.[symbol] || 0;
                  return (
                    <div key={symbol} className="signal-row">
                      <span className="symbol">{symbol}</span>
                      <span className="value">
                        {typeof value === 'number' ? value.toFixed(4) : value}
                      </span>
                      <div className="confidence-mini">
                        <div 
                          className={`bar ${confidenceColor(conf)}`}
                          style={{ width: `${conf * 100}%` }}
                        />
                        <span className="conf-text">
                          {(conf * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="signal-row empty">
                  <span className="no-data">No signals</span>
                </div>
              )}
            </div>
            
            {idx < beliefs.length - 1 && (
              <div className="layer-arrow">↓</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
