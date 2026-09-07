"""Graph service — NetworkX-based commitment graph analysis and invalidation propagation."""

from __future__ import annotations

import networkx as nx
from typing import Optional, Any
from datetime import datetime

from ..models.graph import CommitmentGraph, GraphNode, GraphEdge, NodeType, EdgeType
from ..models.commitment import (
    Commitment, Requirement, Evidence, Capability, Dependency,
    Risk, Action, Verification, Conflict, CommitmentStatus, EvidenceStatus, RiskLevel
)


class GraphService:
    """Operations on the Commitment Graph using NetworkX."""

    def __init__(self, graph: Optional[CommitmentGraph] = None):
        self.graph_model = graph or CommitmentGraph(workspace_id="default")
        self.nx_graph = nx.DiGraph()
        self._sync_nx_from_model()

    def _sync_nx_from_model(self) -> None:
        """Sync internal NetworkX directed graph from Pydantic CommitmentGraph model."""
        self.nx_graph.clear()
        for node in self.graph_model.nodes:
            self.nx_graph.add_node(
                node.id,
                node_type=node.node_type.value,
                label=node.label,
                status=node.status,
                **node.properties
            )
        for edge in self.graph_model.edges:
            self.nx_graph.add_edge(
                edge.source_id,
                edge.target_id,
                edge_id=edge.id,
                edge_type=edge.edge_type.value,
                label=edge.label or edge.edge_type.value,
                **edge.properties
            )

    def add_node(self, node: GraphNode) -> None:
        self.graph_model.add_node(node)
        self.nx_graph.add_node(
            node.id,
            node_type=node.node_type.value,
            label=node.label,
            status=node.status,
            **node.properties
        )

    def add_edge(self, edge: GraphEdge) -> None:
        self.graph_model.add_edge(edge)
        self.nx_graph.add_edge(
            edge.source_id,
            edge.target_id,
            edge_id=edge.id,
            edge_type=edge.edge_type.value,
            label=edge.label or edge.edge_type.value,
            **edge.properties
        )

    def populate_from_workspace(
        self,
        requirements: list[Requirement],
        commitments: list[Commitment],
        evidences: list[Evidence],
        capabilities: list[Capability],
        conflicts: list[Conflict],
        risks: list[Risk],
        actions: list[Action],
    ) -> None:
        """Build graph representation from all workspace domain entities."""
        # 1. Requirements
        for req in requirements:
            self.add_node(GraphNode(
                id=req.id,
                node_type=NodeType.REQUIREMENT,
                label=req.text[:60] + ("..." if len(req.text) > 60 else ""),
                status=req.requirement_type.value,
                properties={
                    "full_text": req.text,
                    "category": req.category,
                    "source_document": req.source_document,
                    "deadline": req.deadline,
                }
            ))

        # 2. Commitments
        for cmt in commitments:
            self.add_node(GraphNode(
                id=cmt.id,
                node_type=NodeType.COMMITMENT,
                label=cmt.title,
                status=cmt.status.value,
                properties={
                    "description": cmt.description,
                    "owner": cmt.owner,
                    "deadline": cmt.deadline,
                    "verification_method": cmt.verification_method,
                    "deliverable": cmt.deliverable,
                }
            ))
            # Edges from requirements
            for req_id in cmt.requirement_ids:
                self.add_edge(GraphEdge(
                    source_id=req_id,
                    target_id=cmt.id,
                    edge_type=EdgeType.CREATES,
                    label="creates"
                ))

        # 3. Evidence
        for ev in evidences:
            self.add_node(GraphNode(
                id=ev.id,
                node_type=NodeType.EVIDENCE,
                label=ev.evidence_text[:50] + "...",
                status=ev.status.value,
                properties={
                    "evidence_text": ev.evidence_text,
                    "source_document": ev.source_document,
                    "section": ev.section,
                    "confidence": ev.confidence,
                }
            ))
            # Connect evidence to commitment
            for c_id in ev.related_commitment_ids:
                edge_type = EdgeType.CONTRADICTED_BY if ev.status == EvidenceStatus.CONTRADICTORY else EdgeType.SUPPORTED_BY
                self.add_edge(GraphEdge(
                    source_id=c_id,
                    target_id=ev.id,
                    edge_type=edge_type,
                    label=edge_type.value
                ))

        # 4. Capabilities
        for cap in capabilities:
            self.add_node(GraphNode(
                id=cap.id,
                node_type=NodeType.CAPABILITY,
                label=cap.name,
                status=cap.temporal_state.value,
                properties={
                    "available": cap.available,
                    "current_state": cap.current_state,
                    "gap_description": cap.gap_description,
                }
            ))
            # Connect commitment to capability if matched
            for cmt in commitments:
                if cap.id in cmt.required_capabilities:
                    self.add_edge(GraphEdge(
                        source_id=cmt.id,
                        target_id=cap.id,
                        edge_type=EdgeType.REQUIRES,
                        label="requires"
                    ))

        # 5. Risks
        for rk in risks:
            self.add_node(GraphNode(
                id=rk.id,
                node_type=NodeType.RISK,
                label=f"{rk.level.value}: {rk.title}",
                status=rk.level.value,
                properties={
                    "description": rk.description,
                    "mitigation": rk.mitigation,
                }
            ))
            if rk.commitment_id:
                self.add_edge(GraphEdge(
                    source_id=rk.commitment_id,
                    target_id=rk.id,
                    edge_type=EdgeType.HAS_RISK,
                    label="has_risk"
                ))

        # 6. Actions
        for act in actions:
            self.add_node(GraphNode(
                id=act.id,
                node_type=NodeType.ACTION,
                label=act.title,
                status=act.status.value,
                properties={
                    "description": act.description,
                    "owner": act.owner,
                    "priority": act.priority.value,
                    "deadline": act.deadline,
                }
            ))
            if act.commitment_id:
                self.add_edge(GraphEdge(
                    source_id=act.commitment_id,
                    target_id=act.id,
                    edge_type=EdgeType.REQUIRES_ACTION,
                    label="requires_action"
                ))

        # 7. Conflicts as contradictory edges
        for conf in conflicts:
            if conf.commitment_id:
                self.add_edge(GraphEdge(
                    source_id=conf.commitment_id,
                    target_id=conf.id,
                    edge_type=EdgeType.CONTRADICTED_BY,
                    label=conf.conflict_type,
                    properties={"severity": conf.severity.value, "recommendation": conf.recommendation}
                ))


    def trace_lineage(self, node_id: str) -> dict[str, Any]:
        """Trace backward upstream to requirements and forward downstream to risks/actions."""
        if node_id not in self.nx_graph:
            return {"error": f"Node {node_id} not found"}

        # Upstream (ancestors)
        upstream_ids = nx.ancestors(self.nx_graph, node_id)
        # Downstream (descendants)
        downstream_ids = nx.descendants(self.nx_graph, node_id)

        all_ids = upstream_ids.union(downstream_ids).union({node_id})
        subgraph_nodes = [self.graph_model.get_node(nid) for nid in all_ids if self.graph_model.get_node(nid)]
        subgraph_edges = [
            e for e in self.graph_model.edges
            if e.source_id in all_ids and e.target_id in all_ids
        ]

        return {
            "root_node_id": node_id,
            "upstream_count": len(upstream_ids),
            "downstream_count": len(downstream_ids),
            "nodes": [n.model_dump() for n in subgraph_nodes if n],
            "edges": [e.model_dump() for e in subgraph_edges],
        }

    def detect_unsupported_commitments(self) -> list[str]:
        """Find commitments that have no SUPPORTED_BY evidence edges."""
        unsupported = []
        for node in self.graph_model.get_nodes_by_type(NodeType.COMMITMENT):
            has_supporting_evidence = False
            for edge in self.graph_model.edges:
                if edge.source_id == node.id and edge.edge_type == EdgeType.SUPPORTED_BY:
                    has_supporting_evidence = True
                    break
            if not has_supporting_evidence:
                unsupported.append(node.id)
        return unsupported

    def invalidate_document(self, document_name: str) -> dict[str, Any]:
        """
        Evidence Invalidation Cascade:
        When a document changes, invalidate its evidence, flag affected commitments,
        and recalculate risk level across downstream nodes.
        """
        affected_commitment_ids = self.graph_model.invalidate_evidence(document_name)
        affected_commitments = []

        for cid in affected_commitment_ids:
            cmt_node = self.graph_model.get_node(cid)
            if cmt_node:
                cmt_node.status = CommitmentStatus.AT_RISK.value
                affected_commitments.append({
                    "id": cmt_node.id,
                    "label": cmt_node.label,
                    "new_status": CommitmentStatus.AT_RISK.value,
                    "reason": f"Supporting evidence from document '{document_name}' was invalidated"
                })

        self._sync_nx_from_model()
        return {
            "invalidated_document": document_name,
            "affected_commitments_count": len(affected_commitments),
            "affected_commitments": affected_commitments,
            "graph_updated_at": self.graph_model.updated_at.isoformat()
        }

    def get_summary_metrics(self) -> dict[str, int]:
        """Calculate live summary counts of nodes, edges, and statuses."""
        nodes = self.graph_model.nodes
        return {
            "total_nodes": len(nodes),
            "total_edges": len(self.graph_model.edges),
            "requirements": len([n for n in nodes if n.node_type == NodeType.REQUIREMENT]),
            "commitments": len([n for n in nodes if n.node_type == NodeType.COMMITMENT]),
            "evidence": len([n for n in nodes if n.node_type == NodeType.EVIDENCE]),
            "capabilities": len([n for n in nodes if n.node_type == NodeType.CAPABILITY]),
            "risks": len([n for n in nodes if n.node_type == NodeType.RISK]),
            "actions": len([n for n in nodes if n.node_type == NodeType.ACTION]),
            "conflicts": len([e for e in self.graph_model.edges if e.edge_type == EdgeType.CONTRADICTED_BY]),
        }
