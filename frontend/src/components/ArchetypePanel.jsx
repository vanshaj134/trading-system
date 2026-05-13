import { useEffect, useState } from "react";
import { resolveBackendBase } from "../services/backend";

/**
 * PHASE 3 ARCHETYPE PANEL
 * 
 * Displays cognitive archetype classification and distribution.
 * Surfaces structural understanding without recommendation.
 */
export function ArchetypePanel() {
  const [archetypes, setArchetypes] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchArchetypes() {
      try {
        const backend = resolveBackendBase();
        const res = await fetch(`${backend}/api/dashboard/archetypes`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setArchetypes(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setArchetypes(null);
      } finally {
        setLoading(false);
      }
    }

    fetchArchetypes();
    const id = setInterval(fetchArchetypes, 10000); // Refresh every 10s
    return () => clearInterval(id);
  }, []);

  if (loading) return <div style={styles.loading}>Loading archetypes…</div>;
  if (error) return <div style={styles.error}>Error: {error}</div>;
  if (!archetypes) return <div style={styles.empty}>No archetype data</div>;

  const latest = archetypes.latest_classification;
  const total = archetypes.total;
  const dist = archetypes.distribution || {};

  return (
    <div style={styles.panel}>
      <div style={styles.header}>
        <h2 style={styles.title}>PHASE 3 — COGNITIVE ARCHETYPE</h2>
        <div style={styles.stat}>
          {total} records classified
        </div>
      </div>

      {latest && (
        <div style={styles.current}>
          <div style={styles.label}>Current Structure</div>
          <div style={styles.archetype}>
            <strong>{latest.archetype}</strong>
          </div>
          <div style={styles.row}>
            <span style={styles.key}>Classification Confidence:</span>
            <span style={styles.value}>{(latest.confidence * 100).toFixed(0)}%</span>
          </div>

          <div style={styles.section}>
            <div style={styles.sectionLabel}>Structural Meaning</div>
            <div style={styles.text}>{latest.rationale}</div>
          </div>

          <div style={styles.section}>
            <div style={styles.sectionLabel}>Cognitive Risk</div>
            <div style={styles.text}>{latest.cognitive_risk}</div>
          </div>

          {latest.blind_spot && (
            <div style={styles.section}>
              <div style={styles.sectionLabel}>Blind Spot (What We Don't Know)</div>
              <div style={styles.text}>{latest.blind_spot}</div>
            </div>
          )}
        </div>
      )}

      <div style={styles.distribution}>
        <div style={styles.label}>Distribution (All Records)</div>
        {Object.entries(dist)
          .sort((a, b) => b[1] - a[1])
          .map(([arch, count]) => {
            const pct = ((count / total) * 100).toFixed(1);
            return (
              <div key={arch} style={styles.archetypeBar}>
                <div style={styles.barLabel}>
                  <span>{arch}</span>
                  <span style={styles.count}>
                    {count} ({pct}%)
                  </span>
                </div>
                <div style={styles.barContainer}>
                  <div
                    style={{
                      ...styles.bar,
                      width: `${(count / total) * 100}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}
      </div>

      <div style={styles.footer}>
        <div style={styles.footerText}>
          ⚠️ Archetypes describe structural risk, not opportunity.
        </div>
        <div style={styles.footerText}>
          They exist to prevent self-deception, not to improve returns.
        </div>
      </div>
    </div>
  );
}

const styles = {
  panel: {
    backgroundColor: "#0d1117",
    border: "1px solid #30363d",
    borderRadius: "4px",
    padding: "16px",
    marginBottom: "16px",
    fontFamily: "'Courier New', monospace",
    fontSize: "13px",
    color: "#c9d1d9",
  },
  header: {
    marginBottom: "16px",
    borderBottom: "1px solid #30363d",
    paddingBottom: "8px",
  },
  title: {
    margin: "0 0 8px 0",
    fontSize: "14px",
    fontWeight: "bold",
    color: "#f0883e",
  },
  stat: {
    fontSize: "11px",
    color: "#8b949e",
  },
  current: {
    marginBottom: "16px",
    paddingBottom: "16px",
    borderBottom: "1px solid #30363d",
  },
  label: {
    fontSize: "11px",
    color: "#8b949e",
    marginBottom: "4px",
    textTransform: "uppercase",
  },
  archetype: {
    fontSize: "18px",
    fontWeight: "bold",
    color: "#79c0ff",
    marginBottom: "12px",
    padding: "8px",
    backgroundColor: "#161b22",
    borderRadius: "2px",
  },
  row: {
    display: "flex",
    justifyContent: "space-between",
    padding: "4px 0",
    fontSize: "12px",
  },
  key: {
    color: "#8b949e",
  },
  value: {
    color: "#79c0ff",
    fontWeight: "bold",
  },
  section: {
    marginTop: "12px",
  },
  sectionLabel: {
    fontSize: "11px",
    color: "#8b949e",
    marginBottom: "4px",
    textTransform: "uppercase",
  },
  text: {
    fontSize: "12px",
    color: "#c9d1d9",
    lineHeight: "1.5",
  },
  distribution: {
    marginTop: "16px",
    paddingTop: "16px",
    borderTop: "1px solid #30363d",
  },
  archetypeBar: {
    marginBottom: "12px",
  },
  barLabel: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: "11px",
    marginBottom: "4px",
    color: "#8b949e",
  },
  count: {
    color: "#79c0ff",
    fontWeight: "bold",
  },
  barContainer: {
    backgroundColor: "#161b22",
    height: "4px",
    borderRadius: "2px",
    overflow: "hidden",
  },
  bar: {
    height: "100%",
    backgroundColor: "#3fb950",
    transition: "width 0.3s ease",
  },
  footer: {
    marginTop: "12px",
    paddingTop: "12px",
    borderTop: "1px solid #30363d",
    fontSize: "11px",
    color: "#8b949e",
  },
  footerText: {
    lineHeight: "1.6",
  },
  loading: {
    padding: "16px",
    color: "#8b949e",
    fontSize: "12px",
  },
  error: {
    padding: "16px",
    color: "#f85149",
    fontSize: "12px",
  },
  empty: {
    padding: "16px",
    color: "#8b949e",
    fontSize: "12px",
  },
};
