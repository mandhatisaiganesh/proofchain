// ─── Analysis Page ──────────────────────────────────────────────────
import { useState } from 'react';
import { Play, CheckCircle2, XCircle, Loader, Clock } from 'lucide-react';
import api from '../api';
import type { AnalysisRun } from '../types';

interface Props { workspaceId: string; }

const PIPELINE_STEPS = [
  'requirement_extraction',
  'commitment_mapping',
  'evidence_grounding',
  'conflict_detection',
  'capability_mapping',
  'risk_assessment',
  'action_generation',
  'verification_auditing',
  'graph_update',
  'metrics_computation',
];

const STEP_LABELS: Record<string, string> = {
  requirement_extraction: '1. Extract Requirements',
  commitment_mapping:     '2. Map Commitments',
  evidence_grounding:     '3. Ground Evidence (RAG)',
  conflict_detection:     '4. Detect Conflicts',
  capability_mapping:     '5. Map Capabilities',
  risk_assessment:        '6. Assess Risks',
  action_generation:      '7. Generate Actions',
  verification_auditing:  '8. Verify & Audit',
  graph_update:           '9. Update Knowledge Graph',
  metrics_computation:    '10. Compute Metrics',
};

function StepStatus({ step, run }: { step: string; run: AnalysisRun | null }) {
  if (!run) return <span className="step-dot pending" />;
  if (run.steps_failed.includes(step)) return <XCircle size={14} style={{ color: 'var(--red)', flexShrink: 0 }} />;
  if (run.steps_completed.includes(step)) return <CheckCircle2 size={14} style={{ color: 'var(--green)', flexShrink: 0 }} />;
  if (run.status === 'RUNNING') return <Loader size={14} style={{ color: 'var(--indigo)', animation: 'spin 1s linear infinite', flexShrink: 0 }} />;
  return <span className="step-dot pending" style={{ background: 'var(--border-strong)' }} />;
}

