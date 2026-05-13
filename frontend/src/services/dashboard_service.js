/**
 * Dashboard State Service
 * Fetches immutable run ledger data for the cognitive dashboard
 * Dynamically resolves API backend in Codespaces environments
 */

function getApiBase() {
  // Explicit env override (for .env files)
  if (import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE;
  }
  
  // Codespaces: transform hostname from 5173-<id> to 8000-<id>
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host.includes('app.github.dev')) {
      const backendHost = host.replace(/-\d+\./, '-8000.');
      return `${window.location.protocol}//${backendHost}`;
    }
  }
  
  // Fallback for localhost
  return 'http://localhost:8000';
}

const API_BASE = getApiBase();

export async function getDashboardState() {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/state`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch dashboard state:', error);
    throw error;
  }
}

export async function getDashboardRuns(limit = 20) {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/runs?limit=${limit}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch runs:', error);
    throw error;
  }
}

export async function getDashboardRun(runId) {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/runs/${runId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch run ${runId}:`, error);
    throw error;
  }
}
