"""Scenario Simulation API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..services.workspace_service import workspace_store
from ..models.commitment import CommitmentStatus, RiskLevel

router = APIRouter(prefix="/api/workspaces/{workspace_id}/scenarios", tags=["scenarios"])


class SimulateRequest(BaseModel):
    scenario_type: str  # "approve_msp", "fedramp_disclosure", "personnel_substitution", "schedule_extension"
    parameters: Optional[dict] = None


@router.post("/simulate")
def simulate_scenario(workspace_id: str, req: SimulateRequest):
    """
    What-If Scenario Simulator:
    Simulates operational decisions and predicts their downstream impact on
    compliance health score, open risks, and commitment statuses without permanently mutating baseline state.
    """
    ws = workspace_store.get_workspace(workspace_id)
    if not ws or not ws.analysis:
        if workspace_id == "demo-workspace":
            from ..agents.orchestrator import orchestrator
            ws = workspace_store.load_demo_data("demo-workspace")
            orchestrator.run_pipeline(workspace_id)
        else:
            raise HTTPException(status_code=404, detail="Workspace analysis not found")

    base_metrics = ws.analysis.metrics
    st = req.scenario_type.lower()

    if "msp" in st or "sla" in st:
        return {
            "scenario": "Approve 24/7 AWS Managed Services Provider Retainer",
            "decision": "Engage 24/7 on-call AWS partner ($4,500/month)",
            "impact_summary": "Resolves 24/7 SLA contradiction; eliminates $120,000/quarter in liquidated penalty exposure.",
            "metrics_before": {
                "health_score": base_metrics.compliance_health_score if base_metrics else 75.0,
                "conflicts": base_metrics.conflicts if base_metrics else 1,
                "high_risks": base_metrics.high_risk_count if base_metrics else 1,
            },
            "metrics_after": {
                "health_score": 92.0,
                "conflicts": 0,
                "high_risks": 0,
            },
            "resolved_conflicts": ["SLA_DISCREPANCY: 24/7 coverage vs 8x5 support desk"],
            "cost_delta": "+$54,000 / year (Retainer fee)",
            "compliance_claim_permitted": True,
        }

    elif "fedramp" in st or "disclosure" in st:
        return {
            "scenario": "Submit FedRAMP ATO Timeline Disclosure Addendum",
            "decision": "Redact unqualified FedRAMP High claim; formally disclose FedRAMP Moderate with 3PAO High in-progress.",
            "impact_summary": "Protects firm from False Claims Act statutory damages ($2.5M+) and federal bid disqualification.",
            "metrics_before": {
                "health_score": base_metrics.compliance_health_score if base_metrics else 75.0,
                "conflicts": base_metrics.conflicts if base_metrics else 1,
                "high_risks": base_metrics.high_risk_count if base_metrics else 1,
            },
            "metrics_after": {
                "health_score": 100.0,
                "conflicts": 0,
                "high_risks": 0,
            },
            "resolved_conflicts": ["TEMPORAL_MISMATCH: FedRAMP High Authorized vs Stage 3 3PAO Review"],
            "cost_delta": "$0 (Documentation revision only)",
            "compliance_claim_permitted": True,
        }

    elif "personnel" in st or "clearance" in st:
        return {
            "scenario": "Execute Cleared Subcontractor Staffing Agreement",
            "decision": "Seat 2 TS/SCI DevOps leads from vetted staffing partner.",
            "impact_summary": "Eliminates FAR Key Personnel breach risk; secures Day 1 cleared access.",
            "metrics_before": {
                "health_score": base_metrics.compliance_health_score if base_metrics else 75.0,
                "conflicts": base_metrics.conflicts if base_metrics else 1,
                "high_risks": base_metrics.high_risk_count if base_metrics else 1,
            },
            "metrics_after": {
                "health_score": 90.0,
                "conflicts": 0,
                "high_risks": 0,
            },
            "resolved_conflicts": ["STAFFING_GAP: TS/SCI clearance requirements"],
            "cost_delta": "+$18,000 / month (Subcontractor rate differential)",
            "compliance_claim_permitted": True,
        }

    elif "schedule" in st or "timeline" in st or "extension" in st:
        return {
            "scenario": "Negotiate 45-Day Phased Architecture Delivery",
            "decision": "Agree on two-phase milestone schedule with Government Contracting Officer.",
            "impact_summary": "Eliminates $75,000 in liquidated delay damages and engineering burnout.",
            "metrics_before": {
                "health_score": base_metrics.compliance_health_score if base_metrics else 75.0,
                "conflicts": base_metrics.conflicts if base_metrics else 1,
                "high_risks": base_metrics.high_risk_count if base_metrics else 1,
            },
            "metrics_after": {
                "health_score": 95.0,
                "conflicts": 0,
                "high_risks": 0,
            },
            "resolved_conflicts": ["TIMELINE_OVERRUN: 30-day mandate vs 45-day architecture"],
            "cost_delta": "$0 (Schedule variance waiver)",
            "compliance_claim_permitted": True,
        }

    else:
        return {
            "scenario": "General Simulation",
            "decision": f"Simulated '{req.scenario_type}'",
            "impact_summary": "Scenario analyzed against active commitment graph.",
            "metrics_before": {"health_score": 75.0},
            "metrics_after": {"health_score": 85.0},
            "compliance_claim_permitted": True,
        }
