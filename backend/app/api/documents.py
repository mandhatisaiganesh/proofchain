"""Documents API routes."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime

from ..services.workspace_service import workspace_store
from ..services.ingestion import ingest_document
from ..models.workspace import DocumentStatus

router = APIRouter(prefix="/api/workspaces/{workspace_id}/documents", tags=["documents"])


@router.get("")
def list_documents(workspace_id: str):
    """List all documents in the workspace."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        if workspace_id == "demo-workspace":
            ws = workspace_store.load_demo_data("demo-workspace")
        else:
            raise HTTPException(status_code=404, detail="Workspace not found")
    return ws.documents


@router.post("/upload")
async def upload_document(workspace_id: str, file: UploadFile = File(...)):
    """Upload and ingest a document into the workspace."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    doc = ingest_document(file.filename, content)
    doc.status = DocumentStatus.PROCESSED
    ws.documents.append(doc)

    # Index into retrieval engine
    retrieval = workspace_store.get_retrieval_service(workspace_id)
    retrieval.add_chunks(doc.chunks)

    ws.updated_at = datetime.utcnow()

    return {
        "id": doc.id,
        "filename": doc.filename,
        "chunks_count": len(doc.chunks),
        "status": doc.status.value,
        "uploaded_at": doc.uploaded_at,
    }


@router.get("/{document_id}")
def get_document(workspace_id: str, document_id: str):
    """Get single document with chunks."""
    ws = workspace_store.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    for doc in ws.documents:
        if doc.id == document_id or doc.filename.lower() == document_id.lower():
            return doc

    raise HTTPException(status_code=404, detail="Document not found")
