// ─── Commitments Page ───────────────────────────────────────────────
import { useState } from 'react';
import { CheckCircle2, Clock, AlertTriangle, Search, ChevronRight } from 'lucide-react';
import { useFetch } from '../hooks';
import api from '../api';
import type { Commitment, CommitmentDetail } from '../types';

interface Props { workspaceId: string; }

const STATUS_BADGE: Record<string, string> = {
  VERIFIED:     'badge-green',
  UNVERIFIED:   'badge-yellow',
  CONFLICT:     'badge-red',
  PENDING:      'badge-gray',
  IN_PROGRESS:  'badge-cyan',
};

const STATUS_ICON: Record<string, React.ComponentType<{ size?: number }>> = {
  VERIFIED:    CheckCircle2,
  UNVERIFIED:  Clock,
  CONFLICT:    AlertTriangle,
};

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 80 ? 'var(--green)' : pct >= 50 ? 'var(--yellow)' : 'var(--red)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <div className="progress-bar" style={{ width: 60, height: 4 }}>
        <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span style={{ fontSize: 11, color, fontWeight: 600 }}>{pct}%</span>
    </div>
  );
}

function CommitmentDetailPanel({ wsId, commitmentId, onClose }: {
  wsId: string; commitmentId: string; onClose: () => void;
}) {
  const { data, loading } = useFetch<CommitmentDetail>(
    () => api.commitments.get(wsId, commitmentId),
    [commitmentId],
  );

  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)',
        zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{ width: '100%', maxWidth: 800, maxHeight: '85vh', display: 'flex', flexDirection: 'column' }}
        onClick={e => e.stopPropagation()}
      >
        {loading ? (
          <div className="loading-overlay"><div className="spinner" /></div>
        ) : data ? (
          <>
            <div className="card-header">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span className={`badge ${STATUS_BADGE[data.commitment.status] ?? 'badge-gray'}`}>
                    {data.commitment.status}
                  </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>
                    {data.commitment.id}
                  </span>
                </div>
                <h3>{data.commitment.title}</h3>
              </div>
              <button className="btn btn-ghost btn-sm" onClick={onClose}>✕</button>
            </div>
            <div style={{ flex: 1, overflow: 'auto', padding: 'var(--space-5) var(--space-6)' }}>
              <p className="text-sm" style={{ marginBottom: 16, lineHeight: 1.7 }}>
                {data.commitment.description}
              </p>

              <div className="grid-2" style={{ marginBottom: 20 }}>
                {[
                  ['Stakeholder', data.commitment.stakeholder],
                  ['Deliverable', data.commitment.deliverable],
                  ['Timeline', data.commitment.timeline],
                  ['Source', data.commitment.source_document],
                  ['Confidence', `${Math.round(data.commitment.confidence * 100)}%`],
                  ['Verification', data.commitment.verification_method ?? '—'],
                ].map(([k, v]) => (
                  <div key={k} className="stat-row" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 2 }}>
                    <span className="text-xs text-muted">{k}</span>
                    <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>{v || '—'}</span>
                  </div>
                ))}
              </div>

              {data.commitment.sla_terms?.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <div className="text-xs text-muted" style={{ marginBottom: 8 }}>SLA TERMS</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {data.commitment.sla_terms.map((t, i) => (
                      <span key={i} className="badge badge-cyan">{t}</span>
                    ))}
                  </div>
                </div>
              )}

              {data.evidence.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <div className="text-xs text-muted" style={{ marginBottom: 8 }}>EVIDENCE ({data.evidence.length})</div>
                  {data.evidence.slice(0, 3).map(ev => (
                    <div key={ev.id} style={{ marginBottom: 10 }}>
                      <div className="evidence-quote">{ev.text}</div>
                      <div className="evidence-source">
                        📄 {ev.source_document} · relevance {Math.round(ev.relevance_score * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {data.risks.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <div className="text-xs text-muted" style={{ marginBottom: 8 }}>RISKS ({data.risks.length})</div>
                  {data.risks.map(r => (
                    <div key={r.id} className="stat-row">
                      <span className="stat-row-label">{r.description}</span>
                      <span className={`badge badge-${r.risk_level === 'CRITICAL' ? 'red' : r.risk_level === 'HIGH' ? 'orange' : r.risk_level === 'MEDIUM' ? 'yellow' : 'green'}`}>
                        {r.risk_level}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {data.actions.length > 0 && (
                <div>
                  <div className="text-xs text-muted" style={{ marginBottom: 8 }}>REQUIRED ACTIONS ({data.actions.length})</div>
                  {data.actions.map(a => (
                    <div key={a.id} style={{ marginBottom: 8 }}>
                      <div style={{ fontWeight: 500, fontSize: 13, color: 'var(--text-primary)' }}>{a.title}</div>
                      <div className="text-sm text-muted">{a.description}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default function Commitments({ workspaceId }: Props) {
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<string | null>(null);

  const { data: commitments, loading, error, refetch } = useFetch<Commitment[]>(
    () => api.commitments.list(workspaceId, statusFilter || undefined),
    [workspaceId, statusFilter],
  );

  const filtered = (commitments ?? []).filter(c =>
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.stakeholder?.toLowerCase().includes(search.toLowerCase()),
  );

  const statuses = ['', 'VERIFIED', 'UNVERIFIED', 'CONFLICT'];

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 style={{ marginBottom: 4 }}>Commitments</h2>
          <p className="text-sm text-muted">{commitments?.length ?? 0} commitment obligations extracted</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Reload</button>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {statuses.map(s => (
          <button
            key={s}
            className={`btn btn-sm ${statusFilter === s ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setStatusFilter(s)}
          >
            {s || 'All'}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <div style={{ position: 'relative' }}>
          <Search size={13} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              padding: '6px 10px 6px 30px', background: 'var(--bg-card)',
              border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)', fontSize: 13, outline: 'none', fontFamily: 'var(--font-sans)',
            }}
          />
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div className="loading-overlay"><div className="spinner" /><span>Extracting commitments…</span></div>
        ) : error ? (
          <div className="empty-state">
            <div className="empty-state-icon">⚠</div>
            <h4>{error}</h4>
            <button className="btn btn-secondary btn-sm" onClick={refetch}>Retry</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📋</div>
            <h4>No commitments found</h4>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Status</th>
                <th>Stakeholder</th>
                <th>Confidence</th>
                <th>Source</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(c => {
                const StatusIcon = STATUS_ICON[c.status] ?? Clock;
                return (
                  <tr key={c.id} onClick={() => setSelected(c.id)} style={{ cursor: 'pointer' }}>
                    <td>
                      <div style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: 13 }}>
                        {c.title}
                      </div>
                      <div className="text-xs text-muted" style={{ marginTop: 2, fontFamily: 'var(--font-mono)' }}>{c.id}</div>
                    </td>
                    <td>
                      <span className={`badge ${STATUS_BADGE[c.status] ?? 'badge-gray'}`}>
                        <StatusIcon size={10} /> {c.status}
                      </span>
                    </td>
                    <td style={{ fontSize: 12 }}>{c.stakeholder || '—'}</td>
                    <td><ConfidenceBar value={c.confidence ?? 0} /></td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>{c.source_document || '—'}</td>
                    <td><ChevronRight size={14} style={{ color: 'var(--text-muted)' }} /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {selected && (
        <CommitmentDetailPanel
          wsId={workspaceId}
          commitmentId={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}