export default function Analysis({ workspaceId }: Props) {
  const [run, setRun] = useState<AnalysisRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.analysis.run(workspaceId);
      setRun(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const elapsed = run?.started_at && run?.completed_at
    ? ((new Date(run.completed_at).getTime() - new Date(run.started_at).getTime()) / 1000).toFixed(1)
    : null;

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 style={{ marginBottom: 4 }}>Run Analysis</h2>
          <p className="text-sm text-muted">
            Trigger the 10-step autonomous commitment intelligence pipeline
          </p>
        </div>
      </div>

      <div className="grid-2">
        {/* Control panel */}
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Play size={14} /> Pipeline Control</span>
          </div>
          <div className="card-body">
            <p className="text-sm" style={{ marginBottom: 20, lineHeight: 1.7 }}>
              The analysis pipeline will scan all workspace documents, extract commitment
              obligations, ground each with evidence from the RAG index, detect conflicts,
              assess delivery risks, and generate required actions.
            </p>

            <button
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '10px' }}
              onClick={startAnalysis}
              disabled={loading}
            >
              {loading
                ? <><Loader size={15} style={{ animation: 'spin 1s linear infinite' }} /> Running pipeline…</>
                : <><Play size={15} /> Start Analysis</>}
            </button>

            {error && (
              <div style={{
                marginTop: 12, padding: '10px 14px',
                background: 'var(--red-bg)', border: '1px solid var(--red-border)',
                borderRadius: 'var(--radius-md)', color: 'var(--red)', fontSize: 13,
              }}>
                {error}
              </div>
            )}

            {run && (
              <div style={{ marginTop: 16 }}>
                <div className="stat-row">
                  <span className="stat-row-label">Run ID</span>
                  <span className="stat-row-value text-mono text-sm">{run.id.slice(0, 8)}…</span>
                </div>
                <div className="stat-row">
                  <span className="stat-row-label">Status</span>
                  <span className={`badge ${run.status === 'COMPLETED' ? 'badge-green' : run.status === 'FAILED' ? 'badge-red' : 'badge-yellow'}`}>
                    {run.status}
                  </span>
                </div>
                <div className="stat-row">
                  <span className="stat-row-label">Steps completed</span>
                  <span className="stat-row-value">{run.steps_completed.length} / {PIPELINE_STEPS.length}</span>
                </div>
                {elapsed && (
                  <div className="stat-row">
                    <span className="stat-row-label">Duration</span>
                    <span className="stat-row-value"><Clock size={12} style={{ display: 'inline', marginRight: 4 }} />{elapsed}s</span>
                  </div>
                )}
                {run.errors.length > 0 && (
                  <div style={{ marginTop: 10 }}>
                    <div className="text-xs text-muted" style={{ marginBottom: 4 }}>ERRORS</div>
                    {run.errors.map((err, i) => (
                      <div key={i} style={{ fontSize: 12, color: 'var(--red)', marginBottom: 3 }}>• {err}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Pipeline steps */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Pipeline Steps</span>
            {run && (
              <span className="text-xs text-muted">
                {run.steps_completed.length}/{PIPELINE_STEPS.length} done
              </span>
            )}
          </div>
          <div className="card-body" style={{ padding: 'var(--space-3) var(--space-4)' }}>
            {PIPELINE_STEPS.map(step => {
              const isDone = run?.steps_completed.includes(step);
              const isFailed = run?.steps_failed.includes(step);
              return (
                <div
                  key={step}
                  className="pipeline-step"
                  style={{ opacity: !run ? 0.5 : 1 }}
                >
                  <StepStatus step={step} run={run} />
                  <span style={{
                    fontSize: 13,
                    color: isDone ? 'var(--text-muted)' : isFailed ? 'var(--red)' : 'var(--text-secondary)',
                    textDecoration: isDone ? 'line-through' : 'none',
                  }}>
                    {STEP_LABELS[step]}
                  </span>
                </div>
              );
            })}

            {/* Overall progress */}
            {run && (
              <div style={{ marginTop: 16 }}>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${(run.steps_completed.length / PIPELINE_STEPS.length) * 100}%`,
                      background: run.status === 'FAILED' ? 'var(--red)' : 'var(--green)',
                    }}
                  />
                </div>
                <div className="text-xs text-muted" style={{ marginTop: 4, textAlign: 'right' }}>
                  {Math.round((run.steps_completed.length / PIPELINE_STEPS.length) * 100)}% complete
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Architecture overview */}
      <div className="card" style={{ marginTop: 16 }}>
        <div className="card-header">
          <span className="card-title">Agent Architecture</span>
        </div>
        <div className="card-body" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {[
            { name: 'OrchestratorAgent', color: 'indigo', desc: 'Coordinates pipeline' },
            { name: 'RequirementAgent',  color: 'cyan',   desc: 'Extracts obligations' },
            { name: 'CommitmentAgent',   color: 'purple', desc: 'Maps commitments' },
            { name: 'EvidenceAgent',     color: 'green',  desc: 'RAG retrieval' },
            { name: 'ConflictAgent',     color: 'red',    desc: 'Detects contradictions' },
            { name: 'CapabilityAgent',   color: 'orange', desc: 'Gap analysis' },
            { name: 'RiskAgent',         color: 'yellow', desc: 'Risk scoring' },
            { name: 'ActionAgent',       color: 'cyan',   desc: 'Generates actions' },
            { name: 'VerificationAgent', color: 'green',  desc: 'Audits evidence' },
            { name: 'GraphAgent',        color: 'indigo', desc: 'Updates graph' },
          ].map(a => (
            <div key={a.name} style={{
              background: 'var(--bg-elevated)', border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)', padding: '8px 12px', flex: '1 1 160px',
              borderLeft: `3px solid var(--${a.color})`,
            }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{a.name}</div>
              <div className="text-xs text-muted">{a.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
