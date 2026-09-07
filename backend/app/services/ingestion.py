"""Document ingestion pipeline — extract text, chunk, embed."""

from __future__ import annotations

import hashlib
import re
from typing import Optional

from ..models import Document, DocumentChunk, DocumentStatus


def validate_file(filename: str, content: bytes, max_size_mb: int = 10) -> tuple[bool, str]:
    """Validate uploaded file. Returns (is_valid, error_message)."""
    allowed_extensions = {".pdf", ".docx", ".txt", ".md"}
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in allowed_extensions:
        return False, f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}"

    max_bytes = max_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        return False, f"File too large ({len(content)} bytes). Maximum: {max_bytes} bytes"

    if len(content) == 0:
        return False, "Empty file"

    return True, ""


def compute_hash(content: bytes) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


def extract_text_from_md(content: str) -> tuple[str, dict]:
    """Extract text and metadata from Markdown content."""
    sections = []
    current_section = ""
    current_heading = "Introduction"
    page = 1

    for line in content.split("\n"):
        if line.startswith("#"):
            if current_section.strip():
                sections.append({
                    "text": current_section.strip(),
                    "section": current_heading,
                    "page": page,
                })
            heading_level = len(line) - len(line.lstrip("#"))
            current_heading = line.lstrip("#").strip()
            current_section = ""
            # Approximate pages every ~3000 chars
            if sum(len(s["text"]) for s in sections) > page * 3000:
                page += 1
        else:
            current_section += line + "\n"

    if current_section.strip():
        sections.append({
            "text": current_section.strip(),
            "section": current_heading,
            "page": page,
        })

    full_text = content
    metadata = {"sections": sections, "page_count": page}
    return full_text, metadata


def extract_text_from_txt(content: str) -> tuple[str, dict]:
    """Extract text from plain text."""
    page = max(1, len(content) // 3000)
    return content, {"sections": [{"text": content, "section": "Full Document", "page": 1}], "page_count": page}


def extract_text(filename: str, content: bytes) -> tuple[str, dict]:
    """Extract text and metadata from a document."""
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext in ("md", "txt"):
        text_content = content.decode("utf-8", errors="replace")
        if ext == "md":
            return extract_text_from_md(text_content)
        return extract_text_from_txt(text_content)

    elif ext == "pdf":
        try:
            import pdfplumber
            import io
            text_parts = []
            sections = []
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    text_parts.append(page_text)
                    sections.append({
                        "text": page_text,
                        "section": f"Page {i+1}",
                        "page": i + 1,
                    })
            return "\n".join(text_parts), {"sections": sections, "page_count": len(text_parts)}
        except ImportError:
            # Fallback: try PyPDF2
            try:
                import PyPDF2
                import io
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                text_parts = []
                sections = []
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    text_parts.append(page_text)
                    sections.append({"text": page_text, "section": f"Page {i+1}", "page": i+1})
                return "\n".join(text_parts), {"sections": sections, "page_count": len(reader.pages)}
            except ImportError:
                return content.decode("utf-8", errors="replace"), {"sections": [], "page_count": 1}

    elif ext == "docx":
        try:
            import docx
            import io
            doc = docx.Document(io.BytesIO(content))
            text_parts = []
            sections = []
            current_section = ""
            current_heading = "Document"
            for para in doc.paragraphs:
                if para.style.name.startswith("Heading"):
                    if current_section.strip():
                        sections.append({"text": current_section.strip(), "section": current_heading, "page": 1})
                    current_heading = para.text
                    current_section = ""
                else:
                    current_section += para.text + "\n"
                text_parts.append(para.text)
            if current_section.strip():
                sections.append({"text": current_section.strip(), "section": current_heading, "page": 1})
            return "\n".join(text_parts), {"sections": sections, "page_count": 1}
        except ImportError:
            return content.decode("utf-8", errors="replace"), {"sections": [], "page_count": 1}

    return content.decode("utf-8", errors="replace"), {"sections": [], "page_count": 1}


def chunk_document(
    document_id: str,
    document_name: str,
    text: str,
    metadata: dict,
    chunk_size: int = 800,
    overlap: int = 200,
) -> list[DocumentChunk]:
    """Chunk document text while preserving provenance (section/page)."""
    chunks = []
    sections = metadata.get("sections", [])

    if sections:
        # Chunk by section, then sub-chunk if needed
        for section_info in sections:
            section_text = section_info["text"]
            section_name = section_info.get("section", "")
            page = section_info.get("page", 1)

            if len(section_text) <= chunk_size:
                chunks.append(DocumentChunk(
                    document_id=document_id,
                    document_name=document_name,
                    text=section_text,
                    page=page,
                    section=section_name,
                    chunk_index=len(chunks),
                ))
            else:
                # Sub-chunk with overlap
                words = section_text.split()
                start = 0
                while start < len(words):
                    end = start + chunk_size // 5  # ~5 chars per word
                    chunk_text = " ".join(words[start:end])
                    chunks.append(DocumentChunk(
                        document_id=document_id,
                        document_name=document_name,
                        text=chunk_text,
                        page=page,
                        section=section_name,
                        chunk_index=len(chunks),
                    ))
                    start = end - overlap // 5
    else:
        # Simple sliding window
        words = text.split()
        start = 0
        while start < len(words):
            end = start + chunk_size // 5
            chunk_text = " ".join(words[start:end])
            chunks.append(DocumentChunk(
                document_id=document_id,
                document_name=document_name,
                text=chunk_text,
                page=1,
                section="",
                chunk_index=len(chunks),
            ))
            start = end - overlap // 5

    return chunks


def ingest_document(filename: str, content: bytes) -> Document:
    """Full document ingestion pipeline."""
    # Validate
    is_valid, error = validate_file(filename, content)
    if not is_valid:
        doc = Document(filename=filename, file_type=filename.rsplit(".", 1)[-1])
        doc.status = DocumentStatus.ERROR
        return doc

    # Extract text
    text, metadata = extract_text(filename, content)

    # Create document
    doc = Document(
        filename=filename,
        file_type=filename.rsplit(".", 1)[-1],
        file_size=len(content),
        content_hash=compute_hash(content),
        extracted_text=text,
        page_count=metadata.get("page_count", 1),
        status=DocumentStatus.PROCESSED,
    )

    # Chunk
    doc.chunks = chunk_document(
        document_id=doc.id,
        document_name=filename,
        text=text,
        metadata=metadata,
    )

    return doc
