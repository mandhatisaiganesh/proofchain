"""Tests for contradiction detection and false compliance prevention."""

import pytest
from app.services.workspace_service import workspace_store
from app.agents import orchestrator
from app.models.commitment import CommitmentStatus, RiskLevel


@pytest.fixture(scope="module")
def analyzed_workspace():
    ws = workspace_store.load_demo_data("conflict-test-ws")
    orchestrator.run_pipeline("conflict-test-ws")
    return ws


def test_intentional_sla_contradiction_detected(analyzed_workspace):
    conflicts = analyzed_workspace.analysis.conflicts
    sla_conflicts = [c for c in conflicts if c.conflict_type == "SLA_DISCREPANCY" or "24/7" in c.requirement_text.lower()]
    assert len(sla_conflicts) >= 1

    conflict = sla_conflicts[0]
    assert conflict.can_claim_compliance is False
    assert conflict.severity in [RiskLevel.CRITICAL, RiskLevel.HIGH]
    assert "24/7" in conflict.requirement_text or "support" in conflict.requirement_text.lower()


def test_false_compliance_claims_prevented(analyzed_workspace):
    conflicts = analyzed_workspace.analysis.conflicts
    for c in conflicts:
        assert c.can_claim_compliance is False, f"Conflict {c.id} allowed compliance claim unexpectedly!"


def test_risk_quantification(analyzed_workspace):
    risks = analyzed_workspace.analysis.risks
    assert len(risks) >= 1
    # Check that high/critical risks have explicit mitigations
    for r in risks:
        assert r.mitigation is not None
        assert len(r.mitigation) > 10


def test_human_in_the_loop_action_proposals(analyzed_workspace):
    actions = analyzed_workspace.analysis.actions
    assert len(actions) >= 1
    # Check that actions require approval
    for a in actions:
        assert a.status.value in ["AWAITING_APPROVAL", "PROPOSED"]
        assert a.owner is not None
