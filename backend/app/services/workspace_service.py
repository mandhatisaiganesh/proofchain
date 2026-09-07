"""Workspace management and storage service."""

from __future__ import annotations

import os
import json
import logging
from typing import Optional, Dict
from datetime import datetime

from ..models.workspace import (
    Workspace, Document, DocumentChunk, DocumentStatus,
    AgentRun, AgentEvent, AgentRunStatus, DashboardMetrics, AnalysisResult
)
from ..models.commitment import (
    Requirement, Commitment, Evidence, Capability, Dependency,
    Risk, Action, Conflict, Verification,
    CommitmentStatus, RiskLevel, ActionStatus
)
from ..models.graph import CommitmentGraph
from .graph_service import GraphService
from .ingestion import ingest_document
from .retrieval import RetrievalService
from ..demo.synthetic_docs import DEMO_DOCUMENTS

logger = logging.getLogger(__name__)


class WorkspaceStore:
    """In-memory workspace store with persistence and optional DynamoDB/S3 backing."""

    def __init__(self):
        self._workspaces: Dict[str, Workspace] = {}
        self._graphs: Dict[str, GraphService] = {}
        self._retrieval_services: Dict[str, RetrievalService] = {}

    def get_or_create_workspace(self, workspace_id: str, name: Optional[str] = None) -> Workspace:
        if workspace_id not in self._workspaces:
            ws = Workspace(
                id=workspace_id,
                name=name or f"Workspace {workspace_id}",
                description="ProofChain commitment intelligence workspace",
                analysis=AnalysisResult(workspace_id=workspace_id)
            )
            self._workspaces[workspace_id] = ws
            self._graphs[workspace_id] = GraphService(CommitmentGraph(workspace_id=workspace_id))
            self._retrieval_services[workspace_id] = RetrievalService()
        return self._workspaces[workspace_id]

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_id)

    def list_workspaces(self) -> list[Workspace]:
        return list(self._workspaces.values())

    def get_graph_service(self, workspace_id: str) -> GraphService:
        if workspace_id not in self._graphs:
            self.get_or_create_workspace(workspace_id)
        return self._graphs[workspace_id]

    def get_retrieval_service(self, workspace_id: str) -> RetrievalService:
        if workspace_id not in self._retrieval_services:
            self.get_or_create_workspace(workspace_id)
        return self._retrieval_services[workspace_id]

    def load_demo_data(self, workspace_id: str = "demo-workspace") -> Workspace:
        """Load synthetic demo documents into the workspace and run indexing."""
        ws = self.get_or_create_workspace(workspace_id, name="Federal Cloud Modernization (FedRFP-2026)")
        retrieval = self.get_retrieval_service(workspace_id)

        # Ingest all demo documents if not already loaded
        if not ws.documents:
            for filename, content in DEMO_DOCUMENTS.items():
                file_bytes = content.encode("utf-8")
                doc = ingest_document(filename, file_bytes)
                doc.status = DocumentStatus.PROCESSED
                ws.documents.append(doc)
                retrieval.add_chunks(doc.chunks)

            ws.updated_at = datetime.utcnow()
            logger.info(f"Loaded {len(ws.documents)} demo documents with {len(retrieval.chunks)} chunks.")

        return ws

    def update_metrics(self, workspace_id: str) -> DashboardMetrics:
        """Recalculate workspace metrics strictly from actual analysis data."""
        ws = self.get_workspace(workspace_id)
        if not ws or not ws.analysis:
            return DashboardMetrics()

        metrics = DashboardMetrics.compute_from(ws.analysis)
        metrics.documents_analyzed = len(ws.documents)
        ws.analysis.metrics = metrics
        return metrics



# Global singleton instance
workspace_store = WorkspaceStore()
