"""Requirement Agent — Extracts requirements from RFP, SOW, and contractual documents."""

from __future__ import annotations

import re
import uuid
import time
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import Requirement, RequirementType
from ..models.workspace import Document, AgentEvent, AgentRunStatus
from ..tools import read_document_text, list_workspace_documents
from ..services.workspace_service import workspace_store


REQUIREMENT_SYSTEM_PROMPT = """You are ProofChain's Requirement Extraction Agent.
Your responsibility is to analyze contractual and procurement documents (such as RFPs, SOWs, and Master Services Agreements)
and extract every explicit and implied requirement.

For each requirement you identify:
1. Extract the verbatim or near-verbatim requirement text.
2. Determine if it is MANDATORY (must, shall, required), OPTIONAL (may, can), or PREFERRED (should, recommended).
3. Assign a specific functional or compliance category (e.g. 'Security & Compliance', 'Support & Operations', 'Timeline & Milestones', 'Architecture', 'Staffing & Personnel').
4. Identify any deadline or specific timeframe mentioned.
5. Identify clear acceptance or measurement criteria.
6. Provide exact document and section provenance.

Never invent or hallucinate requirements not grounded in the source text.
"""


class RequirementAgent:
    """Agent responsible for identifying and classifying contractual requirements."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="RequirementAgent",
            description="Extracts contractual, technical, and regulatory requirements with provenance",
            system_prompt=REQUIREMENT_SYSTEM_PROMPT,
            tools=[read_document_text, list_workspace_documents],
            model=self.model if self.model else None,
        )

    def extract_requirements(self, workspace_id: str) -> list[Requirement]:
        """Extract requirements from all workspace documents."""
        ws = workspace_store.get_workspace(workspace_id)
        if not ws:
            return []

        requirements: list[Requirement] = []

        # Grounded parser that scans document chunks and text
        for doc in ws.documents:
            text = doc.extracted_text or ""
            lines = text.split("\n")
            current_section = "General"

            for idx, line in enumerate(lines):
                line_str = line.strip()
                if line_str.startswith("#"):
                    current_section = line_str.lstrip("#").strip()
                    continue

                # Look for requirement markers: shall, must, require, deadline, within X days, 99.9%, FedRAMP, etc.
                is_req = False
                req_type = RequirementType.MANDATORY
                category = "General"

                lower_line = line_str.lower()
                if any(k in lower_line for k in ["must", "shall", "mandatory", "required to", "needs to"]):
                    is_req = True
                    req_type = RequirementType.MANDATORY
                elif any(k in lower_line for k in ["should", "preferred", "strongly recommended"]):
                    is_req = True
                    req_type = RequirementType.PREFERRED
                elif any(k in lower_line for k in ["may", "optional"]):
                    is_req = True
                    req_type = RequirementType.OPTIONAL

                # Filter out short or heading-like lines
                if is_req and len(line_str) > 25:
                    if any(s in lower_line for s in ["security", "fedramp", "soc 2", "encrypt", "cjis"]):
                        category = "Security & Compliance"
                    elif any(s in lower_line for s in ["24/7", "support", "sla", "uptime", "availability", "incident"]):
                        category = "Support & SLA"
                    elif any(s in lower_line for s in ["day", "timeline", "phase", "deadline", "schedule", "milestone"]):
                        category = "Timeline & Milestones"
                    elif any(s in lower_line for s in ["clearance", "staff", "engineer", "lead", "personnel", "team"]):
                        category = "Staffing & Clearance"
                    elif any(s in lower_line for s in ["api", "cloud", "aws", "architecture", "database"]):
                        category = "Technical Architecture"

                    # Check for deadline in line
                    deadline = None
                    deadline_match = re.search(r"within (\d+ (?:days|months|weeks|business days))", lower_line)
                    if deadline_match:
                        deadline = deadline_match.group(1)

                    requirements.append(Requirement(
                        id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
                        text=line_str.lstrip("-*123456789. "),
                        requirement_type=req_type,
                        category=category,
                        source_document=doc.filename,
                        section=current_section,
                        deadline=deadline,
                        acceptance_criteria=f"Compliance verified against {doc.filename} section '{current_section}'"
                    ))

        return requirements
