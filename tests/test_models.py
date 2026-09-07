"""Tests for ProofChain data models and graph operations."""

import pytest
from app.models.commitment import (
    Requirement, Commitment, Evidence, Capability, Risk, Action, Conflict,
    CommitmentStatus, EvidenceStatus, RiskLevel, ActionStatus, TemporalState
)
from app.models.graph import CommitmentGraph, GraphNode, GraphEdge, NodeType, EdgeType
from app.models.workspace import Workspace, Document, DashboardMetrics, AnalysisResult


def test_commitment_model_defaults():
    cmt = Commitment(
        title="FedRAMP High Certification",
        description="Deliver FedRAMP High certification before contract execution",
    )
    assert cmt.id.startswith("CMT-")
    assert cmt.status == CommitmentStatus.UNVERIFIED
    assert cmt.temporal_state == TemporalState.CURRENT


def test_conflict_false_compliance():
    conf = Conflict(
        commitment_id="CMT-123",
        requirement_text="24/7 dedicated support",
        requirement_source="RFP.md",
        evidence_text="Business hours 8am-6pm support only",
        evidence_source="Staffing_Plan.md",
        conflict_type="SLA_DISCREPANCY",
        severity=RiskLevel.CRITICAL,
        can_claim_compliance=False,
    )
    assert conf.can_claim_compliance is False
    assert conf.severity == RiskLevel.CRITICAL


def test_graph_node_and_edge_operations():
    graph = CommitmentGraph(workspace_id="ws-test")

    node1 = GraphNode(id="REQ-1", node_type=NodeType.REQUIREMENT, label="Requirement 1")
    node2 = GraphNode(id="CMT-1", node_type=NodeType.COMMITMENT, label="Commitment 1")
    edge = GraphEdge(source_id="REQ-1", target_id="CMT-1", edge_type=EdgeType.CREATES)

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge(edge)

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert graph.get_node("REQ-1") is not None
    assert len(graph.get_connected_nodes("REQ-1")) == 1


def test_evidence_invalidation_cascade():
    graph = CommitmentGraph(workspace_id="ws-test")

    cmt = GraphNode(id="CMT-100", node_type=NodeType.COMMITMENT, label="FedRAMP Compliance")
    evd = GraphNode(
        id="EVD-100",
        node_type=NodeType.EVIDENCE,
        label="FedRAMP Audit Certificate",
        properties={"source_document": "Security_Audit.md"}
    )
    edge = GraphEdge(source_id="CMT-100", target_id="EVD-100", edge_type=EdgeType.SUPPORTED_BY)

    graph.add_node(cmt)
    graph.add_node(evd)
    graph.add_edge(edge)

    # Invalidate document
    affected = graph.invalidate_evidence("Security_Audit.md")
    assert "CMT-100" in affected
    assert evd.status == "STALE"


def test_metrics_calculation():
    result = AnalysisResult(
        workspace_id="ws-1",
        run_id="run-1",
        requirements=[Requirement(text="Req 1"), Requirement(text="Req 2")],
        commitments=[
            Commitment(title="C1", description="C1", status=CommitmentStatus.VERIFIED),
            Commitment(title="C2", description="C2", status=CommitmentStatus.CONFLICT),
        ],
        conflicts=[
            Conflict(
                commitment_id="C2",
                requirement_text="Req",
                requirement_source="R",
                evidence_text="Ev",
                evidence_source="E",
                conflict_type="CONTRADICTION",
                can_claim_compliance=False
            )
        ]
    )
    metrics = DashboardMetrics.compute_from(result)
    assert metrics.total_requirements == 2
    assert metrics.total_commitments == 2
    assert metrics.verified == 1
    assert metrics.conflicts == 1
    assert metrics.false_compliance_prevented == 1
    assert metrics.compliance_health_score == 50.0
