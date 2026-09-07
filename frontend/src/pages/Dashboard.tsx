// ─── Dashboard Page ─────────────────────────────────────────────────
import {
  BarChart2, Shield, AlertTriangle, CheckCircle2,
  FileText, Zap, TrendingUp, Activity, Clock, Target,
} from 'lucide-react';
import { useFetch } from '../hooks';
import api from '../api';
import type { DashboardMetrics } from '../types';

interface Props { workspaceId: string; }

function Metric({
  label, value, sub, icon: Icon, accent, iconBg,
}: {
  label: string; value: string | number; sub?: string;
  icon: React.ComponentType<{ size?: number }>;
  accent: string; iconBg: string;
}) {
  return (
    <div className="metric-card" style={{ '--metric-accent': accent, '--metric-icon-bg': iconBg } as React.CSSProperties}>
      <div className="metric-icon"><Icon size={16} /></div>
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
      {sub && <span className="metric-sub">{sub}</span>}
    </div>
  );
}

export default function Dashboard({ workspaceId }: Props) {
  const { data: metrics, loading, error, refetch } = useFetch<DashboardMetrics>(
    () => api.workspaces.metrics(workspaceId),
    [workspaceId],
  );

  if (loading) {
    return (
      <div className="loading-overlay">
        <div className="spinner" />
        <span>Loading intelligence…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">⚠</div>
        <h4>Failed to load metrics</h4>
        <p className="text-sm">{error}</p>
        <button className="btn btn-secondary btn-sm" onClick={refetch}>Retry</button>
      </div>
    );
  }

  const m = metrics!;
  const verifiedPct = m.total_commitments > 0
    ? Math.round((m.verified / m.total_commitments) * 100)
    : 0;
  const healthScore = Math.round(m.compliance_health_score ?? 0);

  return (
    <div className="fade-in">
      {/* Header row */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 style={{ marginBottom: 4 }}>Intelligence Dashboard</h2>
          <p className="text-sm text-muted">
            Real-time commitment intelligence · {m.documents_analyzed} documents analyzed
          </p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={refetch}>
          <Activity size={14} /> Refresh
        </button>
      </div>

      {/* Metric grid */}
      <div className="metric-grid">
        <Metric label="Total Commitments" value={m.total_commitments}
          sub={`from ${m.documents_analyzed} documents`}
          icon={FileText} accent="var(--indigo)" iconBg="var(--indigo-glow)" />
        <Metric label="Verified" value={m.verified}
          sub={`${verifiedPct}% verification rate`}
          icon={CheckCircle2} accent="var(--green)" iconBg="var(--green-bg)" />
        <Metric label="Unverified" value={m.unverified}
          sub="need evidence"
          icon={Clock} accent="var(--yellow)" iconBg="var(--yellow-bg)" />
        <Metric label="Conflicts" value={m.conflicts}
          sub="SLA contradictions"
          icon={AlertTriangle} accent="var(--red)" iconBg="var(--red-bg)" />
        <Metric label="High Risks" value={m.high_risk_count}
          sub={`${m.at_risk} at risk total`}
          icon={Shield} accent="var(--orange)" iconBg="var(--orange-bg)" />
        <Metric label="Evidence Items" value={m.evidence_items}
          sub="grounded citations"
          icon={Target} accent="var(--cyan)" iconBg="var(--cyan-bg)" />
        <Metric label="Open Actions" value={m.open_actions}
          sub="pending approval"
          icon={Zap} accent="var(--purple)" iconBg="var(--purple-bg)" />
        <Metric label="Health Score" value={`${healthScore}%`}
          sub="compliance health"
          icon={BarChart2} accent="var(--green)" iconBg="var(--green-bg)" />
      </div>

      {/* Score row */}
      <div className="grid-2 mb-6">
        <div className="card">
          <div className="card-header">
            <span className="card-title"><TrendingUp size={14} /> Verification Rate</span>
            <span className={`badge ${verifiedPct >= 80 ? 'badge-green' : verifiedPct >= 50 ? 'badge-yellow' : 'badge-red'}`}>
              {verifiedPct}%
            </span>
          </div>
          <div className="card-body">
            <div className="progress-bar" style={{ height: 8, marginBottom: 12 }}>
              <div className="progress-fill" style={{
                width: `${verifiedPct}%`,
                background: verifiedPct >= 80 ? 'var(--green)' : verifiedPct >= 50 ? 'var(--yellow)' : 'var(--red)',
              }} />
            </div>
            <div className="stat-row">
              <span className="stat-row-label">Verified commitments</span>
              <span className="stat-row-value" style={{ color: 'var(--green)' }}>{m.verified}</span>
            </div>
            <div className="stat-row">
              <span className="stat-row-label">Partially verified</span>
              <span className="stat-row-value" style={{ color: 'var(--yellow)' }}>{m.partially_verified}</span>
            </div>
            <div className="stat-row">
              <span className="stat-row-label">Unverified</span>
              <span className="stat-row-value" style={{ color: 'var(--text-muted)' }}>{m.unverified}</span>
            </div>
            <div className="stat-row">
              <span className="stat-row-label">Verification failures</span>
              <span className="stat-row-value" style={{ color: 'var(--red)' }}>{m.verification_failures}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title"><Shield size={14} /> Compliance Health</span>
            <span className={`badge ${healthScore >= 80 ? 'badge-green' : healthScore >= 60 ? 'badge-yellow' : 'badge-red'}`}>
              {healthScore}%
            </span>
          </div>
          <div className="card-body">
            <div className="progress-bar" style={{ height: 8, marginBottom: 12 }}>
              <div className="progress-fill" style={{
                width: `${healthScore}%`,
                background: healthScore >= 80 ? 'var(--green)' : healthScore >= 60 ? 'var(--yellow)' : 'var(--red)',
              }} />
            </div>
            <div className="stat-row">
              <span className="stat-row-label">Conflicts detected</span>
              <span className="stat-row-value" style={{ color: 'var(--red)' }}>{m.conflicts}</span>
            </div>
            <div className="stat-row">
              <span className="stat-row-label">High risk items</span>
              <span className="stat-row-value" style={{ color: 'var(--orange)' }}>{m.high_risk_count}</span>
            </div>
            <div className="stat-row">
              <span className="stat-row-label">False compliance prevented</span>
              <span className="stat-row-value" style={{ color: 'var(--green)' }}>{m.false_compliance_prevented}</span>
            </div>
            <div className="stat-row">
              <span className="stat-row-label">Evidence items</span>
              <span className="stat-row-value">{m.evidence_items}</span>
            </div>
          </div>
        </div>
      </div>

      {/* System status */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><Activity size={14} /> System Status</span>
          <span className="badge badge-green">● Live</span>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-6)' }}>
            {[
              { label: 'Agent Pipeline',  value: '10 agents',       status: 'green', note: 'All healthy' },
              { label: 'RAG Retrieval',   value: 'Active',          status: 'green', note: 'Deterministic fallback' },
              { label: 'Graph Engine',    value: 'NetworkX',        status: 'cyan',  note: `${m.total_commitments + m.evidence_items} nodes` },
            ].map(s => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 22, fontWeight: 700, color: `var(--${s.status})` }}>{s.value}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{s.label}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{s.note}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
