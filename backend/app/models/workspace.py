"""Workspace and document models."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field

from .commitment import (
    Requirement, Commitment, Evidence, Capability, Dependency,
    Risk, Action, Verification, Conflict,
)
from .graph import CommitmentGraph


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class AgentRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class Document(BaseModel):
    """A document in a workspace."""
    id: str = Field(default_factory=lambda: f"DOC-{uuid.uuid4().hex[:8].upper()}")
    filename: str
    file_type: str
    file_size: int = 0
    status: DocumentStatus = DocumentStatus.UPLOADED
    page_count: Optional[int] = None
    content_hash: Optional[str] = None
    s3_key: Optional[str] = None
    extracted_text: Optional[str] = None
    chunks: list[DocumentChunk] = Field(default_factory=list)
    version: int = 1
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


class DocumentChunk(BaseModel):
    """A chunk of document text with provenance."""
    id: str = Field(default_factory=lambda: f"CHK-{uuid.uuid4().hex[:8].upper()}")
    document_id: str
    document_name: str
    text: str
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_index: int = 0
    embedding: Optional[list[float]] = None


# Forward reference fix
Document.model_rebuild()


class AgentEvent(BaseModel):
    """A single event in the agent execution timeline."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent: str
    event: str
    status: AgentRunStatus = AgentRunStatus.RUNNING
    details: Optional[str] = None
    duration_ms: Optional[int] = None


class AgentRun(BaseModel):
    """A complete agent analysis run."""
    id: str = Field(default_factory=lambda: f"RUN-{uuid.uuid4().hex[:8].upper()}")
    workspace_id: str
    status: AgentRunStatus = AgentRunStatus.PENDING
    events: list[AgentEvent] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    error: Optional[str] = None

    def add_event(self, agent: str, event: str, status: AgentRunStatus = AgentRunStatus.RUNNING, details: str = None):
        self.events.append(AgentEvent(
            agent=agent, event=event, status=status, details=details
        ))


class Scenario(BaseModel):
    """A what-if scenario for commitment analysis."""
    id: str = Field(default_factory=lambda: f"SCN-{uuid.uuid4().hex[:8].upper()}")
    name: str
    description: str
    commitment_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    result: Optional[ScenarioResult] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScenarioResult(BaseModel):
    """Result of a scenario analysis."""
    risk_level: str
    affected_commitments: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    recommendation: str = ""
    risk_comparison: Optional[dict[str, Any]] = None


Scenario.model_rebuild()


class AnalysisResult(BaseModel):
    """Complete result of a ProofChain analysis."""
    workspace_id: str
    run_id: str = Field(default_factory=lambda: f"RUN-{uuid.uuid4().hex[:8].upper()}")
    requirements: list[Requirement] = Field(default_factory=list)
    commitments: list[Commitment] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    capabilities: list[Capability] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    verifications: list[Verification] = Field(default_factory=list)
    graph: Optional[CommitmentGraph] = None
    metrics: Optional[DashboardMetrics] = None


class DashboardMetrics(BaseModel):
    """Computed metrics for the dashboard — never hardcoded."""
    total_requirements: int = 0
    total_commitments: int = 0
    verified: int = 0
    partially_verified: int = 0
    unverified: int = 0
    at_risk: int = 0
    conflicts: int = 0
    open_actions: int = 0
    verification_failures: int = 0
    documents_analyzed: int = 0
    evidence_items: int = 0
    high_risk_count: int = 0
    false_compliance_prevented: int = 0
    compliance_health_score: float = 0.0

    @classmethod
    def compute_from(cls, result: AnalysisResult) -> DashboardMetrics:
        """Compute metrics from actual analysis results."""
        from .commitment import CommitmentStatus, ActionStatus, RiskLevel

        commitments = result.commitments
        total = len(commitments)
        v = sum(1 for c in commitments if c.status == CommitmentStatus.VERIFIED)
        pv = sum(1 for c in commitments if c.status == CommitmentStatus.PARTIALLY_VERIFIED)
        health = 100.0 if total == 0 else round(((v + (pv * 0.5)) / total) * 100.0, 1)

        return cls(
            total_requirements=len(result.requirements),
            total_commitments=total,
            verified=v,
            partially_verified=pv,
            unverified=sum(1 for c in commitments if c.status == CommitmentStatus.UNVERIFIED),
            at_risk=sum(1 for c in commitments if c.status == CommitmentStatus.AT_RISK),
            conflicts=len(result.conflicts),
            open_actions=sum(
                1 for a in result.actions
                if a.status in (ActionStatus.PROPOSED, ActionStatus.AWAITING_APPROVAL, ActionStatus.IN_PROGRESS)
            ),
            verification_failures=sum(
                1 for v in result.verifications
                if v.result.value in ("REJECTED", "INSUFFICIENT_EVIDENCE")
            ),
            documents_analyzed=0,  # Set by caller
            evidence_items=len(result.evidence),
            high_risk_count=sum(1 for r in result.risks if r.level in (RiskLevel.CRITICAL, RiskLevel.HIGH)),
            false_compliance_prevented=sum(
                1 for c in result.conflicts if not c.can_claim_compliance
            ),
            compliance_health_score=health,
        )


AnalysisResult.model_rebuild()


class Workspace(BaseModel):
    """A ProofChain workspace containing documents and analysis."""
    id: str = Field(default_factory=lambda: f"WS-{uuid.uuid4().hex[:8].upper()}")
    name: str
    description: str = ""
    documents: list[Document] = Field(default_factory=list)
    analysis: Optional[AnalysisResult] = None
    runs: list[AgentRun] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
