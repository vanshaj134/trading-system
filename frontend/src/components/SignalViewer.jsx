import React, { useState, useEffect } from 'react';
// import apiClient from '../services/api_client';

const SignalViewer = () => {
  const [cycles, setCycles] = useState([
    { id: 'phase_0_run_001' }
  ]);
  const [selectedCycle, setSelectedCycle] = useState('phase_0_run_001');
  const [trace, setTrace] = useState({
    marketData: { AAPL: 375.11, GOOGL: 340.84, MSFT: 384.27, TSLA: 363.12, NVDA: 373.50 },
    features: {},
    signal: { AAPL: 0.84, GOOGL: -0.82 },
    riskApproval: { approved: true },
    regime: 'normal',
    siloAlloc: { capital: 40000 },
    targetPos: { AAPL: 1968.86 },
    orders: [{ symbol: 'AAPL', qty: 1968.86 }],
    liveFill: { symbol: 'AAPL', qty: 1968.86, fill_price: 375.48 },
    shadowFill: { symbol: 'AAPL', qty: 1968.86, fill_price: 375.11 },
    divergence: { price_diff: 0.37, slippage_diff: 0.37 }
  });

  // useEffect(() => {
  //   apiClient.get('/cycles').then(setCycles);
  // }, []);

  // const loadTrace = (cycleId) => {
  //   apiClient.get(`/cycles/${cycleId}/trace`).then(setTrace);
  // };

  return (
    <div className="signal-viewer">
      <h2>Decision Trace</h2>
      <select value={selectedCycle} onChange={(e) => setSelectedCycle(e.target.value)}>
        {cycles.map(c => <option key={c.id} value={c.id}>{c.id}</option>)}
      </select>
      <div className="trace">
        <p>Market Data: {JSON.stringify(trace.marketData)}</p>
        <p>Features: {JSON.stringify(trace.features)}</p>
        <p>Signal: {JSON.stringify(trace.signal)}</p>
        <p>Risk Approval: {JSON.stringify(trace.riskApproval)}</p>
        <p>Regime Context: {JSON.stringify(trace.regime)}</p>
        <p>Silo Allocation: {JSON.stringify(trace.siloAlloc)}</p>
        <p>Target Position: {JSON.stringify(trace.targetPos)}</p>
        <p>Orders: {JSON.stringify(trace.orders)}</p>
        <p>Live Fill: {JSON.stringify(trace.liveFill)}</p>
        <p>Shadow Fill: {JSON.stringify(trace.shadowFill)}</p>
        <p>Divergence: {JSON.stringify(trace.divergence)}</p>
      </div>
    </div>
  );
};

export default SignalViewer;