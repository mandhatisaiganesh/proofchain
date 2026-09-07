// ─── Actions Page ───────────────────────────────────────────────────
import { useState } from 'react';
import { Zap, CheckCircle2, XCircle, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { useFetch, useToast } from '../hooks';
import api from '../api';
import type { Action } from '../types';

interface Props { workspaceId: string; }

const PRIORITY_BADGE: Record<string, string> = {
  CRITICAL: 'badge-red',
  HIGH:     'badge-orange',
  MEDIUM:   'badge-yellow',
  LOW:      'badge-green',
};

const STATUS_BADGE: Record<string, string> = {
  PENDING:   'badge-yellow',
  APPROVED:  'badge-green',
  REJECTED:  'badge-red',
  COMPLETED: 'badge-indigo',
};

function ActionItem({ action, wsId, onRefetch, showToast }: {
  action: Action;
  wsId: string;
  onRefetch: () => void;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleApprove = async (approved: boolean) => {
    setLoading(true);
    try {
      await api.actions.approve(wsId, action.id, approved, notes);
      showToast(`Action ${approved ? 'approved' : 'rejected'}`, 'success');
      onRefetch();
    } catch (e) {
      showToast(e instanceof Error ? e.message : 'Failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const statusCls = action.status?.toLowerCase() as 'pending' | 'approved' | 'rejected' | 'completed';

  return (
    <div className={`action-item ${statusCls}`}>
      <div
        style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}
        onClick={() => setExpanded(!expanded)}
      >
        <Zap size={14} style={{ color: 'var(--yellow)', flexShrink: 0 }} />
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{action.title}</span>
            <span className={`badge ${PRIORITY_BADGE[action.priority] ?? 'badge-gray'}`}>{action.priority}</span>
            <span className={`badge ${STATUS_BADGE[action.status] ?? 'badge-gray'}`}>{action.status}</span>
          </div>
          <div className="text-xs text-muted" style={{ marginTop: 2, fontFamily: 'var(--font-mono)' }}>
            {action.commitment_id} · assigned: {action.assigned_to || 'Unassigned'}
          </div>
        </div>
        {expanded ? <ChevronUp size={14} style={{ color: 'var(--text-muted)' }} />
                  : <ChevronDown size={14} style={{ color: 'var(--text-muted)' }} />}
      </div>

      {expanded && (
        <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--border)' }}>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12, lineHeight: 1.6 }}>
            {action.description}
          </p>

          {action.due_date && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
              <Clock size={12} style={{ color: 'var(--text-muted)' }} />
              <span className="text-xs text-muted">Due: {new Date(action.due_date).toLocaleDateString()}</span>
            </div>
          )}

          {action.status === 'PENDING' && (
            <div style={{ marginTop: 8 }}>
              <textarea
                placeholder="Optional notes…"
                value={notes}
                onChange={e => setNotes(e.target.value)}
                style={{
                  width: '100%', padding: '8px 12px', marginBottom: 10,
                  background: 'var(--bg-elevated)', border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-md)', color: 'var(--text-primary)',
                  fontSize: 12, resize: 'vertical', minHeight: 60,
                  outline: 'none', fontFamily: 'var(--font-sans)',
                }}
              />
              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  className="btn btn-sm"
                  style={{ background: 'var(--green-bg)', color: 'var(--green)', border: '1px solid var(--green-border)' }}
                  disabled={loading}
                  onClick={() => handleApprove(true)}
                >
                  <CheckCircle2 size={13} /> Approve
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  disabled={loading}
                  onClick={() => handleApprove(false)}
                >
                  <XCircle size={13} /> Reject
                </button>
                {loading && <div className="spinner" style={{ width: 16, height: 16 }} />}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function Actions({ workspaceId }: Props) {
  const [filter, setFilter] = useState('');
  const { data: actions, loading, error, refetch } = useFetch<Action[]>(
    () => api.actions.list(workspaceId),
    [workspaceId],
  );
  const { toasts, show, remove } = useToast();

  const filtered = filter
    ? (actions ?? []).filter(a => a.status === filter)
    : (actions ?? []);

  const pending = (actions ?? []).filter(a => a.status === 'PENDING').length;

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 style={{ marginBottom: 4 }}>Actions & Approvals</h2>
          <p className="text-sm text-muted">
            {pending > 0
              ? `${pending} action${pending > 1 ? 's' : ''} require your approval`
              : 'All actions reviewed'}
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Reload</button>
      </div>

      {/* Filter tabs */}
      <div className="tabs">
        {['', 'PENDING', 'APPROVED', 'REJECTED', 'COMPLETED'].map(s => (
          <div
            key={s}
            className={`tab ${filter === s ? 'active' : ''}`}
            onClick={() => setFilter(s)}
          >
            {s || 'All'}
            {s === 'PENDING' && pending > 0 && (
              <span className="nav-badge" style={{ marginLeft: 6, fontSize: 10 }}>{pending}</span>
            )}
          </div>
        ))}
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="spinner" /><span>Loading actions…</span></div>
      ) : error ? (
        <div className="empty-state">
          <div className="empty-state-icon">⚠</div>
          <h4>{error}</h4>
          <button className="btn btn-secondary btn-sm" onClick={refetch}>Retry</button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty-state card" style={{ padding: 48 }}>
          <div className="empty-state-icon">⚡</div>
          <h4>No actions in this view</h4>
        </div>
      ) : (
        filtered.map(a => (
          <ActionItem
            key={a.id}
            action={a}
            wsId={workspaceId}
            onRefetch={refetch}
            showToast={show}
          />
        ))
      )}

      {/* Toast container */}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type}`} onClick={() => remove(t.id)}>
            {t.type === 'success' ? '✓' : t.type === 'error' ? '✕' : 'ℹ'} {t.message}
          </div>
        ))}
      </div>
    </div>
  );
}
