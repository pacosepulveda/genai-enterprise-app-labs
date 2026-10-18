import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from enterprise_genai.config import get_settings
from enterprise_genai.embeddings import DEFAULT_DIMENSIONS, embed_documents, semantic_search


st.set_page_config(page_title="Knowledge", page_icon="💬", layout="wide")

st.title("💬 Knowledge — Semantic Retrieval Explorer")
st.caption(
    "M05-P02 · Consulta → embedding → similitud coseno → ranking de fragmentos empresariales"
)

st.info(
    "En esta etapa Knowledge recupera fragmentos relevantes, pero todavía no genera una respuesta con un LLM. "
    "El RAG completo llegará en M06."
)

CORPUS_PATH = Path("data/knowledge/m05_enterprise_chunks.json")
settings = get_settings()


def load_corpus() -> list[dict]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


@st.cache_resource(show_spinner=False)
def build_cached_index() -> tuple[list[dict], dict]:
    documents = load_corpus()
    index = embed_documents(
        documents,
        dimensions=DEFAULT_DIMENSIONS,
        normalize=True,
    )
    return documents, index


documents_preview = load_corpus()
services = ["Todos"] + sorted({doc["service"] for doc in documents_preview})
source_types = ["Todos"] + sorted({doc["source_type"] for doc in documents_preview})

query = st.text_input(
    "Consulta",
    value="No me llega el código de seguridad al móvil cuando intento conectarme desde casa",
    help="Prueba una pregunta natural. No necesitas copiar las mismas palabras que aparecen en los documentos.",
)

c1, c2, c3 = st.columns(3)
with c1:
    top_k = st.slider("Top-k", min_value=1, max_value=8, value=4)
with c2:
    service_filter = st.selectbox("Servicio", services)
with c3:
    source_filter = st.selectbox("Tipo de fuente", source_types)

st.caption(
    f"Corpus: **{len(documents_preview)} fragmentos** · Modelo: "
    f"`{settings.bedrock_embedding_model_id}` · Dimensiones: **{DEFAULT_DIMENSIONS}**"
)

search = st.button("Buscar semánticamente", type="primary", use_container_width=True)

if search:
    if not query.strip():
        st.warning("Introduce una consulta antes de buscar.")
        st.stop()

    with st.spinner("Preparando índice y generando embedding de la consulta..."):
        try:
            documents, index = build_cached_index()
            result = semantic_search(
                query,
                documents,
                index["matrix"],
                top_k=top_k,
                filters={
                    "service": service_filter,
                    "source_type": source_filter,
                },
                dimensions=DEFAULT_DIMENSIONS,
            )
        except Exception as exc:
            st.error(f"No se pudo completar la búsqueda semántica: {exc}")
            st.stop()

    st.success(
        f"Recuperados {len(result['results'])} fragmentos de "
        f"{result['candidate_count']} candidatos tras aplicar filtros."
    )

    if not result["results"]:
        st.warning("No hay documentos que cumplan los filtros seleccionados.")
    else:
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

        st.subheader("Ranking")
        ranking_df = pd.DataFrame(score_rows)
        st.dataframe(ranking_df, use_container_width=True, hide_index=True)

        chart_df = ranking_df.set_index("id")[["score"]]
        st.bar_chart(chart_df)

        st.subheader("Fragmentos recuperados")
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
                "index_embedding_latency_ms_total": int(sum(index["latencies_ms"])),
                "filters": result["filters"],
            }
        )
        st.markdown("**Primeras 12 coordenadas del embedding de consulta**")
        st.code(np.array2string(query_vector[:12], precision=5), language=None)

st.divider()
st.caption(
    "El score expresa similitud vectorial, no una verdad absoluta ni una probabilidad. "
    "En M06 usaremos retrieval como una etapa del pipeline RAG y evaluaremos su calidad."
)
