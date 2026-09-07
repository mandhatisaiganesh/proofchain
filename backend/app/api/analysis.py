"""Analysis execution and results API routes."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..services.workspace_service import workspace_store
from ..agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/workspaces/{workspace_id}/analysis", tags=["analysis"])


@router.post("/run")
def trigger_analysis(workspace_id: str):
    """Trigger the multi-agent commitment intelligence analysis pipeline."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        if workspace_id == "demo-workspace":
            ws = workspace_store.load_demo_data("demo-workspace")
        else:
            raise HTTPException(status_code=404, detail="Workspace not found")

    if not ws.documents:
        ws = workspace_store.load_demo_data(workspace_id)

    run = orchestrator.run_pipeline(workspace_id)
    return {
        "run_id": run.id,
        "status": run.status.value,
        "events_count": len(run.events),
        "events": [e.model_dump() for e in run.events],
        "metrics": ws.analysis.metrics.model_dump() if ws.analysis and ws.analysis.metrics else None,
    }


@router.get("")
def get_analysis(workspace_id: str):
    """Get latest completed analysis result."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        if workspace_id == "demo-workspace":
            ws = workspace_store.load_demo_data("demo-workspace")
            orchestrator.run_pipeline(workspace_id)
        else:
            raise HTTPException(status_code=404, detail="Workspace not found")

    if not ws.analysis:
        # Run automatically if not analyzed yet
        orchestrator.run_pipeline(workspace_id)

    return ws.analysis


@router.get("/runs")
def list_runs(workspace_id: str):
    """List agent execution runs with timeline events."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws.runs
