import React, { useState, useEffect } from 'react';
// import apiClient from '../services/api_client';

const PortfolioMonitor = () => {
  const [silos, setSilos] = useState([
    {
      id: 'trend_following_v1',
      state: 'ACTIVE',
      capital: 40000,
      drawdown: 0.0,
      riskUsed: 0.01,
      contribution: 6227.34,
      divergence: 0.05
    },
    {
      id: 'mean_reversion_v1',
      state: 'ACTIVE',
      capital: 30000,
      drawdown: 0.0,
      riskUsed: 0.008,
      contribution: 2394.59,
      divergence: 0.03
    },
    {
      id: 'stat_arb_v1',
      state: 'ACTIVE',
      capital: 30000,
      drawdown: 0.0,
      riskUsed: 0.012,
      contribution: 1374.61,
      divergence: 0.02
    }
  ]);

  // useEffect(() => {
  //   apiClient.get('/silos').then(setSilos);
  // }, []);

  return (
    <div className="portfolio-monitor">
      <h2>Strategy Silos</h2>
      {silos.map(silo => (
        <div key={silo.id} className="silo-card">
          <h3>{silo.id}</h3>
          <p>State: {silo.state}</p>
          <p>Silo Capital: {silo.capital}</p>
          <p>Current Drawdown: {silo.drawdown}</p>
          <p>Risk Budget Used: {silo.riskUsed}%</p>
          <p>Today's Net Contribution: {silo.contribution}</p>
          <p>Shadow Divergence: {silo.divergence}</p>
        </div>
      ))}
    </div>
  );
};

export default PortfolioMonitor;