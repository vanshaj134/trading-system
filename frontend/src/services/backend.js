/**
 * Backend Resolver
 * Derives backend URL from reality, not assumptions
 * Zero placeholders. No hardcoded URLs.
 */

export function resolveBackendBase() {
  const host = window.location.hostname;

  // Codespaces pattern: <prefix>-5173.app.github.dev → <prefix>-8000.app.github.dev
  if (host.includes(".app.github.dev")) {
    const base = host.replace(/-\d+\.app\.github\.dev$/, "");
    return `https://${base}-8000.app.github.dev`;
  }

  // Local dev fallback
  return "http://localhost:8000";
}

export async function fetchState() {
  const base = resolveBackendBase();
  const res = await fetch(`${base}/api/dashboard/state`);

  if (!res.ok) {
    throw new Error(`Backend responded ${res.status}`);
  }

  return res.json();
}

export async function fetchRuns() {
  const base = resolveBackendBase();
  const res = await fetch(`${base}/api/dashboard/runs`);

  if (!res.ok) {
    throw new Error(`Backend responded ${res.status}`);
  }

  return res.json();
}
