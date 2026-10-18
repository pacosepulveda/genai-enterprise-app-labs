import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from enterprise_genai.config import get_settings
from enterprise_genai.embeddings import DEFAULT_DIMENSIONS, embed_documents, semantic_search
from enterprise_genai.rag import (
    answer_with_context,
    build_rag_index,
    chunk_documents,
    retrieve_chunks,
)


st.set_page_config(page_title="Knowledge", page_icon="💬", layout="wide")

st.title("💬 Knowledge")
st.caption("M05 retrieval semántico → M06 RAG desde cero, con el pipeline visible")

CORPUS_PATH = Path("data/knowledge/m05_enterprise_chunks.json")
settings = get_settings()


def load_corpus() -> list[dict]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


@st.cache_resource(show_spinner=False)
def build_cached_semantic_index() -> tuple[list[dict], dict]:
    documents = load_corpus()
    index = embed_documents(
        documents,
        dimensions=DEFAULT_DIMENSIONS,
        normalize=True,
    )
    return documents, index


@st.cache_resource(show_spinner=False)
def build_cached_rag_index() -> tuple[list[dict], list[dict], dict]:
    documents = load_corpus()
    chunks = chunk_documents(documents, chunk_size_words=36, overlap_words=8)
    index = build_rag_index(
        chunks,
        dimensions=DEFAULT_DIMENSIONS,
        normalize=True,
        max_workers=8,
    )
    return documents, chunks, index


documents_preview = load_corpus()
services = ["Todos"] + sorted({doc["service"] for doc in documents_preview})
source_types = ["Todos"] + sorted({doc["source_type"] for doc in documents_preview})

mode = st.radio(
    "Modo",
    ["Búsqueda semántica (M05)", "RAG desde cero (M06)"],
    horizontal=True,
)

if mode.startswith("Búsqueda"):
    st.info(
        "Recuperamos documentos por similitud semántica. No se genera todavía una respuesta con un LLM."
    )
else:
    st.info(
        "RAG = retrieval + contexto + generación. La respuesta se construye únicamente con los chunks recuperados y muestra sus fuentes."
    )

query = st.text_input(
    "Consulta",
    value="¿Qué debo comprobar si no recibo el segundo factor al conectarme por VPN?",
    help="La consulta se convierte en embedding antes de compararla con el índice.",
)

c1, c2, c3 = st.columns(3)
with c1:
    top_k = st.slider("Top-k", min_value=1, max_value=8, value=4)
with c2:
    service_filter = st.selectbox("Servicio", services)
with c3:
    source_filter = st.selectbox("Tipo de fuente", source_types)

filters = {"service": service_filter, "source_type": source_filter}

if mode.startswith("Búsqueda"):
    st.caption(
        f"Corpus: **{len(documents_preview)} documentos** · Modelo: "
        f"`{settings.bedrock_embedding_model_id}` · Dimensiones: **{DEFAULT_DIMENSIONS}**"
    )
    button_label = "Buscar semánticamente"
else:
    preview_chunks = chunk_documents(documents_preview, chunk_size_words=36, overlap_words=8)
    st.caption(
        f"Corpus: **{len(documents_preview)} documentos → {len(preview_chunks)} chunks** · "
        f"Embeddings: `{settings.bedrock_embedding_model_id}` · LLM: `{settings.bedrock_text_model_id}`"
    )
    button_label = "Preguntar con RAG"

run = st.button(button_label, type="primary", use_container_width=True)

