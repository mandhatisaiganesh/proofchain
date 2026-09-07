"""Graph query and inspection tools for Strands agents."""

import json
from strands import tool
from typing import Optional
from ..services.workspace_service import workspace_store


@tool
def query_graph_node(node_id: str, workspace_id: str = "demo-workspace") -> str:
    """
    Retrieve details and connections for a specific node in the Commitment Graph.

    Args:
        node_id: The ID of the node (e.g. 'CMT-XXXX', 'REQ-XXXX', 'EVD-XXXX').
        workspace_id: Target workspace ID.
    """
    graph_svc = workspace_store.get_graph_service(workspace_id)
    node = graph_svc.graph_model.get_node(node_id)
    if not node:
        return f"Node '{node_id}' not found in Commitment Graph."

    edges = graph_svc.graph_model.get_edges_for_node(node_id)
    return json.dumps({
        "node": node.model_dump(),
        "connected_edges": [e.model_dump() for e in edges]
    }, indent=2, default=str)


@tool
def trace_node_lineage(node_id: str, workspace_id: str = "demo-workspace") -> str:
    """
    Trace upstream ancestors (requirements, origin docs) and downstream descendants (risks, actions) for a node.

    Args:
        node_id: The ID of the node to trace.
        workspace_id: Target workspace ID.
    """
    graph_svc = workspace_store.get_graph_service(workspace_id)
    lineage = graph_svc.trace_lineage(node_id)
    return json.dumps(lineage, indent=2, default=str)


@tool
def get_graph_metrics(workspace_id: str = "demo-workspace") -> str:
    """
    Get summary statistics and health counts from the Commitment Graph.

    Args:
        workspace_id: Target workspace ID.
    """
    graph_svc = workspace_store.get_graph_service(workspace_id)
    metrics = graph_svc.get_summary_metrics()
    unsupported = graph_svc.detect_unsupported_commitments()
    metrics["unsupported_commitments_count"] = len(unsupported)
    metrics["unsupported_commitment_ids"] = unsupported
    return json.dumps(metrics, indent=2)
