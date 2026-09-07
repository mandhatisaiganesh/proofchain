"""Commitment Graph API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..services.workspace_service import workspace_store

router = APIRouter(prefix="/api/workspaces/{workspace_id}/graph", tags=["graph"])


class InvalidateRequest(BaseModel):
    document_name: str


@router.get("")
def get_graph(workspace_id: str):
    """Get the complete Commitment Graph in visualization-ready node/edge format."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws or not ws.analysis or not ws.analysis.graph:
        if workspace_id == "demo-workspace":
            from ..agents.orchestrator import orchestrator
            ws = workspace_store.load_demo_data("demo-workspace")
            orchestrator.run_pipeline(workspace_id)
        else:
            raise HTTPException(status_code=404, detail="Commitment Graph not found")

    graph_svc = workspace_store.get_graph_service(workspace_id)
    return {
        "workspace_id": workspace_id,
        "visualization": graph_svc.graph_model.to_visualization_data(),
        "summary": graph_svc.get_summary_metrics(),
    }


@router.get("/trace/{node_id}")
def trace_lineage(workspace_id: str, node_id: str):
    """Trace upstream causes and downstream effects of a graph node."""
    graph_svc = workspace_store.get_graph_service(workspace_id)
    result = graph_svc.trace_lineage(node_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/invalidate")
def invalidate_evidence(workspace_id: str, req: InvalidateRequest):
    """
    Evidence Invalidation Cascade:
    Simulates what happens when a document is updated or invalidated (e.g. audit expired).
    Cascades 'AT_RISK' status to all dependent commitments.
    """
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    graph_svc = workspace_store.get_graph_service(workspace_id)
    result = graph_svc.invalidate_document(req.document_name)

    # Recompute workspace metrics to reflect the invalidated commitments
    if ws.analysis:
        for cmt in ws.analysis.commitments:
            for affected in result["affected_commitments"]:
                if cmt.id == affected["id"]:
                    from ..models.commitment import CommitmentStatus
                    cmt.status = CommitmentStatus.AT_RISK
        workspace_store.update_metrics(workspace_id)

    return result
