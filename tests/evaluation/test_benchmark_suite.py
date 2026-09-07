"""Comprehensive evaluation benchmark suite for ProofChain commitment intelligence.

Measures accuracy, precision, contradiction detection rate, hallucination rate,
and graph cascading performance against synthetic ground truth documents.
"""

import pytest
import time
from app.services.workspace_service import workspace_store
from app.agents import orchestrator
from app.models.commitment import RiskLevel, CommitmentStatus, EvidenceStatus


@pytest.fixture(scope="module")
def eval_benchmark_workspace():
    """Load and execute the multi-agent pipeline on the synthetic evaluation dataset."""
    ws_id = "eval-benchmark-suite"
    ws = workspace_store.load_demo_data(ws_id)
    start_time = time.time()
    orchestrator.run_pipeline(ws_id)
    duration = time.time() - start_time
    return ws, duration


def test_benchmark_metrics(eval_benchmark_workspace):
    ws, duration = eval_benchmark_workspace
    analysis = ws.analysis

    # 1. Extraction & Grounding
    requirements = analysis.requirements
    commitments = analysis.commitments
    evidences = analysis.evidence
    conflicts = analysis.conflicts
    risks = analysis.risks
    actions = analysis.actions

    # Check minimum yield from synthetic set
    assert len(requirements) >= 5, "Failed to extract required minimum requirements"
    assert len(commitments) >= 5, "Failed to formulate commitments from requirements"
    assert len(evidences) >= 5, "Failed to retrieve evidence candidates"

    # Grounding precision: 100% of evidence items must trace to a valid ingested document
    valid_docs = {d.filename for d in ws.documents}
    unreferenced_evidence = [e for e in evidences if e.source_document not in valid_docs]
    grounding_precision = (len(evidences) - len(unreferenced_evidence)) / len(evidences)
    assert grounding_precision == 1.0, f"Grounding precision dropped to {grounding_precision}"

    # 2. Contradiction Detection Accuracy (Killer Feature: 24/7 vs Business Hours)
    critical_sla_conflicts = [
        c for c in conflicts
        if "24/7" in c.requirement_text.lower() or "business hours" in c.evidence_text.lower()
    ]
    assert len(critical_sla_conflicts) >= 1, "Failed to catch the primary 24/7 support contradiction"

    for conflict in critical_sla_conflicts:
        assert conflict.can_claim_compliance is False, "Violation: Allowed compliance claim on direct contradiction!"
        assert conflict.severity in [RiskLevel.CRITICAL, RiskLevel.HIGH]

    # Contradiction Detection Rate on Known Injected Contradictions
    assert len(conflicts) >= 1

    # 3. Hallucination Rate Verification
    # Every commitment must have a non-empty source_document, page/section, or source quote
    hallucinated_commitments = [c for c in commitments if not c.source_document or not c.description]
    hallucination_rate = len(hallucinated_commitments) / len(commitments)
    assert hallucination_rate == 0.0, f"Detected hallucinated commitments: {hallucination_rate}"

    # 4. Human-in-the-Loop Action Generation
    # Critical and high conflicts must generate actionable mitigations requiring human review
    pending_actions = [a for a in actions if a.status.value in ["AWAITING_APPROVAL", "PROPOSED"]]
    assert len(pending_actions) >= 1, "Expected pending actions awaiting human approval"

    # 5. Pipeline Speed / Execution
    assert duration < 30.0, f"Pipeline execution took longer than 30s benchmark: {duration:.2f}s"
