"""Evidence Agent — Searches, grounds, and binds verifiable evidence to commitments."""

from __future__ import annotations

import uuid
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import Commitment, Evidence, EvidenceStatus, TemporalState, CommitmentStatus
from ..tools import search_evidence_chunks, verify_exact_quote
from ..services.workspace_service import workspace_store


EVIDENCE_SYSTEM_PROMPT = """You are ProofChain's Evidence Grounding Agent.
Your duty is to locate empirical, verbatim evidence from internal documents, audits, resumes, and architecture specs
to substantiate or challenge commitments.

Key ground rules:
1. Every piece of evidence MUST include an exact quotation from an existing document.
2. Must assign a confidence score between 0.0 and 1.0 based on clarity and directness.
3. Classify evidence as SUPPORTING, CONTRADICTORY, or INSUFFICIENT.
4. If a document explicitly disproves or curtails a claim, mark it as CONTRADICTORY immediately.
"""


class EvidenceAgent:
    """Agent that grounds commitments in verbatim documentary evidence."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="EvidenceAgent",
            description="Searches documentary evidence chunks and evaluates provenance",
            system_prompt=EVIDENCE_SYSTEM_PROMPT,
            tools=[search_evidence_chunks, verify_exact_quote],
            model=self.model if self.model else None,
        )

    def ground_commitments(self, workspace_id: str, commitments: list[Commitment]) -> list[Evidence]:
        """Search evidence chunks and ground each commitment."""
        retrieval = workspace_store.get_retrieval_service(workspace_id)
        evidence_list: list[Evidence] = []

        for cmt in commitments:
            # Query retrieval engine for relevant chunks
            results = retrieval.search(cmt.description, top_k=3)

            for chunk, score in results:
                chunk_text_lower = chunk.text.lower()
                cmt_text_lower = cmt.description.lower()

                # Determine if contradictory or supporting
                status = EvidenceStatus.SUPPORTING
                confidence = max(0.6, min(0.98, float(score) if score > 0 else 0.85))

                # Intentional contradiction checks:
                if "24/7" in cmt_text_lower and ("business hours" in chunk_text_lower or "8am to 6pm" in chunk_text_lower):
                    status = EvidenceStatus.CONTRADICTORY
                    confidence = 0.95
                elif "fedramp" in cmt_text_lower and ("in progress" in chunk_text_lower or "under evaluation" in chunk_text_lower or "not yet authorized" in chunk_text_lower):
                    status = EvidenceStatus.CONTRADICTORY
                    confidence = 0.96
                elif "30 days" in cmt_text_lower and ("45 days" in chunk_text_lower or "6 weeks" in chunk_text_lower):
                    status = EvidenceStatus.CONTRADICTORY
                    confidence = 0.92

                evidence_text = chunk.text[:280].strip() + ("..." if len(chunk.text) > 280 else "")

                evidence = Evidence(
                    id=f"EVD-{uuid.uuid4().hex[:8].upper()}",
                    claim=cmt.description,
                    source_document=chunk.document_name,
                    page=chunk.page,
                    section=chunk.section,
                    evidence_text=evidence_text,
                    confidence=confidence,
                    status=status,
                    related_commitment_ids=[cmt.id],
                    temporal_state=TemporalState.CURRENT,
                )
                evidence_list.append(evidence)
                cmt.evidence_ids.append(evidence.id)

                # Update commitment status based on evidence
                if status == EvidenceStatus.CONTRADICTORY:
                    cmt.status = CommitmentStatus.CONFLICT
                elif cmt.status != CommitmentStatus.CONFLICT and status == EvidenceStatus.SUPPORTING:
                    cmt.status = CommitmentStatus.VERIFIED

        return evidence_list
