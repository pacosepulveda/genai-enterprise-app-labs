"""Transparent embedding and semantic-search helpers for M05-P02.

The goal is deliberately to keep the core mechanics visible before introducing
vector databases and RAG frameworks in M06.
"""

from __future__ import annotations

import json
import time
from typing import Iterable

import numpy as np

from enterprise_genai.config import get_settings
from enterprise_genai.models.bedrock import bedrock_runtime


DEFAULT_DIMENSIONS = 512


def embed_text(
    text: str,
    *,
    dimensions: int = DEFAULT_DIMENSIONS,
    normalize: bool = True,
    model_id: str | None = None,
) -> dict:
    """Create one Titan Text Embeddings V2 vector and expose useful metadata."""
    if not text.strip():
        raise ValueError("text cannot be empty")
    if dimensions not in {256, 512, 1024}:
        raise ValueError("dimensions must be one of: 256, 512, 1024")

    settings = get_settings()
    selected_model = model_id or settings.bedrock_embedding_model_id
    if not selected_model:
        raise ValueError("BEDROCK_EMBEDDING_MODEL_ID is not configured")

    payload = {
        "inputText": text,
        "dimensions": dimensions,
        "normalize": normalize,
    }

    started = time.perf_counter()
    response = bedrock_runtime().invoke_model(
        modelId=selected_model,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json",
    )
    latency_ms = (time.perf_counter() - started) * 1000

    body = json.loads(response["body"].read().decode("utf-8"))
    vector = np.asarray(body["embedding"], dtype=np.float32)

    return {
        "embedding": vector,
        "input_tokens": body.get("inputTextTokenCount"),
        "dimensions": int(vector.shape[0]),
        "norm": float(np.linalg.norm(vector)),
        "model_id": selected_model,
        "region": settings.aws_region,
        "latency_ms": round(latency_ms),
        "request": payload,
    }


def embed_documents(
    documents: Iterable[dict],
    *,
    text_field: str = "content",
    dimensions: int = DEFAULT_DIMENSIONS,
    normalize: bool = True,
    model_id: str | None = None,
) -> dict:
    """Embed a small corpus sequentially so every model call remains observable."""
    docs = list(documents)
    vectors: list[np.ndarray] = []
    token_counts: list[int | None] = []
    latencies: list[int] = []

    for doc in docs:
        result = embed_text(
            str(doc[text_field]),
            dimensions=dimensions,
            normalize=normalize,
            model_id=model_id,
        )
        vectors.append(result["embedding"])
        token_counts.append(result["input_tokens"])
        latencies.append(result["latency_ms"])

    matrix = np.vstack(vectors) if vectors else np.empty((0, dimensions), dtype=np.float32)
    return {
        "matrix": matrix,
        "token_counts": token_counts,
        "latencies_ms": latencies,
        "request_count": len(docs),
        "dimensions": dimensions,
        "normalized": normalize,
    }


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Cosine similarity in [-1, 1]."""
    a = np.asarray(vector_a, dtype=np.float32)
    b = np.asarray(vector_b, dtype=np.float32)
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def semantic_search(
    query: str,
    documents: list[dict],
    matrix: np.ndarray,
    *,
    top_k: int = 5,
    filters: dict[str, str] | None = None,
    dimensions: int = DEFAULT_DIMENSIONS,
    model_id: str | None = None,
) -> dict:
    """Embed the query, calculate cosine similarity, apply metadata filters and rank."""
    if len(documents) != len(matrix):
        raise ValueError("documents and matrix must have the same number of rows")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    query_result = embed_text(
        query,
        dimensions=dimensions,
        normalize=True,
        model_id=model_id,
    )
    query_vector = query_result["embedding"]

    candidates = []
    for index, doc in enumerate(documents):
        if filters and any(
            expected and expected != "Todos" and str(doc.get(key)) != expected
            for key, expected in filters.items()
        ):
            continue

        score = cosine_similarity(query_vector, matrix[index])
        candidates.append(
            {
                "rank": 0,
                "score": score,
                "document_index": index,
                "document": doc,
            }
        )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    results = candidates[: min(top_k, len(candidates))]
    for rank, item in enumerate(results, start=1):
        item["rank"] = rank

    return {
        "query": query,
        "query_embedding": query_vector,
        "query_tokens": query_result["input_tokens"],
        "query_latency_ms": query_result["latency_ms"],
        "results": results,
        "candidate_count": len(candidates),
        "filters": filters or {},
    }
