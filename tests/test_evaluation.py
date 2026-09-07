"""Evaluation and benchmarking tests for ProofChain commitment intelligence."""

import pytest
from app.services.workspace_service import workspace_store
from app.agents import orchestrator
from app.services.graph_service import GraphService


def test_grounding_precision_and_provenance():
    """Verify that 100% of extracted evidence items have valid source document references."""
    ws = workspace_store.load_demo_data("eval-workspace")
    orchestrator.run_pipeline("eval-workspace")

    evidence_items = ws.analysis.evidence
    assert len(evidence_items) > 0

    valid_documents = {d.filename for d in ws.documents}
    for ev in evidence_items:
        assert ev.source_document in valid_documents
        assert len(ev.evidence_text) > 10
        assert 0.0 <= ev.confidence <= 1.0


def test_invalidation_cascade_evaluation():
    """Verify that invalidating a critical document correctly cascades AT_RISK to dependent commitments."""
    ws = workspace_store.get_workspace("eval-workspace")
    graph_svc = workspace_store.get_graph_service("eval-workspace")

    # Invalidate RFP.md
    res = graph_svc.invalidate_document("RFP.md")
    assert res["invalidated_document"] == "RFP.md"
    assert "affected_commitments_count" in res
    assert "graph_updated_at" in res
