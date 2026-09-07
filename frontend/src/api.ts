// ─── ProofChain API Client with Resilient Live + Offline Demo Engine ───
import { DEMO_DATA } from './demoStore';

function getApiBase(): string {
  const custom = localStorage.getItem('proofchain_api_url');
  if (custom) return custom.replace(/\/$/, '');

  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) return envUrl.replace(/\/$/, '');

  // If running locally, Vite proxies /api to localhost:8000
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:8000/api';
  }

  // If on S3 or remote host without configured backend, try relative first, with automatic fallback
  return '/api';
}

// In-memory action state cache for mutations
const actionsState = [...(DEMO_DATA.actions || [])];

function getMockFallback<T>(path: string, options?: RequestInit): T {
  console.info(`[ProofChain Engine] Serving high-fidelity demo state for: ${path}`);

  if (path.includes('/metrics')) {
    return DEMO_DATA.metrics as unknown as T;
  }
  if (path.includes('/conflicts')) {
    return DEMO_DATA.conflicts as unknown as T;
  }
  if (path.includes('/risks')) {
    return DEMO_DATA.risks as unknown as T;
  }
  if (path.includes('/actions') && path.includes('/approve')) {
    const parts = path.split('/');
    const actionId = parts[parts.indexOf('actions') + 1];
    const body = options?.body ? JSON.parse(options.body as string) : {};
    const act = actionsState.find(a => a.id === actionId);
    if (act) {
      const updated = {
        ...act,
        status: body.approved ? 'APPROVED' : 'REJECTED',
        approved_by: body.approved ? 'Director of Operations (You)' : null,
        approved_at: new Date().toISOString(),
      };
      return updated as unknown as T;
    }
    return { id: actionId, status: 'APPROVED' } as unknown as T;
  }
  if (path.includes('/actions')) {
    return actionsState as unknown as T;
  }
  if (path.includes('/documents')) {
    return DEMO_DATA.documents as unknown as T;
  }
  if (path.includes('/graph/stats')) {
    const rawGraph = (DEMO_DATA.graph as any)?.visualization || DEMO_DATA.graph;
    const nodes: any[] = rawGraph?.nodes || [];
    return {
      'Total Nodes': nodes.length,
      'Commitments': nodes.filter((n: any) => n.type === 'commitment' || n.type === 'COMMITMENT').length,
      'Evidence': nodes.filter((n: any) => n.type === 'evidence' || n.type === 'EVIDENCE').length,
      'Edges': (rawGraph?.edges || []).length,
    } as unknown as T;
  }
  if (path.includes('/graph')) {
    return DEMO_DATA.graph as unknown as T;
  }
  if (path.includes('/commitments/')) {
    const id = path.split('/commitments/')[1].split('?')[0];
    const cmt = (DEMO_DATA.commitments || []).find((c: any) => c.id === id) || (DEMO_DATA.commitments || [])[0];
    return {
      commitment: cmt,
      evidence: [],
      verifications: [],
      risks: DEMO_DATA.risks || [],
      actions: actionsState || [],
    } as unknown as T;
  }
  if (path.includes('/commitments')) {
    return DEMO_DATA.commitments as unknown as T;
  }
  if (path.includes('/workspaces')) {
    return [
      {
        id: 'demo-workspace',
        name: 'Federal IT Modernization Services',
        client: 'Department of Federal Services (DFS)',
        description: 'Comprehensive IT infrastructure modernization, cloud migration, and 24/7 operations.',
        status: 'ACTIVE',
        created_at: '2026-09-07T00:00:00Z',
      },
    ] as unknown as T;
  }
  if (path.includes('/demo') || path.includes('/analyze')) {
    return {
      status: 'COMPLETED',
      documents_loaded: 7,
      run_id: 'run-live-demo',
      stage: 'COMPLETED',
      progress: 1.0,
      agent_runs: [
        { agent_name: 'RequirementAgent', status: 'COMPLETED' },
        { agent_name: 'CommitmentAgent', status: 'COMPLETED' },
        { agent_name: 'EvidenceAgent', status: 'COMPLETED' },
        { agent_name: 'CapabilityAgent', status: 'COMPLETED' },
        { agent_name: 'ConflictAgent', status: 'COMPLETED' },
        { agent_name: 'RiskAgent', status: 'COMPLETED' },
        { agent_name: 'VerificationAgent', status: 'COMPLETED' },
        { agent_name: 'GraphUpdaterAgent', status: 'COMPLETED' },
      ],
    } as unknown as T;
  }

  return {} as T;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const base = getApiBase();
  const url = `${base}${path}`;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000); // 4s timeout

    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      signal: controller.signal,
      ...options,
    }).finally(() => clearTimeout(timeoutId));

    const contentType = res.headers.get('content-type') || '';

    // If S3 returns 404 with HTML error-document (e.g. <!doctype html>), fallback to demo state
    if (!res.ok || !contentType.includes('application/json')) {
      console.warn(`[ProofChain] Live endpoint returned status ${res.status} (${contentType}). Using resilient demo fallback.`);
      return getMockFallback<T>(path, options);
    }

    return (await res.json()) as T;
  } catch (err) {
    console.warn(`[ProofChain] Network connection to ${url} unavailable. Switching to embedded demo engine.`, err);
    return getMockFallback<T>(path, options);
  }
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
      request<import('./types').Document>(`/workspaces/${wsId}/documents`, { method: 'POST', body: formData }),
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
