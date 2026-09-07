// ─── ProofChain API Client ──────────────────────────────────────────

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${err}`);
  }
  return res.json() as Promise<T>;
}

// ─── Workspaces ──────────────────────────────────────────────────────
export const api = {
  workspaces: {
    list: () => request<import('./types').Workspace[]>('/workspaces'),
    get: (id: string) => request<import('./types').Workspace>(`/workspaces/${id}`),
    metrics: (id: string) => request<import('./types').DashboardMetrics>(`/workspaces/${id}/metrics`),
    loadDemo: (id: string) => request<{ status: string; documents_loaded: number }>(`/workspaces/${id}/demo`, { method: 'POST' }),
    analyze: (id: string) => request<import('./types').AnalysisRun>(`/workspaces/${id}/analyze`, { method: 'POST' }),
  },

  documents: {
    list: (wsId: string) => request<import('./types').Document[]>(`/workspaces/${wsId}/documents`),
    get: (wsId: string, docId: string) => request<import('./types').Document>(`/workspaces/${wsId}/documents/${docId}`),
    upload: (wsId: string, formData: FormData) =>
      fetch(`${BASE}/workspaces/${wsId}/documents`, { method: 'POST', body: formData }).then(r => r.json()),
  },

  analysis: {
    run: (wsId: string) => request<import('./types').AnalysisRun>(`/workspaces/${wsId}/analyze`, { method: 'POST' }),
    status: (wsId: string, runId: string) => request<import('./types').AnalysisRun>(`/workspaces/${wsId}/analysis/${runId}`),
  },

  commitments: {
    list: (wsId: string, status?: string) =>
      request<import('./types').Commitment[]>(`/workspaces/${wsId}/commitments${status ? `?status=${status}` : ''}`),
    get: (wsId: string, id: string) =>
      request<import('./types').CommitmentDetail>(`/workspaces/${wsId}/commitments/${id}`),
  },

  conflicts: {
    list: (wsId: string) => request<import('./types').Conflict[]>(`/workspaces/${wsId}/conflicts`),
  },

  risks: {
    list: (wsId: string) => request<import('./types').Risk[]>(`/workspaces/${wsId}/risks`),
  },

  actions: {
    list: (wsId: string) => request<import('./types').Action[]>(`/workspaces/${wsId}/actions`),
    approve: (wsId: string, actionId: string, approved: boolean, notes: string) =>
      request<import('./types').Action>(`/workspaces/${wsId}/actions/${actionId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ approved, notes }),
      }),
  },

  graph: {
    get: (wsId: string) => request<import('./types').GraphData>(`/workspaces/${wsId}/graph`),
    stats: (wsId: string) => request<Record<string, number>>(`/workspaces/${wsId}/graph/stats`),
    paths: (wsId: string, source: string, target: string) =>
      request<{ paths: string[][] }>(`/workspaces/${wsId}/graph/paths?source=${source}&target=${target}`),
  },

  scenarios: {
    simulate: (wsId: string, scenario: unknown) =>
      request<unknown>(`/workspaces/${wsId}/scenarios/simulate`, {
        method: 'POST',
        body: JSON.stringify(scenario),
      }),
  },
};

export default api;
