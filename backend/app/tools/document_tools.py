"""Document retrieval and inspection tools for Strands agents."""

from strands import tool
from typing import Optional
from ..services.workspace_service import workspace_store


@tool
def read_document_text(document_name: str, workspace_id: str = "demo-workspace") -> str:
    """
    Read the full extracted text of a document from the workspace.

    Args:
        document_name: The name or filename of the document (e.g. 'RFP.md', 'SOW.md').
        workspace_id: The workspace ID containing the document.
    """
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        return f"Error: Workspace '{workspace_id}' not found."

    for doc in ws.documents:
        if doc.filename.lower() == document_name.lower():
            if doc.extracted_text:
                return doc.extracted_text[:12000]  # Truncate if very large
            return "Document has no extracted text."

    available = [d.filename for d in ws.documents]
    return f"Document '{document_name}' not found. Available documents: {available}"


@tool
def list_workspace_documents(workspace_id: str = "demo-workspace") -> str:
    """
    List all documents currently available in the given workspace with their status.

    Args:
        workspace_id: The ID of the workspace to inspect.
    """
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        return f"Workspace '{workspace_id}' not found."

    if not ws.documents:
        return "No documents found in workspace. Run load_demo_data or upload files."

    res = []
    for d in ws.documents:
        res.append(f"- {d.filename} ({d.file_type}, {d.file_size} bytes, {len(d.chunks)} chunks, status: {d.status.value})")
    return "\n".join(res)
