import React from 'react';

export default function SystemConsciousnessBar({ system }) {
  const formatTime = (ts) => {
    if (!ts) return 'Never';
    return new Date(ts).toLocaleTimeString();
  };

  return (
    <div className="system-consciousness-bar">
      <div className="bar-left">
        <h1 className="system-name">{system.name}</h1>
      </div>
      
      <div className="bar-center">
        <span className="badge phase">{system.phase}</span>
        <span className="badge mode">{system.mode}</span>
        <span className={`badge status ${system.status.toLowerCase()}`}>
          {system.status}
        </span>
      </div>
      
      <div className="bar-right">
        <div className="stat">
          <span className="label">Last Run:</span>
          <span className="value">{formatTime(system.last_run)}</span>
        </div>
        <div className="stat">
          <span className="label">Memory Depth:</span>
          <span className="value">{system.run_count} runs</span>
        </div>
      </div>
    </div>
  );
}
