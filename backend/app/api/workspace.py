"""Workspace API routes."""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from ..services.workspace_service import workspace_store
from ..models.workspace import Workspace, DashboardMetrics

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])


class CreateWorkspaceRequest(BaseModel):
    name: str
    description: Optional[str] = ""


@router.get("", response_model=list[dict])
def list_workspaces():
    """List all available workspaces."""
    workspaces = workspace_store.list_workspaces()
    if not workspaces:
        # Automatically load demo workspace if none exist
        ws = workspace_store.load_demo_data("demo-workspace")
        workspaces = [ws]

    return [
        {
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "documents_count": len(w.documents),
            "created_at": w.created_at,
            "updated_at": w.updated_at,
        }
        for w in workspaces
    ]


@router.post("", response_model=dict)
def create_workspace(req: CreateWorkspaceRequest):
    """Create a new workspace."""
    import uuid
    ws_id = f"WS-{uuid.uuid4().hex[:8].upper()}"
    ws = workspace_store.get_or_create_workspace(ws_id, name=req.name)
    ws.description = req.description or ""
    return {"id": ws.id, "name": ws.name, "description": ws.description}


@router.get("/{workspace_id}")
def get_workspace(workspace_id: str):
    """Get full workspace details."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        # Try loading demo if it's the demo-workspace
        if workspace_id == "demo-workspace":
            ws = workspace_store.load_demo_data("demo-workspace")
        else:
            raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


@router.get("/{workspace_id}/metrics")
def get_workspace_metrics(workspace_id: str):
    """Get calculated dashboard metrics for the workspace."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    metrics = workspace_store.update_metrics(workspace_id)
    return metrics


@router.post("/{workspace_id}/demo")
def load_demo(workspace_id: str):
    """Load or reload demo dataset and index into workspace."""
    ws = workspace_store.load_demo_data(workspace_id)
    return {
        "status": "success",
        "workspace_id": ws.id,
        "documents_loaded": len(ws.documents),
    }
