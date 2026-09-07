// ─── Commitment Graph Page ──────────────────────────────────────────
import { useState, useRef, useEffect, useCallback } from 'react';
import { Network, ZoomIn, ZoomOut, Maximize2, Info } from 'lucide-react';
import { useFetch } from '../hooks';
import api from '../api';
import type { GraphData, GraphNode } from '../types';

interface Props { workspaceId: string; }

// Node colors by type
const NODE_COLOR: Record<string, string> = {
  commitment:  '#6366f1',
  evidence:    '#06b6d4',
  risk:        '#ef4444',
  action:      '#f59e0b',
  conflict:    '#a855f7',
  document:    '#22c55e',
  stakeholder: '#f97316',
};

// Simple force-directed layout (no external library)
function useLayout(nodes: GraphNode[], edges: { source: string; target: string }[]) {
  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});

  useEffect(() => {
    if (nodes.length === 0) return;

    // Initialize positions
    const pos: Record<string, { x: number; y: number; vx: number; vy: number }> = {};
    nodes.forEach((n, i) => {
      const angle = (i / nodes.length) * 2 * Math.PI;
      const r = 160 + Math.random() * 60;
      pos[n.id] = { x: 250 + r * Math.cos(angle), y: 250 + r * Math.sin(angle), vx: 0, vy: 0 };
    });

    // Run simulation
    const sim = () => {
      for (let iter = 0; iter < 80; iter++) {
        // Repulsion
        nodes.forEach(a => {
          nodes.forEach(b => {
            if (a.id === b.id) return;
            const dx = pos[a.id].x - pos[b.id].x;
            const dy = pos[a.id].y - pos[b.id].y;
            const d = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = 1800 / (d * d);
            pos[a.id].vx += (dx / d) * force;
            pos[a.id].vy += (dy / d) * force;
          });
        });
        // Attraction along edges
        edges.forEach(e => {
          const s = pos[e.source];
          const t = pos[e.target];
          if (!s || !t) return;
          const dx = t.x - s.x;
          const dy = t.y - s.y;
          const d = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = (d - 120) * 0.03;
          s.vx += (dx / d) * force;
          s.vy += (dy / d) * force;
          t.vx -= (dx / d) * force;
          t.vy -= (dy / d) * force;
        });
        // Integrate + dampen
        nodes.forEach(n => {
          pos[n.id].x = Math.max(30, Math.min(470, pos[n.id].x + pos[n.id].vx));
          pos[n.id].y = Math.max(30, Math.min(470, pos[n.id].y + pos[n.id].vy));
          pos[n.id].vx *= 0.8;
          pos[n.id].vy *= 0.8;
        });
      }
    };
    sim();

    setPositions(Object.fromEntries(
      Object.entries(pos).map(([id, { x, y }]) => [id, { x, y }])
    ));
  }, [nodes.length, edges.length]); // eslint-disable-line

  return positions;
}

