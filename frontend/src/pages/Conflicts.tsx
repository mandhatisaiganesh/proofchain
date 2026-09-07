// ─── Conflicts Page ─────────────────────────────────────────────────
import { AlertTriangle, Zap } from 'lucide-react';
import { useFetch } from '../hooks';
import api from '../api';
import type { Conflict } from '../types';

interface Props { workspaceId: string; }

const SEVERITY_BADGE: Record<string, string> = {
  CRITICAL: 'badge-red',
  HIGH:     'badge-orange',
  MEDIUM:   'badge-yellow',
  LOW:      'badge-green',
};

function ConflictCard({ conflict }: { conflict: Conflict }) {
  return (
    <div className="conflict-card">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertTriangle size={15} style={{ color: 'var(--red)', flexShrink: 0 }} />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>{conflict.id}</span>
        </div>
        <span className={`badge ${SEVERITY_BADGE[conflict.severity] ?? 'badge-gray'}`}>
          {conflict.severity}
        </span>
      </div>

      <p style={{ fontSize: 14, color: 'var(--text-primary)', fontWeight: 500, marginBottom: 10, lineHeight: 1.5 }}>
        {conflict.description}
      </p>

      <div style={{ marginBottom: 12 }}>
        <div className="text-xs text-muted" style={{ marginBottom: 6 }}>AFFECTED COMMITMENTS</div>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {conflict.commitment_ids.map(id => (
            <span key={id} className="badge badge-indigo" style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>
              {id}
            </span>
          ))}
        </div>
      </div>

      {conflict.resolution_suggestion && (
        <div style={{
          background: 'rgba(99,102,241,0.06)',
          border: '1px solid var(--border-accent)',
          borderRadius: 'var(--radius-md)',
          padding: '10px 14px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
            <Zap size={12} style={{ color: 'var(--indigo-light)' }} />
            <span className="text-xs" style={{ color: 'var(--indigo-light)', fontWeight: 600 }}>SUGGESTED RESOLUTION</span>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {conflict.resolution_suggestion}
          </p>
        </div>
      )}
    </div>
  );
}

export default function Conflicts({ workspaceId }: Props) {
  const { data: conflicts, loading, error, refetch } = useFetch<Conflict[]>(
    () => api.conflicts.list(workspaceId),
    [workspaceId],
  );

  const bySeverity = (s: string) => (conflicts ?? []).filter(c => c.severity === s);
  const critical = bySeverity('CRITICAL');
  const high = bySeverity('HIGH');
  const medium = bySeverity('MEDIUM');
  const low = bySeverity('LOW');

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 style={{ marginBottom: 4 }}>Conflicts Detected</h2>
          <p className="text-sm text-muted">SLA contradictions and commitment inconsistencies</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Reload</button>
      </div>

      {/* Summary pills */}
      {!loading && conflicts && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
          {[
            { label: 'Critical', count: critical.length, cls: 'badge-red' },
            { label: 'High', count: high.length, cls: 'badge-orange' },
            { label: 'Medium', count: medium.length, cls: 'badge-yellow' },
            { label: 'Low', count: low.length, cls: 'badge-green' },
            { label: 'Total', count: conflicts.length, cls: 'badge-gray' },
          ].map(s => (
            <span key={s.label} className={`badge ${s.cls}`} style={{ fontSize: 12, padding: '4px 12px' }}>
              {s.label}: {s.count}
            </span>
          ))}
        </div>
      )}

      {loading ? (
        <div className="loading-overlay"><div className="spinner" /><span>Analyzing conflicts…</span></div>
      ) : error ? (
        <div className="empty-state">
          <div className="empty-state-icon">⚠</div>
          <h4>{error}</h4>
          <button className="btn btn-secondary btn-sm" onClick={refetch}>Retry</button>
        </div>
      ) : (conflicts?.length ?? 0) === 0 ? (
        <div className="empty-state card" style={{ padding: 48 }}>
          <div className="empty-state-icon">✅</div>
          <h4>No conflicts detected</h4>
          <p className="text-sm">All commitments appear consistent</p>
        </div>
      ) : (
        <div>
          {critical.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <h4 style={{ color: 'var(--red)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                <AlertTriangle size={14} /> Critical ({critical.length})
              </h4>
              {critical.map(c => <ConflictCard key={c.id} conflict={c} />)}
            </div>
          )}
          {high.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <h4 style={{ color: 'var(--orange)', marginBottom: 12 }}>High ({high.length})</h4>
              {high.map(c => <ConflictCard key={c.id} conflict={c} />)}
            </div>
          )}
          {medium.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <h4 style={{ color: 'var(--yellow)', marginBottom: 12 }}>Medium ({medium.length})</h4>
              {medium.map(c => <ConflictCard key={c.id} conflict={c} />)}
            </div>
          )}
          {low.length > 0 && (
            <div>
              <h4 style={{ color: 'var(--green)', marginBottom: 12 }}>Low ({low.length})</h4>
              {low.map(c => <ConflictCard key={c.id} conflict={c} />)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
