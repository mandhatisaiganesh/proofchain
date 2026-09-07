"""Multi-Agent Orchestrator — Coordinates the full ProofChain agentic analysis pipeline."""

from __future__ import annotations

import time
import logging
from datetime import datetime
from typing import Optional, Callable
from strands import Agent

from .base import get_bedrock_model
from .requirement import RequirementAgent
from .commitment import CommitmentAgent
from .evidence import EvidenceAgent
from .conflict import ConflictAgent
from .capability import CapabilityAgent
from .risk import RiskAgent
from .action import ActionAgent
from .verification import VerificationAgent
from .graph_updater import GraphUpdaterAgent

from ..models.workspace import (
    Workspace, AgentRun, AgentEvent, AgentRunStatus, AnalysisResult, DashboardMetrics
)
from ..services.workspace_service import workspace_store

logger = logging.getLogger(__name__)


ORCHESTRATOR_SYSTEM_PROMPT = """You are the ProofChain Principal Multi-Agent Orchestrator.
You oversee the rigorous, evidence-grounded evaluation of contractual promises, regulatory commitments,
and enterprise delivery capabilities. You coordinate specialized agents to discover truth, verify claims,
and prevent false compliance.
"""


class OrchestratorAgent:
    """Master orchestrator executing the 10-step multi-agent analysis pipeline."""

    def __init__(self):
        self.model = get_bedrock_model()
        self.strands_agent = Agent(
            name="OrchestratorAgent",
            description="Coordinates specialized agents across ingestion, extraction, conflict detection, and graph synthesis",
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            model=self.model if self.model else None,
        )

        # Child specialized agents
        self.req_agent = RequirementAgent()
        self.cmt_agent = CommitmentAgent()
        self.evd_agent = EvidenceAgent()
        self.cnf_agent = ConflictAgent()
        self.cap_agent = CapabilityAgent()
        self.rsk_agent = RiskAgent()
        self.act_agent = ActionAgent()
        self.ver_agent = VerificationAgent()
        self.grp_agent = GraphUpdaterAgent()

    def run_pipeline(
        self,
        workspace_id: str,
        event_callback: Optional[Callable[[AgentEvent], None]] = None
    ) -> AgentRun:
        """
        Execute the end-to-end multi-agent pipeline:
        1. Requirement Extraction
        2. Commitment Synthesis
        3. Evidence Grounding & RAG Retrieval
        4. Conflict & Contradiction Discovery
        5. Capability Mapping
        6. Risk & Exposure Quantification
        7. Human-in-the-Loop Action Generation
        8. Cross-Verification Auditing
        9. Topological Commitment Graph Synthesis
        10. Metrics Computation & Persistence
        """
        ws = workspace_store.get_workspace(workspace_id)
        if not ws:
            raise ValueError(f"Workspace '{workspace_id}' not found.")

        run = AgentRun(
            workspace_id=workspace_id,
            status=AgentRunStatus.RUNNING,
            start_time=datetime.utcnow()
        )
        ws.runs.append(run)

        def emit_event(agent_name: str, event_text: str, status: AgentRunStatus = AgentRunStatus.RUNNING, details: str = "", start_t: float = 0.0):
            duration = int((time.time() - start_t) * 1000) if start_t > 0 else None
            evt = AgentEvent(
                agent=agent_name,
                event=event_text,
                status=status,
                details=details,
                duration_ms=duration,
                timestamp=datetime.utcnow(),
            )
            run.events.append(evt)
            if event_callback:
                try:
                    event_callback(evt)
                except Exception as ex:
                    logger.warning(f"Event callback failed: {ex}")

        overall_start = time.time()
        emit_event("Orchestrator", "Initiated autonomous multi-agent analysis run", AgentRunStatus.RUNNING)

        try:
            # Step 1: Requirement Extraction
            t0 = time.time()
            emit_event("RequirementAgent", "Analyzing procurement & contract text for explicit requirements", AgentRunStatus.RUNNING)
            requirements = self.req_agent.extract_requirements(workspace_id)
            emit_event("RequirementAgent", f"Extracted {len(requirements)} contractual requirements across categories", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 2: Commitment Synthesis
            t0 = time.time()
            emit_event("CommitmentAgent", "Synthesizing actionable commitments with owners and deliverables", AgentRunStatus.RUNNING)
            commitments = self.cmt_agent.generate_commitments(workspace_id, requirements)
            emit_event("CommitmentAgent", f"Formulated {len(commitments)} structured organizational commitments", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 3: Evidence Grounding
            t0 = time.time()
            emit_event("EvidenceAgent", "Executing semantic RAG search to ground commitments in source citations", AgentRunStatus.RUNNING)
            evidences = self.evd_agent.ground_commitments(workspace_id, commitments)
            emit_event("EvidenceAgent", f"Bound {len(evidences)} verified evidence citations with provenance", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 4: Conflict Detection
            t0 = time.time()
            emit_event("ConflictAgent", "Scanning commitment and evidence graph for contradictions & false compliance claims", AgentRunStatus.RUNNING)
            conflicts = self.cnf_agent.detect_conflicts(workspace_id, commitments, evidences)
            emit_event("ConflictAgent", f"Discovered {len(conflicts)} critical contradictions (SLA, FedRAMP, Schedule, Clearance)", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 5: Capability Mapping
            t0 = time.time()
            emit_event("CapabilityAgent", "Cataloging organizational capabilities and temporal maturity states", AgentRunStatus.RUNNING)
            capabilities = self.cap_agent.extract_capabilities(workspace_id, commitments)
            emit_event("CapabilityAgent", f"Mapped {len(capabilities)} operational capabilities across temporal states", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 6: Risk Quantification
            t0 = time.time()
            emit_event("RiskAgent", "Calculating financial exposure, liquidated damages, and False Claims Act liability", AgentRunStatus.RUNNING)
            risks = self.rsk_agent.assess_risks(workspace_id, commitments, conflicts)
            emit_event("RiskAgent", f"Quantified {len(risks)} high/critical risk items with financial exposures", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 7: Action Generation
            t0 = time.time()
            emit_event("ActionAgent", "Formulating human-in-the-loop remediation proposals and redline workflows", AgentRunStatus.RUNNING)
            actions = self.act_agent.generate_actions(workspace_id, commitments, conflicts, risks)
            emit_event("ActionAgent", f"Proposed {len(actions)} remediation actions requiring human sign-off", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 8: Verification Auditing
            t0 = time.time()
            emit_event("VerificationAgent", "Executing adversarial cross-verification of all claims", AgentRunStatus.RUNNING)
            verifications = self.ver_agent.verify_commitments(workspace_id, commitments, evidences)
            emit_event("VerificationAgent", f"Completed {len(verifications)} formal commitment verification audits", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 9: Graph Synthesis
            t0 = time.time()
            emit_event("GraphUpdaterAgent", "Constructing topological Commitment Graph with NetworkX", AgentRunStatus.RUNNING)
            graph = self.grp_agent.update_graph(
                workspace_id=workspace_id,
                requirements=requirements,
                commitments=commitments,
                evidences=evidences,
                capabilities=capabilities,
                conflicts=conflicts,
                risks=risks,
                actions=actions,
            )
            emit_event("GraphUpdaterAgent", f"Graph generated: {len(graph.nodes)} nodes, {len(graph.edges)} directed edges", AgentRunStatus.COMPLETED, start_t=t0)

            # Step 10: Store Results & Recompute Metrics
            analysis = AnalysisResult(
                workspace_id=workspace_id,
                run_id=run.id,
                requirements=requirements,
                commitments=commitments,
                evidence=evidences,
                capabilities=capabilities,
                conflicts=conflicts,
                risks=risks,
                actions=actions,
                verifications=verifications,
                graph=graph,
            )
            ws.analysis = analysis
            metrics = workspace_store.update_metrics(workspace_id)

            run.status = AgentRunStatus.COMPLETED
            run.end_time = datetime.utcnow()

            emit_event(
                "Orchestrator",
                f"Multi-Agent analysis completed in {round(time.time() - overall_start, 2)}s. Health score: {metrics.compliance_health_score if hasattr(metrics, 'compliance_health_score') else 0}%",
                AgentRunStatus.COMPLETED
            )

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            run.status = AgentRunStatus.FAILED
            run.end_time = datetime.utcnow()
            run.error = str(e)
            emit_event("Orchestrator", f"Pipeline encountered error: {e}", AgentRunStatus.FAILED)
            raise

        return run


# Global singleton orchestrator
orchestrator = OrchestratorAgent()
