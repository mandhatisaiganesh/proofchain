"""Evidence search and verification tools for Strands agents."""

import json
from strands import tool
from typing import Optional
from ..services.workspace_service import workspace_store


@tool
def search_evidence_chunks(query: str, workspace_id: str = "demo-workspace", top_k: int = 4) -> str:
    """
    Search workspace documents using semantic and keyword matching for relevant evidence chunks.

    Args:
        query: Search query or requirement text to match against evidence.
        workspace_id: The workspace ID to search within.
        top_k: Number of most relevant results to return (default 4).
    """
    retrieval = workspace_store.get_retrieval_service(workspace_id)
    results = retrieval.search(query, top_k=top_k)

    if not results:
        return "No matching evidence chunks found."

    formatted = []
    for chunk, score in results:
        formatted.append({
            "chunk_id": chunk.id,
            "document": chunk.document_name,
            "section": chunk.section,
            "page": chunk.page,
            "score": round(score, 3),
            "text": chunk.text
        })
    return json.dumps(formatted, indent=2)


@tool
def verify_exact_quote(quote: str, document_name: str, workspace_id: str = "demo-workspace") -> str:
    """
    Verify whether a cited quote exists verbatim in a specific document.

    Args:
        quote: The exact phrase or sentence claimed as evidence.
        document_name: The document where the quote should be present.
        workspace_id: Target workspace ID.
    """
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        return f"Workspace '{workspace_id}' not found."

    for doc in ws.documents:
        if doc.filename.lower() == document_name.lower():
            if not doc.extracted_text:
                return "Document text is empty."
            cleaned_quote = " ".join(quote.strip().lower().split())
            cleaned_doc = " ".join(doc.extracted_text.lower().split())

            if cleaned_quote in cleaned_doc:
                return f"VALID: Quote confirmed in '{doc.filename}'."
            else:
                return f"INVALID: Quote was not found in '{doc.filename}'. Possible hallucination or misattribution."

    return f"Document '{document_name}' not found."
