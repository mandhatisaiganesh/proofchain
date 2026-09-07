// ─── Documents Page ─────────────────────────────────────────────────
import { useState } from 'react';
import { FileText, Upload, Search, Eye, Tag } from 'lucide-react';
import { useFetch } from '../hooks';
import api from '../api';
import type { Document } from '../types';

interface Props { workspaceId: string; }

const DOC_TYPE_COLOR: Record<string, string> = {
  proposal:     'indigo',
  contract:     'cyan',
  sow:          'purple',
  requirements: 'yellow',
  email:        'orange',
  report:       'green',
  memo:         'gray',
};

function DocTypeIcon({ type }: { type: string }) {
  const color = DOC_TYPE_COLOR[type?.toLowerCase()] ?? 'gray';
  return <span className={`badge badge-${color}`}>{type}</span>;
}

function DocumentRow({ doc, onClick }: { doc: Document; onClick: () => void }) {
  return (
    <tr onClick={onClick}>
      <td>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <FileText size={14} style={{ color: 'var(--indigo-light)', flexShrink: 0 }} />
          <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{doc.title}</span>
        </div>
      </td>
      <td><DocTypeIcon type={doc.doc_type} /></td>
      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>{doc.source}</td>
      <td>
        <span className="badge badge-indigo">{doc.chunk_count ?? '—'} chunks</span>
      </td>
      <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>
        {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : '—'}
      </td>
    </tr>
  );
}

function DocumentModal({ doc, onClose }: { doc: Document; onClose: () => void }) {
  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
        zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 24,
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{ width: '100%', maxWidth: 720, maxHeight: '80vh', display: 'flex', flexDirection: 'column' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="card-header">
          <div>
            <h3 style={{ marginBottom: 4 }}>{doc.title}</h3>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <DocTypeIcon type={doc.doc_type} />
              <span className="text-xs text-muted">{doc.source}</span>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>✕</button>
        </div>
        <div style={{ flex: 1, overflow: 'auto', padding: 'var(--space-5) var(--space-6)' }}>
          {doc.metadata && Object.keys(doc.metadata).length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <div className="text-xs text-muted" style={{ marginBottom: 8 }}>METADATA</div>
              {Object.entries(doc.metadata).map(([k, v]) => (
                <div key={k} className="stat-row">
                  <span className="stat-row-label"><Tag size={12} style={{ display: 'inline', marginRight: 4 }} />{k}</span>
                  <span className="stat-row-value text-sm">{v}</span>
                </div>
              ))}
            </div>
          )}
          <div className="text-xs text-muted" style={{ marginBottom: 8 }}>CONTENT</div>
          <pre style={{
            fontFamily: 'var(--font-mono)', fontSize: 12, whiteSpace: 'pre-wrap',
            color: 'var(--text-secondary)', lineHeight: 1.6,
          }}>
            {doc.content}
          </pre>
        </div>
      </div>
    </div>
  );
}

export default function Documents({ workspaceId }: Props) {
  const { data: docs, loading, error, refetch } = useFetch<Document[]>(
    () => api.documents.list(workspaceId),
    [workspaceId],
  );
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<Document | null>(null);

  const filtered = (docs ?? []).filter(d =>
    d.title.toLowerCase().includes(search.toLowerCase()) ||
    d.doc_type.toLowerCase().includes(search.toLowerCase()) ||
    d.source.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 style={{ marginBottom: 4 }}>Documents</h2>
          <p className="text-sm text-muted">{docs?.length ?? 0} documents indexed</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={refetch}><Upload size={13} /> Upload</button>
        </div>
      </div>

      {/* Search */}
      <div style={{ position: 'relative', marginBottom: 20 }}>
        <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
        <input
          type="text"
          placeholder="Search documents..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            width: '100%', padding: '8px 12px 8px 36px',
            background: 'var(--bg-card)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)', color: 'var(--text-primary)',
            fontSize: 13, outline: 'none', fontFamily: 'var(--font-sans)',
          }}
        />
      </div>

      <div className="card">
        {loading ? (
          <div className="loading-overlay"><div className="spinner" /><span>Loading documents…</span></div>
        ) : error ? (
          <div className="empty-state">
            <div className="empty-state-icon">⚠</div>
            <h4>{error}</h4>
            <button className="btn btn-secondary btn-sm" onClick={refetch}>Retry</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📄</div>
            <h4>No documents found</h4>
            <p className="text-sm">Upload documents to start analyzing commitments</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Type</th>
                <th>Source</th>
                <th>Chunks</th>
                <th>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(doc => (
                <DocumentRow key={doc.id} doc={doc} onClick={() => setSelected(doc)} />
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'flex-end' }}>
        <Eye size={12} style={{ color: 'var(--text-muted)' }} />
        <span className="text-xs text-muted">Click a row to view full document content</span>
      </div>

      {selected && <DocumentModal doc={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
