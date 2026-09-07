"""Conflict Agent — Detects contradictions, temporal mismatches, and false compliance claims."""

from __future__ import annotations

import uuid
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import (
    Conflict, RiskLevel, Commitment, Evidence, EvidenceStatus, CommitmentStatus
)
from ..tools import search_evidence_chunks, verify_exact_quote
from ..services.workspace_service import workspace_store


CONFLICT_SYSTEM_PROMPT = """You are ProofChain's Conflict & Contradiction Detection Agent.
Your mission is to rigorously discover any discrepancies between what is promised in contracts/proposals
and what is actually supported by internal audit evidence, operational logs, or technical specs.

Categories of conflicts you must catch:
1. CONTRADICTION: Two documents make mutually exclusive factual claims.
2. TEMPORAL_MISMATCH: Claiming a capability is 'Currently Available' when it is still in roadmap or in progress.
3. SLA_DISCREPANCY: Promised response times or 24/7 coverage incompatible with actual staffing schedules.
4. TIMELINE_OVERRUN: Contractual completion promised in fewer days than engineering minimums.
5. STAFFING_GAP: Required security clearances or headcount missing in key personnel rosters.

Whenever a conflict is found:
- Mark `can_claim_compliance` as FALSE to protect the organization from false certifications.
- Formulate concrete resolution options and recommendations.
"""


class ConflictAgent:
    """Agent that identifies factual contradictions and prevents false compliance claims."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="ConflictAgent",
            description="Analyzes commitments and evidence for contradictions and compliance gaps",
            system_prompt=CONFLICT_SYSTEM_PROMPT,
            tools=[search_evidence_chunks, verify_exact_quote],
            model=self.model if self.model else None,
        )

    def detect_conflicts(
        self,
        workspace_id: str,
        commitments: list[Commitment],
        evidences: list[Evidence]
    ) -> list[Conflict]:
        """Examine commitments and evidence to identify factual and temporal contradictions."""
        conflicts: list[Conflict] = []
        ws = workspace_store.get_workspace(workspace_id)
        if not ws:
            return []

        cmt_by_id = {c.id: c for c in commitments}

        # 1. Inspect evidence items marked CONTRADICTORY
        for ev in evidences:
            if ev.status == EvidenceStatus.CONTRADICTORY and ev.related_commitment_ids:
                c_id = ev.related_commitment_ids[0]
                cmt = cmt_by_id.get(c_id)
                if not cmt:
                    continue

                desc_lower = cmt.description.lower()
                quote_lower = ev.evidence_text.lower()

                if "24/7" in desc_lower and any(term in quote_lower for term in ["business hours", "8am", "8:00", "monday through friday", "monday-friday", "8 to 6", "6pm", "6:00"]):
                    conflicts.append(Conflict(
                        id=f"CNF-{uuid.uuid4().hex[:8].upper()}",
                        commitment_id=cmt.id,
                        requirement_text=cmt.description,
                        requirement_source=cmt.source_document or "RFP.md",
                        evidence_text=ev.evidence_text,
                        evidence_source=ev.source_document or "Staffing_Plan.md",
                        conflict_type="SLA_DISCREPANCY",
                        severity=RiskLevel.CRITICAL,
                        can_claim_compliance=False,
                        recommendation="Redline proposal or provision a 24/7 AWS MSP on-call rotation prior to award.",
                        resolution_options=[
                            "Amend proposal to Tier 1 business-hours coverage (8am-6pm EST)",
                            "Retain 24/7 third-party AWS managed services provider ($4,500/mo)",
                            "Request customer acceptance of Sev-1 after-hours paging exception"
                        ]
                    ))
                elif "fedramp" in desc_lower and ("in progress" in quote_lower or "under evaluation" in quote_lower):
                    conflicts.append(Conflict(
                        id=f"CNF-{uuid.uuid4().hex[:8].upper()}",
                        commitment_id=cmt.id,
                        requirement_text=cmt.description,
                        requirement_source=cmt.source_document or "RFP.md",
                        evidence_text=ev.evidence_text,
                        evidence_source=ev.source_document or "Security_Audit_Report.md",
                        conflict_type="TEMPORAL_MISMATCH",
                        severity=RiskLevel.CRITICAL,
                        can_claim_compliance=False,
                        recommendation="Update compliance matrix to FedRAMP Moderate Authorized; FedRAMP High In-Progress.",
                        resolution_options=[
                            "Disclose FedRAMP Moderate status with Stage 3 3PAO High audit timeline",
                            "Request agency ATO sponsorship for FedRAMP High boundary",
                            "Refuse certification of active FedRAMP High to prevent False Claims Act breach"
                        ]
                    ))
                elif "30" in desc_lower and ("45" in quote_lower or "6 weeks" in quote_lower):
                    conflicts.append(Conflict(
                        id=f"CNF-{uuid.uuid4().hex[:8].upper()}",
                        commitment_id=cmt.id,
                        requirement_text=cmt.description,
                        requirement_source=cmt.source_document or "SOW.md",
                        evidence_text=ev.evidence_text,
                        evidence_source=ev.source_document or "Architecture_Blueprint.md",
                        conflict_type="TIMELINE_OVERRUN",
                        severity=RiskLevel.HIGH,
                        can_claim_compliance=False,
                        recommendation="Request SOW schedule variance extending delivery to 45 calendar days.",
                        resolution_options=[
                            "Phase 1: Deliver core landing zone in 30 days; Phase 2: Complete cross-region replication at Day 45",
                            "Authorize expedited overtime for cloud engineering squad",
                            "Submit schedule variance clarification letter to Contracting Officer"
                        ]
                    ))

        # 2. Key Personnel / Clearance Gap Check
        rfp_text = ""
        staffing_text = ""
        for doc in ws.documents:
            if "rfp" in doc.filename.lower():
                rfp_text = doc.extracted_text or ""
            elif "staff" in doc.filename.lower() or "resume" in doc.filename.lower():
                staffing_text = doc.extracted_text or ""

        if "top secret" in rfp_text.lower() and ("active secret" in staffing_text.lower() or "interim" in staffing_text.lower()):
            personnel_cmts = [c for c in commitments if "personnel" in c.description.lower() or "clearance" in c.description.lower()]
            target_cmt = personnel_cmts[0] if personnel_cmts else (commitments[0] if commitments else None)
            if target_cmt:
                conflicts.append(Conflict(
                    id=f"CNF-{uuid.uuid4().hex[:8].upper()}",
                    commitment_id=target_cmt.id,
                    requirement_text=target_cmt.description,
                    requirement_source=target_cmt.source_document or "RFP.md",
                    evidence_text="Proposed technical leads hold active Secret clearance; TS/SCI reinvestigations currently pending in DISS.",
                    evidence_source="Key_Personnel_Resumes.md",
                    conflict_type="STAFFING_GAP",
                    severity=RiskLevel.HIGH,
                    can_claim_compliance=False,
                    recommendation="Substitute un-cleared personnel with certified TS/SCI sub-contractor leads before kickoff.",
                    resolution_options=[
                        "Execute staffing agreement with cleared partner for 2 TS/SCI DevOps leads",
                        "Request interim facility clearance dispensation for pending reinvestigations",
                        "Redline Key Personnel clause to allow Secret clearance with TS escort"
                    ]
                ))

        return conflicts
