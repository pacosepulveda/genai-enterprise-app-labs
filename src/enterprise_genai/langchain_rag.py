"""LangChain-based RAG helpers for M06-P02.

The goal is to rebuild the transparent M06-P01 pipeline with LangChain abstractions
and add measurable retrieval evaluation without hiding what is happening.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from langchain_aws import ChatBedrockConverse
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from enterprise_genai.config import get_settings
from enterprise_genai.embeddings import DEFAULT_DIMENSIONS, embed_documents, embed_text


class CourseBedrockEmbeddings(Embeddings):
    """LangChain Embeddings adapter backed by the course's Titan helper.

    Reusing our helper keeps the Bedrock calls observable and performs document
    embedding concurrently, which is useful for the teaching corpus.
    """

    def __init__(self, *, dimensions: int = DEFAULT_DIMENSIONS, max_workers: int = 8):
        self.dimensions = dimensions
        self.max_workers = max_workers

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        docs = [{"content": text} for text in texts]
        result = embed_documents(
            docs,
            dimensions=self.dimensions,
            normalize=True,
            max_workers=self.max_workers,
        )
        return result["matrix"].tolist()

    def embed_query(self, text: str) -> list[float]:
        result = embed_text(text, dimensions=self.dimensions, normalize=True)
        return result["embedding"].tolist()


def to_langchain_documents(records: Iterable[dict]) -> list[Document]:
    """Convert the 80 enterprise records into LangChain Documents."""
    documents: list[Document] = []
    for record in records:
        documents.append(
            Document(
                page_content=str(record["content"]),
                metadata={
                    "document_id": record["id"],
                    "title": record["title"],
                    "service": record["service"],
                    "source_type": record["source_type"],
                    "audience": record["audience"],
                },
            )
        )
    return documents


def split_documents(
    documents: list[Document],
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Document]:
    """Split documents with LangChain's RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "; ", ", ", " "],
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks, start=1):
        chunk.metadata = {**chunk.metadata, "chunk_index": index}
    return chunks


def build_chroma(
    chunks: list[Document],
    *,
    collection_name: str,
    embeddings: Embeddings | None = None,
) -> Chroma:
    """Create an in-memory Chroma collection using cosine distance."""
    embedding_function = embeddings or CourseBedrockEmbeddings()
    return Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        collection_name=collection_name,
        collection_metadata={"hnsw:space": "cosine"},
    )


def retrieve_with_scores(
    store: Chroma,
    query: str,
    *,
    k: int = 4,
    metadata_filter: dict | None = None,
) -> list[dict]:
    """Return retrieved Documents with relevance scores in descending order."""
    pairs = store.similarity_search_with_relevance_scores(
        query,
        k=k,
        filter=metadata_filter,
    )
    results = []
    for rank, (document, score) in enumerate(pairs, start=1):
        results.append(
            {
                "rank": rank,
                "score": float(score),
                "document": document,
            }
        )
    return results


def _contains_expected_document(results: list[dict], expected_document_id: str) -> int | None:
    for item in results:
        if item["document"].metadata.get("document_id") == expected_document_id:
            return int(item["rank"])
    return None


def evaluate_retrieval(
    store: Chroma,
    cases: list[dict],
    *,
    k: int,
    use_service_filter: bool = False,
) -> dict:
    """Measure Hit Rate@k and MRR@k over a small labelled benchmark."""
    rows = []
    reciprocal_ranks: list[float] = []
    hits = 0

    for case in cases:
        metadata_filter = {"service": case["service"]} if use_service_filter else None
        results = retrieve_with_scores(
            store,
            case["query"],
            k=k,
            metadata_filter=metadata_filter,
        )
        rank = _contains_expected_document(results, case["expected_document_id"])
        hit = rank is not None
        rr = 1.0 / rank if rank else 0.0
        hits += int(hit)
        reciprocal_ranks.append(rr)
        rows.append(
            {
                "id": case["id"],
                "query": case["query"],
                "expected_document_id": case["expected_document_id"],
                "service": case["service"],
                "hit": hit,
                "rank": rank,
                "reciprocal_rank": rr,
                "top_document_id": (
                    results[0]["document"].metadata.get("document_id") if results else None
                ),
            }
        )

    total = len(cases)
    return {
        "k": k,
        "use_service_filter": use_service_filter,
        "cases": total,
        "hits": hits,
        "hit_rate": hits / total if total else 0.0,
        "mrr": sum(reciprocal_ranks) / total if total else 0.0,
        "rows": rows,
    }


def format_context(results: list[dict]) -> str:
    """Format LangChain retrieval results as explicit source blocks."""
    blocks = []
    for index, item in enumerate(results, start=1):
        doc = item["document"]
        meta = doc.metadata
        blocks.append(
            "\n".join(
                [
                    f"[S{index}] document_id={meta.get('document_id')}",
                    f"title={meta.get('title')}",
                    f"service={meta.get('service')}",
                    f"source_type={meta.get('source_type')}",
                    f"content={doc.page_content}",
                ]
            )
        )
    return "\n\n".join(blocks)


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Responde usando exclusivamente el CONTEXTO recuperado. "
            "No añadas ejemplos, causas, pasos ni detalles que no aparezcan explícitamente "
            "en las fuentes. Cita [S1], [S2], etc. junto a cada afirmación relevante. "
            "Si el contexto no basta, indícalo claramente.",
        ),
        (
            "human",
            "PREGUNTA:\n{question}\n\nCONTEXTO RECUPERADO:\n{context}",
        ),
    ]
)


def build_generation_chain():
    """Build the LCEL prompt → Bedrock → string parser chain."""
    settings = get_settings()
    llm = ChatBedrockConverse(
        model_id=settings.bedrock_text_model_id,
        region_name=settings.aws_region,
        temperature=0.0,
        max_tokens=700,
    )
    return RAG_PROMPT | llm | StrOutputParser()


def answer_with_langchain(query: str, results: list[dict]) -> dict:
    """Generate one grounded answer through an explicit LCEL chain."""
    if not results:
        raise ValueError("results cannot be empty")
    context = format_context(results)
    chain = build_generation_chain()
    answer = chain.invoke({"question": query, "context": context})
    return {
        "answer": answer,
        "context": context,
        "prompt": RAG_PROMPT,
    }
