"""Commitment Agent — Synthesizes requirements and proposals into actionable commitments."""

from __future__ import annotations

import uuid
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import Commitment, CommitmentStatus, Requirement, RequirementType
from ..tools import read_document_text, list_workspace_documents
from ..services.workspace_service import workspace_store


COMMITMENT_SYSTEM_PROMPT = """You are ProofChain's Commitment Mapping Agent.
Your role is to map formal requirements into explicit, actionable organizational commitments.
Every commitment must specify:
1. Clear title and operational scope.
2. Requirement IDs it fulfills.
3. Designated accountable owner/role.
4. Target completion timeframe or milestone.
5. Tangible deliverable.
6. Empirical verification method.
"""


class CommitmentAgent:
    """Agent that creates structured, trackable commitments from parsed requirements."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="CommitmentAgent",
            description="Synthesizes contractual obligations into verifiable commitments",
            system_prompt=COMMITMENT_SYSTEM_PROMPT,
            tools=[read_document_text, list_workspace_documents],
            model=self.model if self.model else None,
        )

    def generate_commitments(self, workspace_id: str, requirements: list[Requirement]) -> list[Commitment]:
        """Generate structured commitments linked to requirements."""
        commitments: list[Commitment] = []

        # Group requirements by category to form coherent organizational commitments
        cat_map: dict[str, list[Requirement]] = {}
        for r in requirements:
            cat_map.setdefault(r.category, []).append(r)

        for cat, reqs in cat_map.items():
            for req in reqs:
                # Derive title and deliverable
                title = req.text[:80].strip()
                if len(req.text) > 80:
                    title += "..."

                owner = "Engineering Lead"
                verification_method = "Automated test suite & verification artifact"
                deliverable = "Technical delivery milestone"

                if "Security" in cat or "FedRAMP" in req.text:
                    owner = "Chief Information Security Officer (CISO)"
                    verification_method = "Third-party audit certification & FedRAMP Marketplace listing"
                    deliverable = "FedRAMP Authorization Package"
                elif "Support" in cat or "SLA" in cat:
                    owner = "VP of Technical Operations"
                    verification_method = "PagerDuty on-call shift schedule & APM 99.99% uptime report"
                    deliverable = "24/7 Follow-the-Sun SLA Dashboard"
                elif "Timeline" in cat:
                    owner = "Senior Delivery Program Manager"
                    verification_method = "Sprint burndown report & sign-off milestone"
                    deliverable = "Production Release & Handover"
                elif "Staffing" in cat:
                    owner = "Technical Talent Partner"
                    verification_method = "DOD clearance verification & background audit"
                    deliverable = "Key Personnel Staffing Matrix"

                commitments.append(Commitment(
                    id=f"CMT-{uuid.uuid4().hex[:8].upper()}",
                    title=title,
                    description=req.text,
                    requirement_ids=[req.id],
                    owner=owner,
                    status=CommitmentStatus.UNVERIFIED,
                    deadline=req.deadline or "Project Phase 1",
                    deliverable=deliverable,
                    verification_method=verification_method,
                    source_document=req.source_document,
                ))

        return commitments
