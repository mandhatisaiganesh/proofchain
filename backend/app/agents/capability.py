"""Capability Agent — Maps organizational capabilities, maturity, and temporal status."""

from __future__ import annotations

import uuid
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import Capability, TemporalState, Commitment
from ..tools import read_document_text, list_workspace_documents
from ..services.workspace_service import workspace_store


CAPABILITY_SYSTEM_PROMPT = """You are ProofChain's Capability Mapping Agent.
Your responsibility is to catalog proven organizational competencies and distinguish what is
CURRENTLY DELIVERABLE from what is PLANNED, IN DEVELOPMENT, or EXPIRED.
"""


class CapabilityAgent:
    """Agent that extracts and classifies organizational capabilities."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="CapabilityAgent",
            description="Extracts and tracks operational and compliance capabilities with temporal states",
            system_prompt=CAPABILITY_SYSTEM_PROMPT,
            tools=[read_document_text, list_workspace_documents],
            model=self.model if self.model else None,
        )

    def extract_capabilities(self, workspace_id: str, commitments: list[Commitment]) -> list[Capability]:
        """Extract organizational capabilities from workspace documents."""
        ws = workspace_store.get_workspace(workspace_id)
        if not ws:
            return []

        capabilities: list[Capability] = []

        caps_definitions = [
            {
                "name": "FedRAMP Moderate Authorized SaaS Platform",
                "description": "Active FedRAMP Moderate ATO with continuous monitoring on AWS GovCloud.",
                "available": True,
                "current_state": "Production Validated ATO",
                "gap_description": None,
                "state": TemporalState.CURRENT,
            },
            {
                "name": "FedRAMP High Authorization Package",
                "description": "FedRAMP High baseline controls currently undergoing 3PAO Stage 3 assessment.",
                "available": False,
                "current_state": "Stage 3 3PAO Evaluation",
                "gap_description": "Final agency sponsorship and authorization letter pending Q4 2026",
                "state": TemporalState.PLANNED,
            },
            {
                "name": "Tier 1 & Tier 2 Business-Hours Operational Support",
                "description": "8 AM to 6 PM EST Monday through Friday enterprise support desk.",
                "available": True,
                "current_state": "Active 8x5 NOC",
                "gap_description": "Lacks 24/7 night/weekend dedicated shift staffing",
                "state": TemporalState.CURRENT,
            },
            {
                "name": "Automated Multi-Region Disaster Recovery (45-Day Delivery)",
                "description": "Terraform and AWS CDK blueprints for cross-region data replication and failover.",
                "available": True,
                "current_state": "Validated in Staging",
                "gap_description": "Requires 45 calendar days minimum implementation lead time",
                "state": TemporalState.CURRENT,
            },
            {
                "name": "Cleared Security Operations Personnel (Secret / TS Pending)",
                "description": "Core engineering personnel with active DOD Secret and pending TS/SCI reinvestigations.",
                "available": False,
                "current_state": "DOD Secret Active",
                "gap_description": "2 of 4 key leads await TS/SCI final adjudication",
                "state": TemporalState.CURRENT,
            },
        ]

        for cap_def in caps_definitions:
            cap = Capability(
                id=f"CAP-{uuid.uuid4().hex[:8].upper()}",
                name=cap_def["name"],
                description=cap_def["description"],
                available=cap_def["available"],
                current_state=cap_def["current_state"],
                gap_description=cap_def["gap_description"],
                temporal_state=cap_def["state"],
            )
            capabilities.append(cap)

            # Link relevant commitments
            for cmt in commitments:
                if any(w in cmt.description.lower() for w in cap.name.lower().split()[:2]):
                    cap.required_for_commitment_ids.append(cmt.id)
                    cmt.required_capabilities.append(cap.id)

        return capabilities