if run:
    if not query.strip():
        st.warning("Introduce una consulta antes de continuar.")
        st.stop()

    if mode.startswith("Búsqueda"):
        with st.spinner("Preparando índice y generando embedding de la consulta..."):
            try:
                documents, index = build_cached_semantic_index()
                result = semantic_search(
                    query,
                    documents,
                    index["matrix"],
                    top_k=top_k,
                    filters=filters,
                    dimensions=DEFAULT_DIMENSIONS,
                )
            except Exception as exc:
                st.error(f"No se pudo completar la búsqueda semántica: {exc}")
                st.stop()

        st.success(
            f"Recuperados {len(result['results'])} documentos de "
            f"{result['candidate_count']} candidatos tras aplicar filtros."
        )

        score_rows = []
        for item in result["results"]:
            doc = item["document"]
            score_rows.append(
                {
                    "rank": item["rank"],
                    "id": doc["id"],
                    "score": round(item["score"], 4),
                    "service": doc["service"],
                    "source_type": doc["source_type"],
                    "title": doc["title"],
                }
            )

        if score_rows:
            st.subheader("Ranking")
            ranking_df = pd.DataFrame(score_rows)
            st.dataframe(ranking_df, use_container_width=True, hide_index=True)
            st.bar_chart(ranking_df.set_index("id")[["score"]])

            st.subheader("Documentos recuperados")
            for item in result["results"]:
                doc = item["document"]
                with st.expander(
                    f"#{item['rank']} · {doc['title']} · score {item['score']:.4f}",
                    expanded=item["rank"] == 1,
                ):
                    m1, m2, m3 = st.columns(3)
                    m1.markdown(f"**Servicio:** `{doc['service']}`")
                    m2.markdown(f"**Fuente:** `{doc['source_type']}`")
                    m3.markdown(f"**Audiencia:** `{doc['audience']}`")
                    st.write(doc["content"])
                    st.caption(f"ID: {doc['id']}")

        with st.expander("🔎 Abrir la caja: embedding y retrieval"):
            query_vector = result["query_embedding"]
            st.write(
                {
                    "embedding_model": settings.bedrock_embedding_model_id,
                    "dimensions": len(query_vector),
                    "query_vector_norm": round(float(np.linalg.norm(query_vector)), 6),
                    "query_input_tokens": result["query_tokens"],
                    "query_embedding_latency_ms": result["query_latency_ms"],
                    "index_shape": list(index["matrix"].shape),
                    "documents_embedded": index["request_count"],
                    "filters": result["filters"],
                }
            )
            st.markdown("**Primeras 12 coordenadas del embedding de consulta**")
            st.code(np.array2string(query_vector[:12], precision=5), language=None)

    else:
        with st.spinner("Chunking → embeddings → retrieval → contexto → LLM..."):
            try:
                documents, chunks, index = build_cached_rag_index()
                retrieval = retrieve_chunks(
                    query,
                    chunks,
                    index["matrix"],
                    top_k=top_k,
                    filters=filters,
                    dimensions=DEFAULT_DIMENSIONS,
                )
                if not retrieval["results"]:
                    st.warning("No hay chunks que cumplan los filtros seleccionados.")
                    st.stop()
                generated = answer_with_context(query, retrieval["results"])
            except Exception as exc:
                st.error(f"No se pudo completar el RAG: {exc}")
                st.stop()

        st.success(
            f"RAG completado con {len(retrieval['results'])} chunks recuperados de "
            f"{retrieval['candidate_count']} candidatos."
        )

        st.subheader("Respuesta fundamentada")
        st.markdown(generated["answer"])

        score_rows = []
        for item in retrieval["results"]:
            chunk = item["document"]
            score_rows.append(
                {
                    "rank": item["rank"],
                    "score": round(item["score"], 4),
                    "chunk_id": chunk["id"],
                    "document_id": chunk["document_id"],
                    "service": chunk["service"],
                    "title": chunk["title"],
                }
            )

        st.subheader("Chunks recuperados")
        st.dataframe(pd.DataFrame(score_rows), use_container_width=True, hide_index=True)
        for i, item in enumerate(retrieval["results"], start=1):
            chunk = item["document"]
            with st.expander(
                f"[S{i}] {chunk['title']} · {chunk['id']} · score {item['score']:.4f}",
                expanded=i == 1,
            ):
                st.write(chunk["content"])
                st.caption(
                    f"Documento: {chunk['document_id']} · Servicio: {chunk['service']} · "
                    f"Fuente: {chunk['source_type']}"
                )

        with st.expander("🔎 Abrir la caja: pipeline RAG"):
            usage = generated["usage"]
            metrics = generated["metrics"]
            st.write(
                {
                    "source_documents": len(documents),
                    "chunks": len(chunks),
                    "chunk_size_words": 36,
                    "overlap_words": 8,
                    "index_shape": list(index["matrix"].shape),
                    "query_input_tokens_embedding": retrieval["query_tokens"],
                    "query_embedding_latency_ms": retrieval["query_latency_ms"],
                    "llm_input_tokens": usage.get("inputTokens"),
                    "llm_output_tokens": usage.get("outputTokens"),
                    "llm_total_tokens": usage.get("totalTokens"),
                    "llm_latency_ms": metrics.get("latencyMs"),
                    "stop_reason": generated["stop_reason"],
                    "filters": retrieval["filters"],
                }
            )
            st.markdown("**Contexto exacto enviado al LLM**")
            st.code(generated["context"], language=None)
            st.markdown("**System prompt**")
            st.code(generated["system_prompt"], language=None)
            st.markdown("**User prompt completo**")
            st.code(generated["user_prompt"], language=None)

st.divider()
st.caption(
    "M05 hizo visible el retrieval. M06-P01 añade contexto y generación sin ocultar el pipeline. "
    "M06-P02 reconstruirá este patrón con LangChain y lo evaluará."
)
