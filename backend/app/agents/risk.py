"""Risk Assessment Agent — Quantifies financial, operational, and legal exposure."""

from __future__ import annotations

import uuid
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import Risk, RiskLevel, RiskFactor, Commitment, Conflict
from ..tools import get_graph_metrics
from ..services.workspace_service import workspace_store


RISK_SYSTEM_PROMPT = """You are ProofChain's Risk Assessment Agent.
Your mission is to quantify the exact exposure (legal, financial, and operational) of unverified commitments,
contractual conflicts, and unsupported claims.
"""


class RiskAgent:
    """Agent that quantifies risk exposure and prioritizes mitigation."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="RiskAgent",
            description="Evaluates financial exposure and legal/operational risk for commitments and conflicts",
            system_prompt=RISK_SYSTEM_PROMPT,
            tools=[get_graph_metrics],
            model=self.model if self.model else None,
        )

    def assess_risks(
        self,
        workspace_id: str,
        commitments: list[Commitment],
        conflicts: list[Conflict]
    ) -> list[Risk]:
        """Generate quantified risk items from discovered conflicts and at-risk commitments."""
        risks: list[Risk] = []

        for conf in conflicts:
            level = conf.severity
            c_id = conf.commitment_id

            if conf.conflict_type == "TEMPORAL_MISMATCH" or "fedramp" in conf.requirement_text.lower():
                risks.append(Risk(
                    id=f"RSK-{uuid.uuid4().hex[:8].upper()}",
                    commitment_id=c_id,
                    level=RiskLevel.CRITICAL,
                    title="False Claims Act / Regulatory Disqualification Exposure",
                    description=(
                        "Certifying FedRAMP High compliance prior to official ATO exposes the firm to "
                        "False Claims Act liability ($2.5M+ treble damages), mandatory debarment from federal "
                        "contracting, and contract termination for default."
                    ),
                    factors=[
                        RiskFactor(factor="Legal Liability", weight=1.0, description="False certification under FAR 52.204-21"),
                        RiskFactor(factor="Financial Treble Damages", weight=0.9, description="Statutory damages up to 3x contract value"),
                    ],
                    mitigation=(
                        "Issue immediate RFP clarification disclosing FedRAMP Moderate status with FedRAMP High in 3PAO review. "
                        "Refuse signature on unamended FedRAMP High certification."
                    )
                ))
            elif conf.conflict_type == "SLA_DISCREPANCY" or "24/7" in conf.requirement_text.lower():
                risks.append(Risk(
                    id=f"RSK-{uuid.uuid4().hex[:8].upper()}",
                    commitment_id=c_id,
                    level=RiskLevel.HIGH,
                    title="Liquidated SLA Penalty & Cure Notice Risk",
                    description=(
                        "Contract stipulates $10,000 per incident failure penalty for missed 15-minute off-hours SLA. "
                        "Current business-hours staffing will fail weekend Sev-1 tickets within 48 hours of go-live."
                    ),
                    factors=[
                        RiskFactor(factor="SLA Penalties", weight=0.8, description="$10,000 per breached incident"),
                        RiskFactor(factor="Customer Relationship", weight=0.75, description="Immediate cure notice upon first unhandled Sev-1"),
                    ],
                    mitigation=(
                        "Contract a certified AWS 24/7 Managed Services Partner for off-hours Tier 1/2 coverage "
                        "or carve out business-hours exception in contract negotiations."
                    )
                ))
            elif conf.conflict_type == "TIMELINE_OVERRUN" or "30" in conf.requirement_text.lower():
                risks.append(Risk(
                    id=f"RSK-{uuid.uuid4().hex[:8].upper()}",
                    commitment_id=c_id,
                    level=RiskLevel.HIGH,
                    title="Schedule Default & Delay Damages",
                    description=(
                        "Mandated 30-day go-live date is unfeasible given 45-day technical dependencies. "
                        "Exposes project to $5,000/day late completion liquidated damages ($75,000 estimated)."
                    ),
                    factors=[
                        RiskFactor(factor="Liquidated Damages", weight=0.7, description="$5,000/day after Day 30"),
                    ],
                    mitigation=(
                        "Negotiate phased milestone delivery: Core landing zone at Day 30, cross-region replication at Day 45."
                    )
                ))
            elif conf.conflict_type == "STAFFING_GAP":
                risks.append(Risk(
                    id=f"RSK-{uuid.uuid4().hex[:8].upper()}",
                    commitment_id=c_id,
                    level=RiskLevel.HIGH,
                    title="Key Personnel Breach & Security Non-Compliance",
                    description=(
                        "Failure to seat active TS/SCI engineers by Day 1 breaches FAR Key Personnel clause, "
                        "allowing the Government to terminate contract for default ($450,000 estimated re-compete exposure)."
                    ),
                    factors=[
                        RiskFactor(factor="FAR Breach", weight=0.85, description="Key personnel clause violation"),
                    ],
                    mitigation="Submit cleared sub-contractor resume substitution to the Contracting Officer immediately."
                ))

        # Unverified commitments
        for cmt in commitments:
            if not cmt.evidence_ids and cmt.id not in [r.commitment_id for r in risks]:
                risks.append(Risk(
                    id=f"RSK-{uuid.uuid4().hex[:8].upper()}",
                    commitment_id=cmt.id,
                    level=RiskLevel.MEDIUM,
                    title=f"Unsubstantiated Obligation: {cmt.title[:40]}",
                    description=f"Commitment '{cmt.title}' lacks supporting internal evidence or audit proof.",
                    factors=[
                        RiskFactor(factor="Missing Evidence", weight=0.5, description="No primary citation attached"),
                    ],
                    mitigation="Request operational verification artifact from accountable owner."
                ))

        return risks
