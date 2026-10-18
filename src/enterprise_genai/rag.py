"""Transparent RAG helpers for M06-P01.

This module intentionally keeps chunking, retrieval, context construction and
LLM generation visible before introducing LangChain in M06-P02.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np

from enterprise_genai.config import get_settings
from enterprise_genai.embeddings import DEFAULT_DIMENSIONS, embed_documents, semantic_search
from enterprise_genai.models.bedrock import bedrock_runtime


def chunk_documents(
    documents: Iterable[dict],
    *,
    chunk_size_words: int = 36,
    overlap_words: int = 8,
) -> list[dict]:
    """Split documents into overlapping word chunks while preserving metadata."""
    if chunk_size_words < 8:
        raise ValueError("chunk_size_words must be >= 8")
    if overlap_words < 0 or overlap_words >= chunk_size_words:
        raise ValueError("overlap_words must be >= 0 and < chunk_size_words")

    chunks: list[dict] = []
    step = chunk_size_words - overlap_words

    for doc in documents:
        words = str(doc["content"]).split()
        if not words:
            continue

        starts = list(range(0, len(words), step))
        for chunk_no, start in enumerate(starts, start=1):
            end = min(start + chunk_size_words, len(words))
            text = " ".join(words[start:end])
            if not text:
                continue

            chunks.append(
                {
                    "id": f"{doc['id']}::c{chunk_no}",
                    "document_id": doc["id"],
                    "title": doc["title"],
                    "service": doc["service"],
                    "source_type": doc["source_type"],
                    "audience": doc["audience"],
                    "content": text,
                    "chunk_no": chunk_no,
                    "start_word": start,
                    "end_word": end,
                }
            )

            if end >= len(words):
                break

    return chunks


def build_rag_index(
    chunks: list[dict],
    *,
    dimensions: int = DEFAULT_DIMENSIONS,
    normalize: bool = True,
    max_workers: int = 8,
) -> dict:
    """Embed chunks and return the matrix plus observable metadata."""
    index = embed_documents(
        chunks,
        dimensions=dimensions,
        normalize=normalize,
        max_workers=max_workers,
    )
    return {"chunks": chunks, **index}


def retrieve_chunks(
    query: str,
    chunks: list[dict],
    matrix: np.ndarray,
    *,
    top_k: int = 4,
    filters: dict[str, str] | None = None,
    dimensions: int = DEFAULT_DIMENSIONS,
) -> dict:
    """Retrieve semantically similar chunks using the helpers from M05-P02."""
    return semantic_search(
        query,
        chunks,
        matrix,
        top_k=top_k,
        filters=filters,
        dimensions=dimensions,
    )


def build_context(results: list[dict]) -> str:
    """Turn retrieved chunks into an explicit, inspectable context block."""
    blocks: list[str] = []
    for i, item in enumerate(results, start=1):
        doc = item["document"]
        blocks.append(
            "\n".join(
                [
                    f"[S{i}] document_id={doc['document_id']}",
                    f"title={doc['title']}",
                    f"service={doc['service']}",
                    f"source_type={doc['source_type']}",
                    f"chunk_id={doc['id']}",
                    f"content={doc['content']}",
                ]
            )
        )
    return "\n\n".join(blocks)


def answer_with_context(
    query: str,
    retrieved_results: list[dict],
    *,
    max_tokens: int = 700,
) -> dict:
    """Generate one grounded answer using only explicitly retrieved context."""
    if not retrieved_results:
        raise ValueError("retrieved_results cannot be empty")

    settings = get_settings()
    model_id = settings.bedrock_text_model_id
    if not model_id:
        raise ValueError("BEDROCK_TEXT_MODEL_ID is not configured")

    context = build_context(retrieved_results)
    system_prompt = (
        "Responde preguntas sobre documentación empresarial usando exclusivamente el CONTEXTO "
        "recuperado. No uses conocimiento externo ni inventes procedimientos, fechas, causas, "
        "ejemplos o detalles plausibles que no aparezcan explícitamente en las fuentes. "
        "No amplíes términos genéricos con ejemplos propios. "
        "Cita las fuentes con [S1], [S2], etc. junto a cada afirmación relevante. "
        "Si el contexto no permite responder con suficiente seguridad, dilo explícitamente."
    )
    user_prompt = f"PREGUNTA:\n{query}\n\nCONTEXTO RECUPERADO:\n{context}"

    request = {
        "modelId": model_id,
        "system": [{"text": system_prompt}],
        "messages": [{"role": "user", "content": [{"text": user_prompt}]}],
        "inferenceConfig": {"temperature": 0.0, "maxTokens": max_tokens},
    }

    response = bedrock_runtime().converse(**request)
    answer = response["output"]["message"]["content"][0]["text"]

    return {
        "answer": answer,
        "context": context,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "usage": response.get("usage", {}),
        "metrics": response.get("metrics", {}),
        "stop_reason": response.get("stopReason"),
        "model_id": model_id,
    }
