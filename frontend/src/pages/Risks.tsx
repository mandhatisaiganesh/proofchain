// ─── Risks Page ─────────────────────────────────────────────────────
import { Shield, TrendingUp } from 'lucide-react';
import { useFetch } from '../hooks';
import api from '../api';
import type { Risk } from '../types';

interface Props { workspaceId: string; }

const LEVEL_BADGE: Record<string, string> = {
  CRITICAL: 'badge-red',
  HIGH:     'badge-orange',
  MEDIUM:   'badge-yellow',
  LOW:      'badge-green',
};

function RiskRow({ risk }: { risk: Risk }) {
  const pct = Math.round((risk.probability ?? 0) * 100);
  const probColor =
    pct >= 70 ? 'var(--red)' :
    pct >= 50 ? 'var(--orange)' :
    pct >= 30 ? 'var(--yellow)' : 'var(--green)';

  return (
    <tr>
      <td>
        <div style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: 13 }}>{risk.description}</div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
          {risk.commitment_id}
        </div>
      </td>
      <td>
        <span className={`badge ${LEVEL_BADGE[risk.risk_level] ?? 'badge-gray'}`}>{risk.risk_level}</span>
      </td>
      <td>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div className="progress-bar" style={{ width: 60, height: 4 }}>
            <div className="progress-fill" style={{ width: `${pct}%`, background: probColor }} />
          </div>
          <span style={{ fontSize: 11, color: probColor, fontWeight: 600 }}>{pct}%</span>
        </div>
      </td>
      <td style={{ fontSize: 12, color: 'var(--text-secondary)', maxWidth: 200 }}>{risk.impact}</td>
      <td style={{ fontSize: 12, color: 'var(--text-secondary)', maxWidth: 200 }}>{risk.mitigation}</td>
    </tr>
  );
}

export default function Risks({ workspaceId }: Props) {
  const { data: risks, loading, error, refetch } = useFetch<Risk[]>(
    () => api.risks.list(workspaceId),
    [workspaceId],
  );

  const counts = {
    CRITICAL: (risks ?? []).filter(r => r.risk_level === 'CRITICAL').length,
    HIGH:     (risks ?? []).filter(r => r.risk_level === 'HIGH').length,
    MEDIUM:   (risks ?? []).filter(r => r.risk_level === 'MEDIUM').length,
    LOW:      (risks ?? []).filter(r => r.risk_level === 'LOW').length,
  };

  const sorted = [...(risks ?? [])].sort((a, b) => {
    const ord = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    return ord.indexOf(a.risk_level) - ord.indexOf(b.risk_level);
  });

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 style={{ marginBottom: 4 }}>Risk Center</h2>
          <p className="text-sm text-muted">Capability gaps and delivery risks across all commitments</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Reload</button>
      </div>

      {/* Risk summary cards */}
      {!loading && risks && (
        <div className="metric-grid" style={{ marginBottom: 20 }}>
          {[
            { level: 'CRITICAL', color: 'var(--red)',    bg: 'var(--red-bg)',    count: counts.CRITICAL },
            { level: 'HIGH',     color: 'var(--orange)', bg: 'var(--orange-bg)', count: counts.HIGH },
            { level: 'MEDIUM',   color: 'var(--yellow)', bg: 'var(--yellow-bg)', count: counts.MEDIUM },
            { level: 'LOW',      color: 'var(--green)',  bg: 'var(--green-bg)',  count: counts.LOW },
          ].map(r => (
            <div
              key={r.level}
              className="metric-card"
              style={{ '--metric-accent': r.color, '--metric-icon-bg': r.bg } as React.CSSProperties}
            >
              <div className="metric-icon"><Shield size={16} /></div>
              <span className="metric-label">{r.level}</span>
              <span className="metric-value">{r.count}</span>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        {loading ? (
          <div className="loading-overlay"><div className="spinner" /><span>Assessing risks…</span></div>
        ) : error ? (
          <div className="empty-state">
            <div className="empty-state-icon">⚠</div>
            <h4>{error}</h4>
            <button className="btn btn-secondary btn-sm" onClick={refetch}>Retry</button>
          </div>
        ) : sorted.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🛡</div>
            <h4>No risks identified</h4>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Risk Description</th>
                <th>Level</th>
                <th>Probability</th>
                <th>Impact</th>
                <th>Mitigation</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map(r => <RiskRow key={r.id} risk={r} />)}
            </tbody>
          </table>
        )}
      </div>

      {!loading && risks && risks.length > 0 && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="card-header">
            <span className="card-title"><TrendingUp size={14} /> Risk Distribution</span>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12, height: 80 }}>
              {[
                { level: 'CRITICAL', color: 'var(--red)',    count: counts.CRITICAL },
                { level: 'HIGH',     color: 'var(--orange)', count: counts.HIGH },
                { level: 'MEDIUM',   color: 'var(--yellow)', count: counts.MEDIUM },
                { level: 'LOW',      color: 'var(--green)',  count: counts.LOW },
              ].map(r => {
                const maxCount = Math.max(...Object.values(counts), 1);
                const barH = (r.count / maxCount) * 70;
                return (
                  <div key={r.level} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: r.color }}>{r.count}</span>
                    <div style={{
                      width: '100%', height: barH, background: r.color,
                      borderRadius: '3px 3px 0 0', opacity: 0.8,
                      minHeight: r.count > 0 ? 4 : 0,
                      transition: 'height 0.5s ease',
                    }} />
                    <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{r.level}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
