import React from 'react';

export default function PortfolioSnapshot({ portfolio }) {
  return (
    <div className="portfolio-snapshot">
      <h3>Portfolio State</h3>
      
      <div className="snapshot-grid">
        <div className="stat-card">
          <span className="stat-label">Gross Exposure</span>
          <span className="stat-value">
            {Math.abs(portfolio.gross_exposure || 0).toFixed(3)}
          </span>
        </div>
        
        <div className="stat-card">
          <span className="stat-label">Net Exposure</span>
          <span className={`stat-value ${(portfolio.net_exposure || 0) >= 0 ? 'long' : 'short'}`}>
            {(portfolio.net_exposure || 0).toFixed(3)}
          </span>
        </div>
      </div>
      
      <div className="positions">
        <h4>Positions</h4>
        {Object.keys(portfolio.positions || {}).length > 0 ? (
          Object.entries(portfolio.positions).map(([symbol, position]) => (
            <div key={symbol} className="position-row">
              <span className="pos-symbol">{symbol}</span>
              <span className={`pos-value ${position >= 0 ? 'long' : 'short'}`}>
                {position.toFixed(4)}
              </span>
            </div>
          ))
        ) : (
          <div className="no-positions">No positions</div>
        )}
      </div>
    </div>
  );
}
