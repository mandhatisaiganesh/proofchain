"""Graph Updater Agent — Synthesizes multi-agent findings into the Commitment Graph."""

from __future__ import annotations

import logging
from typing import Optional
from strands import Agent

from .base import get_bedrock_model
from ..models.commitment import (
    Requirement, Commitment, Evidence, Capability, Risk, Action, Conflict
)
from ..models.graph import CommitmentGraph
from ..services.workspace_service import workspace_store
from ..services.graph_service import GraphService

logger = logging.getLogger(__name__)


class GraphUpdaterAgent:
    """Agent that maintains graph consistency, links nodes, and propagates updates."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="GraphUpdaterAgent",
            description="Constructs and maintains topological consistency in the Commitment Graph",
            model=self.model if self.model else None,
        )

    def update_graph(
        self,
        workspace_id: str,
        requirements: list[Requirement],
        commitments: list[Commitment],
        evidences: list[Evidence],
        capabilities: list[Capability],
        conflicts: list[Conflict],
        risks: list[Risk],
        actions: list[Action],
    ) -> CommitmentGraph:
        """Populate the graph with all extracted nodes and directed relationships."""
        graph_svc = workspace_store.get_graph_service(workspace_id)
        # Reset and build fresh graph
        graph_svc.graph_model = CommitmentGraph(workspace_id=workspace_id)
        graph_svc._sync_nx_from_model()

        graph_svc.populate_from_workspace(
            requirements=requirements,
            commitments=commitments,
            evidences=evidences,
            capabilities=capabilities,
            conflicts=conflicts,
            risks=risks,
            actions=actions,
        )

        logger.info(
            f"Commitment Graph updated: {len(graph_svc.graph_model.nodes)} nodes, "
            f"{len(graph_svc.graph_model.edges)} edges."
        )
        return graph_svc.graph_model
