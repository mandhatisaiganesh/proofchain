// ─── ProofChain API Types ───────────────────────────────────────────

export interface Workspace {
  id: string;
  name: string;
  description: string;
  documents_count: number;
  created_at: string;
  updated_at: string;
}

export interface DashboardMetrics {
  // Actual backend field names from workspace_service
  total_requirements: number;
  total_commitments: number;
  verified: number;
  partially_verified: number;
  unverified: number;
  at_risk: number;
  conflicts: number;
  open_actions: number;
  verification_failures: number;
  documents_analyzed: number;
  evidence_items: number;
  high_risk_count: number;
  false_compliance_prevented: number;
  compliance_health_score: number;
}

export interface Document {
  id: string;
  title: string;
  doc_type: string;
  source: string;
  content: string;
  metadata: Record<string, string>;
  chunk_count: number;
  uploaded_at: string;
}

export interface Evidence {
  id: string;
  text: string;
  source_document: string;
  chunk_id: string;
  relevance_score: number;
  related_commitment_ids: string[];
}

export interface Commitment {
  id: string;
  title: string;
  description: string;
  status: string;
  confidence: number;
  stakeholder: string;
  deliverable: string;
  timeline: string;
  sla_terms: string[];
  required_capabilities: string[];
  evidence_ids: string[];
  risk_ids: string[];
  action_ids: string[];
  source_document: string;
  created_at: string;
  verification_method?: string;
}

export interface CommitmentDetail {
  commitment: Commitment;
  evidence: Evidence[];
  verifications: Verification[];
  risks: Risk[];
  actions: Action[];
}

export interface Conflict {
  id: string;
  commitment_id?: string;
  requirement_text?: string;
  requirement_source?: string;
  evidence_text?: string;
  evidence_source?: string;
  conflict_type?: string;
  severity: string;
  can_claim_compliance?: boolean;
  recommendation?: string;
  resolution_options?: string[];
  description?: string;
  commitment_ids?: string[];
  evidence_ids?: string[];
  resolution_suggestion?: string;
}

export interface Risk {
  id: string;
  commitment_id: string;
  description: string;
  risk_level: string;
  probability: number;
  impact: string;
  mitigation: string;
}

export interface Action {
  id: string;
  commitment_id: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  assigned_to: string;
  due_date: string;
  created_at: string;
}

export interface Verification {
  id: string;
  commitment_id: string;
  status: string;
  confidence: number;
  reasoning: string;
  evidence_ids: string[];
  verified_at: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  status?: string;
  confidence?: number;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  weight?: number;
}

export interface AnalysisRun {
  id: string;
  workspace_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  steps_completed: string[];
  steps_failed: string[];
  errors: string[];
}