function GraphCanvas({ graph }: { graph: GraphData }) {
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const svgRef = useRef<SVGSVGElement>(null);
  const dragging = useRef(false);
  const lastMouse = useRef({ x: 0, y: 0 });

  // Limit nodes for performance
  const nodes = graph.nodes.slice(0, 60);
  const nodeSet = new Set(nodes.map(n => n.id));
  const edges = graph.edges.filter(e => nodeSet.has(e.source) && nodeSet.has(e.target)).slice(0, 100);

  const positions = useLayout(nodes, edges);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    dragging.current = true;
    lastMouse.current = { x: e.clientX, y: e.clientY };
  }, []);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging.current) return;
    setOffset(prev => ({
      x: prev.x + e.clientX - lastMouse.current.x,
      y: prev.y + e.clientY - lastMouse.current.y,
    }));
    lastMouse.current = { x: e.clientX, y: e.clientY };
  }, []);

  const onMouseUp = useCallback(() => { dragging.current = false; }, []);

  const onWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    setScale(s => Math.max(0.4, Math.min(3, s - e.deltaY * 0.001)));
  }, []);

  if (Object.keys(positions).length === 0) {
    return <div className="loading-overlay"><div className="spinner" /><span>Computing graph layout…</span></div>;
  }

  return (
    <div style={{ position: 'relative', userSelect: 'none' }}>
      {/* Controls */}
      <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 5, display: 'flex', gap: 4 }}>
        <button className="btn btn-secondary btn-xs" onClick={() => setScale(s => Math.min(s + 0.2, 3))}><ZoomIn size={12} /></button>
        <button className="btn btn-secondary btn-xs" onClick={() => setScale(s => Math.max(s - 0.2, 0.4))}><ZoomOut size={12} /></button>
        <button className="btn btn-secondary btn-xs" onClick={() => { setScale(1); setOffset({ x: 0, y: 0 }); }}><Maximize2 size={12} /></button>
      </div>

      <svg
        ref={svgRef}
        width="100%"
        viewBox="0 0 500 500"
        style={{ height: 480, background: 'var(--bg-surface)', borderRadius: 'var(--radius-lg)', cursor: 'grab' }}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
        onWheel={onWheel}
      >
        <g transform={`translate(${offset.x},${offset.y}) scale(${scale})`}
           style={{ transformOrigin: '250px 250px' }}>

          {/* Defs: arrowhead marker */}
          <defs>
            <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="rgba(255,255,255,0.15)" />
            </marker>
          </defs>

          {/* Edges */}
          {edges.map(e => {
            const s = positions[e.source];
            const t = positions[e.target];
            if (!s || !t) return null;
            return (
              <line
                key={e.id}
                x1={s.x} y1={s.y} x2={t.x} y2={t.y}
                stroke="rgba(255,255,255,0.1)"
                strokeWidth={1}
                markerEnd="url(#arrow)"
              />
            );
          })}

          {/* Nodes */}
          {nodes.map(n => {
            const pos = positions[n.id];
            if (!pos) return null;
            const color = NODE_COLOR[n.type] ?? '#6b7280';
            const r = n.type === 'commitment' ? 12 : n.type === 'document' ? 10 : 8;
            const isSelected = selected?.id === n.id;
            return (
              <g key={n.id} transform={`translate(${pos.x},${pos.y})`}
                 style={{ cursor: 'pointer' }}
                 onClick={() => setSelected(isSelected ? null : n)}>
                {isSelected && (
                  <circle r={r + 5} fill="transparent" stroke={color} strokeWidth={1.5} opacity={0.5} />
                )}
                <circle r={r} fill={color} fillOpacity={0.9} />
                <text
                  textAnchor="middle"
                  y={r + 11}
                  fontSize={8}
                  fill="rgba(255,255,255,0.6)"
                  style={{ pointerEvents: 'none' }}
                >
                  {(n.label ?? n.id).slice(0, 14)}
                </text>
              </g>
            );
          })}
        </g>
      </svg>

      {/* Selected node panel */}
      {selected && (
        <div style={{
          position: 'absolute', bottom: 12, left: 12,
          background: 'var(--bg-elevated)', border: '1px solid var(--border-strong)',
          borderRadius: 'var(--radius-md)', padding: '10px 14px',
          maxWidth: 240, boxShadow: 'var(--shadow-md)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <div style={{
              width: 10, height: 10, borderRadius: '50%',
              background: NODE_COLOR[selected.type] ?? '#6b7280', flexShrink: 0,
            }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>{selected.label}</span>
          </div>
          <div className="text-xs text-muted" style={{ marginBottom: 4 }}>
            Type: <span style={{ color: 'var(--text-secondary)' }}>{selected.type}</span>
          </div>
          {selected.status && (
            <div className="text-xs text-muted">
              Status: <span style={{ color: 'var(--text-secondary)' }}>{selected.status}</span>
            </div>
          )}
          {selected.confidence != null && (
            <div className="text-xs text-muted">
              Confidence: <span style={{ color: 'var(--indigo-light)' }}>{Math.round(selected.confidence * 100)}%</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function Graph({ workspaceId }: Props) {
  const { data: graph, loading, error, refetch } = useFetch<GraphData>(
    () => api.graph.get(workspaceId),
    [workspaceId],
  );
  const { data: stats } = useFetch<Record<string, number>>(
    () => api.graph.stats(workspaceId),
    [workspaceId],
  );

  const legend = Object.entries(NODE_COLOR);

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 style={{ marginBottom: 4 }}>Commitment Graph</h2>
          <p className="text-sm text-muted">Interactive knowledge graph of commitments, evidence, and risks</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={refetch}><Network size={13} /> Reload</button>
      </div>

      {/* Stats */}
      {stats && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
          {Object.entries(stats).map(([k, v]) => (
            <span key={k} className="badge badge-gray" style={{ fontSize: 12 }}>
              {k}: {v}
            </span>
          ))}
        </div>
      )}

      <div className="card" style={{ marginBottom: 16 }}>
        {loading ? (
          <div className="loading-overlay"><div className="spinner" /><span>Building graph…</span></div>
        ) : error ? (
          <div className="empty-state">
            <div className="empty-state-icon">⚠</div>
            <h4>{error}</h4>
            <button className="btn btn-secondary btn-sm" onClick={refetch}>Retry</button>
          </div>
        ) : graph ? (
          <div style={{ padding: 16 }}>
            <GraphCanvas graph={graph} />
          </div>
        ) : null}
      </div>

      {/* Legend */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><Info size={14} /> Legend</span>
        </div>
        <div className="card-body" style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
          {legend.map(([type, color]) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: color }} />
              <span style={{ fontSize: 12, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
