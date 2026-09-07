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
  const isComplianceProhibited = conflict.can_claim_compliance === false;

  return (
    <div className="conflict-card" style={{ borderLeft: isComplianceProhibited ? '4px solid var(--red)' : undefined }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertTriangle size={16} style={{ color: 'var(--red)', flexShrink: 0 }} />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>{conflict.id}</span>
          {conflict.conflict_type && (
            <span className="badge badge-gray" style={{ fontSize: 10 }}>{conflict.conflict_type}</span>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {isComplianceProhibited && (
            <span className="badge badge-red" style={{ fontWeight: 700, letterSpacing: '0.04em' }}>
              ⛔ DO NOT CLAIM COMPLIANCE
            </span>
          )}
          <span className={`badge ${SEVERITY_BADGE[conflict.severity] ?? 'badge-gray'}`}>
            {conflict.severity}
          </span>
        </div>
      </div>

      {isComplianceProhibited && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '8px 12px',
          marginBottom: 14,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          color: '#f87171',
          fontSize: 12,
          fontWeight: 600,
        }}>
          <span>⚠️ CONTRADICTION DETECTED: Internal operational evidence directly conflicts with contractual promise. Under Federal False Claims and SLA provisions, do not certify compliance until mitigated.</span>
        </div>
      )}

      {/* Requirement vs Evidence Comparison */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12, marginBottom: 14 }}>
        <div style={{ background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', padding: '10px 12px', border: '1px solid var(--border)' }}>
          <div className="text-xs text-muted" style={{ fontWeight: 600, marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
            <span>PROMISED REQUIREMENT</span>
            <span style={{ color: 'var(--accent-blue)', fontFamily: 'var(--font-mono)' }}>{conflict.requirement_source || 'Contract / RFP'}</span>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.5, margin: 0 }}>
            "{conflict.requirement_text || conflict.description}"
          </p>
        </div>

        <div style={{ background: 'rgba(239, 68, 68, 0.04)', borderRadius: 'var(--radius-sm)', padding: '10px 12px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          <div className="text-xs text-muted" style={{ fontWeight: 600, marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--red)' }}>CONTRADICTORY EVIDENCE</span>
            <span style={{ color: 'var(--red)', fontFamily: 'var(--font-mono)' }}>{conflict.evidence_source || 'Internal Evidence'}</span>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.5, margin: 0 }}>
            "{conflict.evidence_text || 'Internal records indicate capability is business-hours only or uncertified.'}"
          </p>
        </div>
      </div>

      {(conflict.commitment_ids && conflict.commitment_ids.length > 0) ? (
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
      ) : conflict.commitment_id ? (
        <div style={{ marginBottom: 12 }}>
          <div className="text-xs text-muted" style={{ marginBottom: 6 }}>AFFECTED COMMITMENT</div>
          <span className="badge badge-indigo" style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>
            {conflict.commitment_id}
          </span>
        </div>
      ) : null}

      {(conflict.recommendation || conflict.resolution_suggestion) && (
        <div style={{
          background: 'rgba(99,102,241,0.06)',
          border: '1px solid var(--border-accent)',
          borderRadius: 'var(--radius-md)',
          padding: '10px 14px',
          marginBottom: conflict.resolution_options?.length ? 10 : 0
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
            <Zap size={12} style={{ color: 'var(--indigo-light)' }} />
            <span className="text-xs" style={{ color: 'var(--indigo-light)', fontWeight: 600 }}>RECOMMENDED REMEDIATION</span>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
            {conflict.recommendation || conflict.resolution_suggestion}
          </p>
        </div>
      )}

      {conflict.resolution_options && conflict.resolution_options.length > 0 && (
        <div style={{ padding: '8px 12px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
          <div className="text-xs text-muted" style={{ fontWeight: 600, marginBottom: 6 }}>RESOLUTION OPTIONS:</div>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: 'var(--text-secondary)' }}>
            {conflict.resolution_options.map((opt, i) => (
              <li key={i} style={{ marginBottom: 4 }}>{opt}</li>
            ))}
          </ul>
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
