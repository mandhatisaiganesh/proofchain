"""Risks API routes."""

from fastapi import APIRouter, HTTPException
from ..services.workspace_service import workspace_store

router = APIRouter(prefix="/api/workspaces/{workspace_id}/risks", tags=["risks"])


@router.get("")
def list_risks(workspace_id: str):
    """List quantified financial and legal exposure risks."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws or not ws.analysis:
        if workspace_id == "demo-workspace":
            from ..agents.orchestrator import orchestrator
            ws = workspace_store.load_demo_data("demo-workspace")
            orchestrator.run_pipeline(workspace_id)
        else:
            raise HTTPException(status_code=404, detail="Workspace analysis not found")

    return ws.analysis.risks
