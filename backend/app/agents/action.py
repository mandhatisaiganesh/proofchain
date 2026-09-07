"""Action Generation Agent — Generates human-in-the-loop remediation and approval actions."""

from __future__ import annotations

import uuid
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import Action, ActionStatus, RiskLevel, Commitment, Conflict, Risk, CommitmentStatus
from ..tools import get_graph_metrics
from ..services.workspace_service import workspace_store


ACTION_SYSTEM_PROMPT = """You are ProofChain's Action Generation Agent.
Your responsibility is to turn risks, conflicts, and missing evidence into concrete, assignable remediations.
Every recommended action must:
1. Define a clear human-in-the-loop approval workflow.
2. Designate a specific responsible role/owner.
3. Be marked initially as 'AWAITING_APPROVAL' or 'PROPOSED' so no irreversible contract modification occurs autonomously.
"""


class ActionAgent:
    """Agent that creates structured human-in-the-loop remediation proposals."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="ActionAgent",
            description="Generates actionable remediation and negotiation steps requiring human approval",
            system_prompt=ACTION_SYSTEM_PROMPT,
            tools=[get_graph_metrics],
            model=self.model if self.model else None,
        )

    def generate_actions(
        self,
        workspace_id: str,
        commitments: list[Commitment],
        conflicts: list[Conflict],
        risks: list[Risk]
    ) -> list[Action]:
        """Generate targeted human-in-the-loop remediation actions."""
        actions: list[Action] = []

        # Action 1: FedRAMP amendment
        fedramp_conflicts = [c for c in conflicts if c.conflict_type == "TEMPORAL_MISMATCH" or "fedramp" in c.requirement_text.lower()]
        if fedramp_conflicts:
            c = fedramp_conflicts[0]
            actions.append(Action(
                id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
                commitment_id=c.commitment_id,
                title="Redact FedRAMP High Claim & Submit ATO Disclosure Addendum",
                description=(
                    "Amend Section 3.1 of RFP Response proposal. Replace unqualified 'FedRAMP High Authorized' "
                    "with 'FedRAMP Moderate Authorized; FedRAMP High In-Progress (3PAO Review, Projected Q4 2026)'."
                ),
                owner="General Counsel & Lead Proposal Manager",
                priority=RiskLevel.CRITICAL,
                status=ActionStatus.AWAITING_APPROVAL,
                deadline="Prior to Final Proposal Submission",
                required_evidence="Draft RFP Addendum redline signed by Counsel",
            ))

        # Action 2: SLA coverage fix
        sla_conflicts = [c for c in conflicts if c.conflict_type == "SLA_DISCREPANCY" or "24/7" in c.requirement_text.lower()]
        if sla_conflicts:
            c = sla_conflicts[0]
            actions.append(Action(
                id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
                commitment_id=c.commitment_id,
                title="Approve 24/7 Managed Operations MSP Subcontract or SOW Clause Carveout",
                description=(
                    "Option A: Approve $4,500/mo retainer for AWS 24/7 on-call partner for night/weekend coverage. "
                    "Option B: Redline contract SOW Section 8 to 'Business Hours 8am-6pm EST with Sev-1 on-call paging'."
                ),
                owner="VP of Technical Operations",
                priority=RiskLevel.HIGH,
                status=ActionStatus.AWAITING_APPROVAL,
                deadline="Day -5 before Contract Signing",
                required_evidence="Executed MSP Subcontract Agreement or Signed Customer Variance Letter",
            ))

        # Action 3: Timeline extension
        timeline_conflicts = [c for c in conflicts if c.conflict_type == "TIMELINE_OVERRUN" or "30" in c.requirement_text.lower()]
        if timeline_conflicts:
            c = timeline_conflicts[0]
            actions.append(Action(
                id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
                commitment_id=c.commitment_id,
                title="Submit 45-Day Phased Architecture Schedule Request",
                description=(
                    "Send formal clarification to Contracting Officer proposing a two-phase rollout: "
                    "Phase 1 (Day 30): Primary GovCloud VPC & Database. Phase 2 (Day 45): Cross-region failover testing."
                ),
                owner="Senior Delivery Program Manager",
                priority=RiskLevel.HIGH,
                status=ActionStatus.AWAITING_APPROVAL,
                deadline="Proposal Clarification Window (Day 10)",
                required_evidence="Written Concurrence from Agency Contracting Officer",
            ))

        # Action 4: Cleared Staffing replacement
        personnel_conflicts = [c for c in conflicts if c.conflict_type == "STAFFING_GAP"]
        if personnel_conflicts:
            c = personnel_conflicts[0]
            actions.append(Action(
                id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
                commitment_id=c.commitment_id,
                title="Execute Cleared Subcontractor Staffing Agreement",
                description=(
                    "Finalize task order with pre-cleared TS/SCI staffing partner to seat 2 certified DevSecOps "
                    "engineers ahead of Day 1 project kickoff."
                ),
                owner="Director of Government Practice",
                priority=RiskLevel.HIGH,
                status=ActionStatus.AWAITING_APPROVAL,
                deadline="Contract Effective Date",
                required_evidence="DOD DISS Visit Request confirming active TS/SCI clearances",
            ))

        # Action 5: Generic for unverified items
        unverified = [c for c in commitments if c.status == CommitmentStatus.UNVERIFIED]
        if unverified:
            actions.append(Action(
                id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
                commitment_id=unverified[0].id,
                title=f"Request Evidence Artifact for {unverified[0].title[:35]}...",
                description="Prompt assigned owner to attach supporting architecture test log or certificate.",
                owner=unverified[0].owner,
                priority=RiskLevel.MEDIUM,
                status=ActionStatus.PROPOSED,
                deadline="Sprint 1 Verification Gate",
                required_evidence="Operational test report or verification screenshot",
            ))

        return actions
