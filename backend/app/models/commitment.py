"""Core data models for ProofChain commitment intelligence."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Status Enums ──────────────────────────────────────────────────────

class CommitmentStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICT = "CONFLICT"
    AT_RISK = "AT_RISK"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"


class EvidenceStatus(str, Enum):
    SUPPORTING = "SUPPORTING"
    CONTRADICTORY = "CONTRADICTORY"
    INSUFFICIENT = "INSUFFICIENT"
    STALE = "STALE"


class ActionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class RequirementType(str, Enum):
    MANDATORY = "MANDATORY"
    OPTIONAL = "OPTIONAL"
    PREFERRED = "PREFERRED"


class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class VerificationResult(str, Enum):
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class TemporalState(str, Enum):
    CURRENT = "CURRENT"
    FUTURE = "FUTURE"
    PLANNED = "PLANNED"
    EXPIRED = "EXPIRED"


# ── Provenance ────────────────────────────────────────────────────────

class Provenance(BaseModel):
    """Source tracking for every material claim."""
    source_document: str
    page: Optional[int] = None
    section: Optional[str] = None
    evidence_reference: str
    confidence: float = Field(ge=0.0, le=1.0)
    verification_status: CommitmentStatus = CommitmentStatus.UNVERIFIED


# ── Core Entities ─────────────────────────────────────────────────────

class Requirement(BaseModel):
    """A requirement extracted from a source document."""
    id: str = Field(default_factory=lambda: f"REQ-{uuid.uuid4().hex[:8].upper()}")
    text: str
    requirement_type: RequirementType = RequirementType.MANDATORY
    category: str = ""
    source_document: str = ""
    page: Optional[int] = None
    section: Optional[str] = None
    deadline: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Commitment(BaseModel):
    """An actionable commitment derived from one or more requirements."""
    id: str = Field(default_factory=lambda: f"CMT-{uuid.uuid4().hex[:8].upper()}")
    title: str
    description: str
    requirement_ids: list[str] = Field(default_factory=list)
    status: CommitmentStatus = CommitmentStatus.UNVERIFIED
    owner: Optional[str] = None
    deadline: Optional[str] = None
    source_document: Optional[str] = None
    deliverable: Optional[str] = None
    verification_method: Optional[str] = None
    required_capabilities: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    risk_ids: list[str] = Field(default_factory=list)
    action_ids: list[str] = Field(default_factory=list)
    temporal_state: TemporalState = TemporalState.CURRENT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Evidence(BaseModel):
    """Evidence supporting or contradicting a commitment."""
    id: str = Field(default_factory=lambda: f"EVD-{uuid.uuid4().hex[:8].upper()}")
    claim: str
    source_document: str
    page: Optional[int] = None
    section: Optional[str] = None
    evidence_text: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    status: EvidenceStatus = EvidenceStatus.INSUFFICIENT
    related_commitment_ids: list[str] = Field(default_factory=list)
    temporal_state: TemporalState = TemporalState.CURRENT
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_provenance(self) -> Provenance:
        return Provenance(
            source_document=self.source_document,
            page=self.page,
            section=self.section,
            evidence_reference=self.evidence_text,
            confidence=self.confidence,
            verification_status=CommitmentStatus.UNVERIFIED,
        )


class Capability(BaseModel):
    """A capability required or available for commitments."""
    id: str = Field(default_factory=lambda: f"CAP-{uuid.uuid4().hex[:8].upper()}")
    name: str
    description: str = ""
    required_for_commitment_ids: list[str] = Field(default_factory=list)
    available: bool = False
    current_state: Optional[str] = None
    gap_description: Optional[str] = None
    temporal_state: TemporalState = TemporalState.CURRENT


class Dependency(BaseModel):
    """A dependency between commitments or capabilities."""
    id: str = Field(default_factory=lambda: f"DEP-{uuid.uuid4().hex[:8].upper()}")
    description: str
    source_commitment_id: str
    target_commitment_id: Optional[str] = None
    target_capability_id: Optional[str] = None
    is_blocking: bool = False


class Risk(BaseModel):
    """A risk associated with a commitment."""
    id: str = Field(default_factory=lambda: f"RSK-{uuid.uuid4().hex[:8].upper()}")
    title: str
    description: str
    commitment_id: str
    level: RiskLevel = RiskLevel.MEDIUM
    factors: list[RiskFactor] = Field(default_factory=list)
    mitigation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RiskFactor(BaseModel):
    """An individual factor contributing to risk."""
    factor: str
    weight: float = Field(ge=0.0, le=1.0, default=0.5)
    description: str = ""


# Fix forward reference — Risk references RiskFactor
Risk.model_rebuild()


class Action(BaseModel):
    """An action required to resolve a commitment issue."""
    id: str = Field(default_factory=lambda: f"ACT-{uuid.uuid4().hex[:8].upper()}")
    title: str
    description: str
    commitment_id: str
    owner: Optional[str] = None
    priority: RiskLevel = RiskLevel.MEDIUM
    deadline: Optional[str] = None
    status: ActionStatus = ActionStatus.PROPOSED
    required_evidence: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Verification(BaseModel):
    """Verification result for a commitment."""
    id: str = Field(default_factory=lambda: f"VER-{uuid.uuid4().hex[:8].upper()}")
    commitment_id: str
    result: VerificationResult = VerificationResult.INSUFFICIENT_EVIDENCE
    reasoning: str = ""
    evidence_reviewed: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    verified_at: datetime = Field(default_factory=datetime.utcnow)


class Conflict(BaseModel):
    """A detected conflict between a requirement and evidence."""
    id: str = Field(default_factory=lambda: f"CNF-{uuid.uuid4().hex[:8].upper()}")
    commitment_id: str
    requirement_text: str
    requirement_source: str
    evidence_text: str
    evidence_source: str
    conflict_type: str  # CONTRADICTION, DEADLINE_CONFLICT, CAPABILITY_GAP, STALE_EVIDENCE
    severity: RiskLevel = RiskLevel.HIGH
    recommendation: str = ""
    can_claim_compliance: bool = False
    resolution_options: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
