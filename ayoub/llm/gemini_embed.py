"""
ayoub/llm/gemini_embed.py — Gemini Embedding 1 (gemini-embedding-exp-03-07).

Gemini Embedding 1  →  gemini-embedding-001      (100 RPM, 3072-dim)
Gemini Embedding 2  →  gemini-embedding-2-preview (100 RPM, experimental)

Free tier: 100 RPM / 10M tokens per minute
Used for: semantic memory search, document similarity, RAG

Google docs:
  https://ai.google.dev/gemini-api/docs/embeddings
"""
from __future__ import annotations

from google import genai
from google.genai import types

from ayoub.config import GOOGLE_API_KEY


# ── Task types ────────────────────────────────────────────────────────────────
TASK_RETRIEVAL_DOCUMENT  = "RETRIEVAL_DOCUMENT"
TASK_RETRIEVAL_QUERY     = "RETRIEVAL_QUERY"
TASK_SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
TASK_CLASSIFICATION      = "CLASSIFICATION"
TASK_CLUSTERING          = "CLUSTERING"

EMBED_MODEL = "gemini-embedding-001"   # Gemini Embedding 1, 100 RPM free


class GeminiEmbedder:
    """
    Wraps Gemini Embedding 1 for generating text embeddings.

    Usage:
        embedder = GeminiEmbedder()
        vector   = embedder.embed("What is quantum computing?")
        # → list of 3072 floats

    Bulk embed:
        vectors  = embedder.embed_bulk(["text 1", "text 2"])
    """

    def __init__(self, api_key: str = GOOGLE_API_KEY):
        self._client = genai.Client(api_key=api_key)

    def embed(
        self,
        text: str,
        task_type: str = TASK_SEMANTIC_SIMILARITY,
    ) -> list[float]:
        """Return a single embedding vector for `text`."""
        result = self._client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        return result.embeddings[0].values

    def embed_bulk(
        self,
        texts: list[str],
        task_type: str = TASK_SEMANTIC_SIMILARITY,
    ) -> list[list[float]]:
        """Return embedding vectors for a list of texts (batched)."""
        result = self._client.models.embed_content(
            model=EMBED_MODEL,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        return [e.values for e in result.embeddings]

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two embedding vectors."""
        dot   = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def find_most_similar(
        self,
        query: str,
        candidates: list[str],
        top_k: int = 3,
    ) -> list[tuple[str, float]]:
        """
        Find the most semantically similar texts from a list of candidates.

        Returns: list of (text, similarity_score) sorted by score (highest first).
        """
        q_vec    = self.embed(query, task_type=TASK_RETRIEVAL_QUERY)
        doc_vecs = self.embed_bulk(candidates, task_type=TASK_RETRIEVAL_DOCUMENT)

        scored = [
            (text, self.cosine_similarity(q_vec, vec))
            for text, vec in zip(candidates, doc_vecs)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
