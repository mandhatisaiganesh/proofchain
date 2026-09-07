"""Semantic retrieval service for evidence search.

Uses lightweight numpy-based cosine similarity for the hackathon demo.
For production, replace with FAISS or OpenSearch.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import numpy as np

from ..models import DocumentChunk

logger = logging.getLogger(__name__)


class RetrievalService:
    """In-memory vector store with semantic search."""

    def __init__(self):
        self._chunks: list[DocumentChunk] = []
        self._embeddings: Optional[np.ndarray] = None
        self._bedrock_client = None
        self._bedrock_disabled = False
        self._embedding_model_id = "amazon.titan-embed-text-v2:0"

    @property
    def chunks(self) -> list[DocumentChunk]:
        return self._chunks


    def _get_bedrock_client(self):
        if self._bedrock_disabled:
            return None
        if self._bedrock_client is None:
            try:
                import boto3
                from ..config import get_settings
                settings = get_settings()
                self._bedrock_client = boto3.client(
                    "bedrock-runtime", region_name=settings.aws_region
                )
                self._embedding_model_id = settings.bedrock_embedding_model_id
            except Exception as e:
                logger.warning(f"Could not create Bedrock client: {e}")
                self._bedrock_disabled = True
        return self._bedrock_client

    def _embed_text(self, text: str) -> Optional[np.ndarray]:
        """Embed text using Bedrock Titan Embeddings."""
        if self._bedrock_disabled:
            return self._fallback_embed(text)

        client = self._get_bedrock_client()
        if client is None:
            return self._fallback_embed(text)

        try:
            body = json.dumps({
                "inputText": text[:8000],  # Titan limit
                "dimensions": 256,
                "normalize": True,
            })
            response = client.invoke_model(
                modelId=self._embedding_model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            result = json.loads(response["body"].read())
            return np.array(result["embedding"], dtype=np.float32)
        except Exception as e:
            logger.warning(f"Bedrock embedding failed: {e}. Disabling Bedrock embeddings and using fast deterministic fallback.")
            self._bedrock_disabled = True
            return self._fallback_embed(text)


    def _fallback_embed(self, text: str) -> np.ndarray:
        """Deterministic hash-based embedding fallback when Bedrock is unavailable."""
        import hashlib
        text_lower = text.lower()
        words = text_lower.split()

        # Create a 256-dim vector from word hashes
        vec = np.zeros(256, dtype=np.float32)
        for word in words:
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            for i in range(256):
                bit = (h >> (i % 128)) & 1
                vec[i] += (1.0 if bit else -1.0)

        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Add document chunks to the index."""
        new_embeddings = []
        for chunk in chunks:
            embedding = self._embed_text(chunk.text)
            if embedding is not None:
                chunk.embedding = embedding.tolist()
                new_embeddings.append(embedding)
                self._chunks.append(chunk)

        if new_embeddings:
            new_matrix = np.array(new_embeddings)
            if self._embeddings is not None:
                self._embeddings = np.vstack([self._embeddings, new_matrix])
            else:
                self._embeddings = new_matrix

    def search(
        self,
        query: str,
        top_k: int = 10,
        document_filter: Optional[str] = None,
    ) -> list[tuple[DocumentChunk, float]]:
        """Search for relevant chunks. Returns (chunk, similarity_score) pairs."""
        if self._embeddings is None or len(self._chunks) == 0:
            return []

        query_embedding = self._embed_text(query)
        if query_embedding is None:
            return []

        # Cosine similarity
        similarities = np.dot(self._embeddings, query_embedding)

        # Apply document filter
        if document_filter:
            mask = np.array([
                1.0 if c.document_name == document_filter else 0.0
                for c in self._chunks
            ])
            similarities = similarities * mask

        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                results.append((self._chunks[idx], float(similarities[idx])))

        return results

    def search_for_evidence(
        self,
        requirement_text: str,
        top_k: int = 10,
        exclude_document: Optional[str] = None,
    ) -> list[tuple[DocumentChunk, float]]:
        """Search specifically for evidence related to a requirement.
        Excludes the requirement's source document to find corroborating/contradicting evidence."""
        if self._embeddings is None or len(self._chunks) == 0:
            return []

        query_embedding = self._embed_text(requirement_text)
        if query_embedding is None:
            return []

        similarities = np.dot(self._embeddings, query_embedding)

        # Exclude source document
        if exclude_document:
            for i, chunk in enumerate(self._chunks):
                if chunk.document_name == exclude_document:
                    similarities[i] = 0.0

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Minimum relevance threshold
                results.append((self._chunks[idx], float(similarities[idx])))

        return results

    def clear(self) -> None:
        """Clear the index."""
        self._chunks = []
        self._embeddings = None

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)


# Global retrieval service instance
_retrieval_service: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
