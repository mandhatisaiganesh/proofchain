"""Tests for document ingestion, chunking, and retrieval indexing."""

import pytest
from app.services.ingestion import ingest_document, chunk_document, validate_file, compute_hash
from app.services.retrieval import RetrievalService
from app.models.workspace import DocumentStatus


def test_validate_file():
    valid, err = validate_file("test.md", b"# Test", max_size_mb=10)
    assert valid is True
    assert err == ""

    valid, err = validate_file("test.exe", b"binary", max_size_mb=10)
    assert valid is False
    assert "Unsupported file type" in err

    valid, err = validate_file("empty.txt", b"", max_size_mb=10)
    assert valid is False
    assert "Empty" in err


def test_ingest_markdown_document():
    content = b"""# Federal Cloud RFP
## Section 1: Security Mandate
The Contractor shall maintain continuous FedRAMP Moderate authorization on AWS GovCloud.
All data at rest must be encrypted using FIPS 140-3 validated cryptographic modules.

## Section 2: SLA & Availability
The platform shall guarantee 99.99% monthly availability with 15-minute response for Sev-1 incidents.
"""
    doc = ingest_document("RFP.md", content)
    assert doc.status == DocumentStatus.PROCESSED
    assert len(doc.chunks) >= 2
    assert doc.content_hash is not None
    assert "FedRAMP Moderate" in doc.extracted_text


def test_chunking_with_provenance():
    metadata = {
        "sections": [
            {"text": "Line 1\nLine 2", "section": "Header 1", "page": 1},
            {"text": "Line 3\nLine 4", "section": "Header 2", "page": 1},
        ],
        "page_count": 1
    }
    chunks = chunk_document("DOC-1", "Spec.md", "Full text", metadata, chunk_size=200)
    assert len(chunks) == 2
    assert chunks[0].document_name == "Spec.md"
    assert chunks[0].section == "Header 1"
    assert chunks[1].section == "Header 2"


def test_retrieval_fallback_indexing():
    retrieval = RetrievalService()
    doc = ingest_document("Test.md", b"# Architecture\nAWS GovCloud multi-region failover across us-gov-west-1 and us-gov-east-1.")
    retrieval.add_chunks(doc.chunks)

    assert len(retrieval.chunks) > 0
    results = retrieval.search("GovCloud failover", top_k=2)
    assert len(results) > 0
    chunk, score = results[0]
    assert "GovCloud" in chunk.text
