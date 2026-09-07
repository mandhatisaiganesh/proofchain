"""Actions and Human-in-the-Loop Approval API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..services.workspace_service import workspace_store
from ..models.commitment import ActionStatus, CommitmentStatus

router = APIRouter(prefix="/api/workspaces/{workspace_id}/actions", tags=["actions"])


class ApprovalRequest(BaseModel):
    approver: str = "Authorized Signer"
    notes: Optional[str] = None


class RejectionRequest(BaseModel):
    reason: str
    rejected_by: str = "Authorized Signer"


@router.get("")
def list_actions(workspace_id: str):
    """List recommended remediation actions."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws or not ws.analysis:
        if workspace_id == "demo-workspace":
            from ..agents.orchestrator import orchestrator
            ws = workspace_store.load_demo_data("demo-workspace")
            orchestrator.run_pipeline(workspace_id)
        else:
            raise HTTPException(status_code=404, detail="Workspace analysis not found")

    return ws.analysis.actions


@router.post("/{action_id}/approve")
def approve_action(workspace_id: str, action_id: str, req: ApprovalRequest):
    """
    Human-in-the-loop approval:
    Approves a proposed remediation action, updates its status, and advances
    the associated commitment out of conflict or at-risk state.
    """
    ws = workspace_store.get_workspace(workspace_id)
    if not ws or not ws.analysis:
        raise HTTPException(status_code=404, detail="Workspace analysis not found")

    act = next((a for a in ws.analysis.actions if a.id == action_id), None)
    if not act:
        raise HTTPException(status_code=404, detail="Action not found")

    act.status = ActionStatus.APPROVED
    act.approved_by = req.approver
    act.approved_at = datetime.utcnow()

    # Update associated commitment if approved
    if act.commitment_id:
        cmt = next((c for c in ws.analysis.commitments if c.id == act.commitment_id), None)
        if cmt and cmt.status in [CommitmentStatus.CONFLICT, CommitmentStatus.AT_RISK]:
            cmt.status = CommitmentStatus.RESOLVED

    workspace_store.update_metrics(workspace_id)

    return {
        "status": "APPROVED",
        "action_id": act.id,
        "approved_by": act.approved_by,
        "approved_at": act.approved_at,
    }


@router.post("/{action_id}/reject")
def reject_action(workspace_id: str, action_id: str, req: RejectionRequest):
    """Record human rejection of a proposed action."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws or not ws.analysis:
        raise HTTPException(status_code=404, detail="Workspace analysis not found")

    act = next((a for a in ws.analysis.actions if a.id == action_id), None)
    if not act:
        raise HTTPException(status_code=404, detail="Action not found")

    act.status = ActionStatus.BLOCKED
    act.rejection_reason = req.reason

    return {
        "status": "REJECTED",
        "action_id": act.id,
        "rejection_reason": act.rejection_reason,
    }
