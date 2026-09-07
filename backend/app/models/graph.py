"""Graph models for the ProofChain Commitment Graph."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    REQUIREMENT = "REQUIREMENT"
    COMMITMENT = "COMMITMENT"
    EVIDENCE = "EVIDENCE"
    CAPABILITY = "CAPABILITY"
    DEPENDENCY = "DEPENDENCY"
    OWNER = "OWNER"
    DEADLINE = "DEADLINE"
    RISK = "RISK"
    ACTION = "ACTION"
    VERIFICATION = "VERIFICATION"
    DOCUMENT = "DOCUMENT"


class EdgeType(str, Enum):
    CREATES = "creates"
    SUPPORTED_BY = "supported_by"
    CONTRADICTED_BY = "contradicted_by"
    REQUIRES = "requires"
    DEPENDS_ON = "depends_on"
    ASSIGNED_TO = "assigned_to"
    HAS_DEADLINE = "has_deadline"
    HAS_RISK = "has_risk"
    REQUIRES_ACTION = "requires_action"
    VERIFIED_BY = "verified_by"
    ORIGINATES_FROM = "originates_from"
    BLOCKS = "blocks"
    MITIGATES = "mitigates"


class GraphNode(BaseModel):
    """A node in the Commitment Graph."""
    id: str
    node_type: NodeType
    label: str
    properties: dict[str, Any] = Field(default_factory=dict)
    status: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GraphEdge(BaseModel):
    """A directed edge in the Commitment Graph."""
    id: str = Field(default_factory=lambda: f"EDGE-{uuid.uuid4().hex[:8].upper()}")
    source_id: str
    target_id: str
    edge_type: EdgeType
    label: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CommitmentGraph(BaseModel):
    """The complete Commitment Graph state."""
    workspace_id: str
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_node(self, node: GraphNode) -> None:
        # Avoid duplicates
        if not any(n.id == node.id for n in self.nodes):
            self.nodes.append(node)
            self.updated_at = datetime.utcnow()

    def add_edge(self, edge: GraphEdge) -> None:
        if not any(
            e.source_id == edge.source_id
            and e.target_id == edge.target_id
            and e.edge_type == edge.edge_type
            for e in self.edges
        ):
            self.edges.append(edge)
            self.updated_at = datetime.utcnow()

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return next((n for n in self.nodes if n.id == node_id), None)

    def get_connected_nodes(self, node_id: str) -> list[GraphNode]:
        """Get all nodes connected to the given node."""
        connected_ids = set()
        for edge in self.edges:
            if edge.source_id == node_id:
                connected_ids.add(edge.target_id)
            elif edge.target_id == node_id:
                connected_ids.add(edge.source_id)
        return [n for n in self.nodes if n.id in connected_ids]

    def get_edges_for_node(self, node_id: str) -> list[GraphEdge]:
        return [
            e for e in self.edges
            if e.source_id == node_id or e.target_id == node_id
        ]

    def get_nodes_by_type(self, node_type: NodeType) -> list[GraphNode]:
        return [n for n in self.nodes if n.node_type == node_type]

    def invalidate_evidence(self, document_name: str) -> list[str]:
        """Invalidate evidence from a changed document. Returns affected commitment IDs."""
        affected_evidence = [
            n for n in self.nodes
            if n.node_type == NodeType.EVIDENCE
            and n.properties.get("source_document") == document_name
        ]
        affected_commitment_ids = set()
        for evidence_node in affected_evidence:
            evidence_node.status = "STALE"
            for edge in self.edges:
                if edge.target_id == evidence_node.id and edge.edge_type == EdgeType.SUPPORTED_BY:
                    affected_commitment_ids.add(edge.source_id)
        self.updated_at = datetime.utcnow()
        return list(affected_commitment_ids)

    def to_visualization_data(self) -> dict:
        """Convert to frontend-friendly visualization format."""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.node_type.value,
                    "label": n.label,
                    "status": n.status,
                    **n.properties,
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "id": e.id,
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type.value,
                    "label": e.label or e.edge_type.value,
                }
                for e in self.edges
            ],
        }
