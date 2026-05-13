import React, { useState, useEffect } from 'react';
// import apiClient from '../services/api_client';

const ExecutionControl = () => {
  const [executionData, setExecutionData] = useState({
    meanLive: 375.48,
    meanShadow: 375.11,
    slippageDist: [0.37, 0.34],
    divergence: 0.05
  });
  const [killReason, setKillReason] = useState('');

  // useEffect(() => {
  //   apiClient.get('/execution/summary').then(setExecutionData);
  // }, []);

  const handleKill = () => {
    if (confirm('Confirm system shutdown?')) {
      // apiClient.post('/system/kill', { reason: killReason });
      alert('System shutdown initiated');
    }
  };

  return (
    <div className="execution-control">
      {/* Section E: Execution vs Shadow */}
      <div className="section execution-shadow">
        <h2>Execution vs Shadow</h2>
        <p>Mean Fill Price Live: {executionData.meanLive}</p>
        <p>Mean Fill Price Shadow: {executionData.meanShadow}</p>
        <p>Slippage Distribution: {JSON.stringify(executionData.slippageDist)}</p>
        <p>Divergence Score: {executionData.divergence}</p>
      </div>

      {/* Section G: Kill Switch */}
      <div className="section kill-switch">
        <h2>Kill Switch</h2>
        <input
          type="text"
          placeholder="Reason for shutdown"
          value={killReason}
          onChange={(e) => setKillReason(e.target.value)}
        />
        <button onClick={handleKill}>SHUTDOWN SYSTEM</button>
      </div>
    </div>
  );
};

export default ExecutionControl;