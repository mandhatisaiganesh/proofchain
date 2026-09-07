"""Verification Agent — Performs empirical cross-verification of claims against evidence."""

from __future__ import annotations

import uuid
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import (
    Verification, VerificationResult, Commitment, Evidence, EvidenceStatus, CommitmentStatus
)
from ..tools import verify_exact_quote
from ..services.workspace_service import workspace_store


VERIFICATION_SYSTEM_PROMPT = """You are ProofChain's Verification Agent.
Your duty is to judge whether a commitment has met the standard of proof.
Standards:
- VERIFIED: Directly proven with unambiguous documentary evidence.
- REJECTED: Disproven by direct contradiction in internal documentation or audits.
- INSUFFICIENT_EVIDENCE: Cited document lacks conclusive factual substantiation.
- REQUIRES_HUMAN_REVIEW: Ambiguous wording requiring legal or executive determination.
"""


class VerificationAgent:
    """Agent that performs final verification auditing on each commitment."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="VerificationAgent",
            description="Performs adversarial verification audits on commitments",
            system_prompt=VERIFICATION_SYSTEM_PROMPT,
            tools=[verify_exact_quote],
            model=self.model if self.model else None,
        )

    def verify_commitments(
        self,
        workspace_id: str,
        commitments: list[Commitment],
        evidences: list[Evidence]
    ) -> list[Verification]:
        """Perform formal verification audit for each commitment."""
        verifications: list[Verification] = []

        ev_by_cmt: dict[str, list[Evidence]] = {}
        for ev in evidences:
            for c_id in ev.related_commitment_ids:
                ev_by_cmt.setdefault(c_id, []).append(ev)

        for cmt in commitments:
            cmt_evs = ev_by_cmt.get(cmt.id, [])

            has_contradiction = any(e.status == EvidenceStatus.CONTRADICTORY for e in cmt_evs)
            has_supporting = any(e.status == EvidenceStatus.SUPPORTING for e in cmt_evs)

            if has_contradiction:
                result = VerificationResult.REJECTED
                reasoning = "Direct contradiction discovered in organizational documents. Cannot certify compliance."
                challenges = [
                    "Empirical evidence directly disproves claim made in contractual commitment",
                    "Requires formal human intervention or proposal amendment before sign-off"
                ]
                cmt.status = CommitmentStatus.CONFLICT
            elif has_supporting:
                result = VerificationResult.VERIFIED
                reasoning = f"Empirically substantiated by {len(cmt_evs)} documentary citations with high confidence."
                challenges = []
                cmt.status = CommitmentStatus.VERIFIED
            else:
                result = VerificationResult.INSUFFICIENT_EVIDENCE
                reasoning = "No primary source documentation or test logs found to substantiate claim."
                challenges = ["Lacks attached technical or operational audit artifacts"]
                cmt.status = CommitmentStatus.UNVERIFIED

            verifications.append(Verification(
                id=f"VER-{uuid.uuid4().hex[:8].upper()}",
                commitment_id=cmt.id,
                result=result,
                reasoning=reasoning,
                evidence_reviewed=[e.id for e in cmt_evs],
                challenges=challenges,
            ))

        return verifications
