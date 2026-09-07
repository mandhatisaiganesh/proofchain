"""Commitments API routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..services.workspace_service import workspace_store
from ..models.commitment import CommitmentStatus

router = APIRouter(prefix="/api/workspaces/{workspace_id}/commitments", tags=["commitments"])


@router.get("")
def list_commitments(
    workspace_id: str,
    status: Optional[str] = Query(None, description="Filter by status, e.g. VERIFIED, CONFLICT, UNVERIFIED")
):
    """List commitments for a workspace with optional status filter."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws or not ws.analysis:
        if workspace_id == "demo-workspace":
            from ..agents.orchestrator import orchestrator
            ws = workspace_store.load_demo_data("demo-workspace")
            orchestrator.run_pipeline(workspace_id)
        else:
            raise HTTPException(status_code=404, detail="Workspace analysis not found")

    commitments = ws.analysis.commitments
    if status:
        stat_upper = status.upper()
        commitments = [c for c in commitments if c.status.value == stat_upper]

    return commitments


@router.get("/{commitment_id}")
def get_commitment(workspace_id: str, commitment_id: str):
    """Get full commitment details with bound evidence, verification audit, and risks."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws or not ws.analysis:
        raise HTTPException(status_code=404, detail="Workspace analysis not found")

    cmt = next((c for c in ws.analysis.commitments if c.id == commitment_id), None)
    if not cmt:
        raise HTTPException(status_code=404, detail="Commitment not found")

    # Gather related evidence
    evidences = [e for e in ws.analysis.evidence if cmt.id in e.related_commitment_ids or e.id in cmt.evidence_ids]
    # Related verifications
    verifications = [v for v in ws.analysis.verifications if v.commitment_id == cmt.id]
    # Related risks
    risks = [r for r in ws.analysis.risks if r.commitment_id == cmt.id]
    # Related actions
    actions = [a for a in ws.analysis.actions if a.commitment_id == cmt.id]

    return {
        "commitment": cmt,
        "evidence": evidences,
        "verifications": verifications,
        "risks": risks,
        "actions": actions,
    }
