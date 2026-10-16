import time

import pandas as pd
import streamlit as st

from enterprise_genai.classical_ml import (
    LABEL_DISPLAY,
    build_ticket_classifier,
    load_ticket_dataset,
    predict_with_probabilities,
)
from enterprise_genai.llm_classifier import classify_ticket_with_llm


st.set_page_config(
    page_title="Classical ML vs LLM",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Classical ML vs LLM")
st.caption("M02-P02 · TF-IDF + Logistic Regression frente a Amazon Bedrock")

DATASET_PATH = "data/tickets/m02_tickets.csv"


@st.cache_resource
def train_ml_model():
    df = load_ticket_dataset(DATASET_PATH)
    model = build_ticket_classifier()
    model.fit(df["text"], df["category"])
    return df, model


df, ml_model = train_ml_model()

examples = {
    "MFA no llega": "No puedo acceder al CRM porque el código MFA no llega al móvil.",
    "MFA no solicitado": "El usuario recibió una solicitud de MFA que no inició.",
    "VPN + Wi-Fi + USB": (
        "Después de conectar la VPN el portátil pierde el Wi-Fi "
        "y el adaptador USB deja de responder."
    ),
    "Reserva de sala (fuera de alcance)": (
        "Necesito reservar una sala grande para una reunión con clientes el próximo martes."
    ),
}

selected = st.selectbox("Ejemplo", list(examples), index=0)
ticket = st.text_area("Ticket", value=examples[selected], height=120)

st.info(
    "El modelo clásico fue reentrenado con los 80 tickets etiquetados. "
    "El LLM no se entrena aquí: recibe la taxonomía y clasifica mediante Bedrock."
)

if st.button("Comparar ambos enfoques", type="primary", use_container_width=True):
    if not ticket.strip():
        st.warning("Introduce un ticket.")
        st.stop()

    started = time.perf_counter()
    ml_probs = predict_with_probabilities(ml_model, ticket)
    ml_ms = (time.perf_counter() - started) * 1000
    ml_best = ml_probs.iloc[0]
    ml_second = ml_probs.iloc[1]

    with st.spinner("Consultando Bedrock..."):
        llm = classify_ticket_with_llm(ticket)
    cls = llm["classification"]

    st.subheader("Resultado comparativo")

    left, right = st.columns(2)

    with left:
        st.markdown("### 🧮 ML clásico")
        st.metric("Categoría", LABEL_DISPLAY[str(ml_best["category"])])
        c1, c2 = st.columns(2)
        c1.metric("Probabilidad máxima", f"{float(ml_best['probability']):.1%}")
        c2.metric(
            "Margen frente a segunda",
            f"{float(ml_best['probability'] - ml_second['probability']):.1%}",
        )

        if float(ml_best["probability"]) < 0.55:
            st.warning("Confianza baja según la regla didáctica del 55 %.")
        else:
            st.success("Preferencia clara según la regla didáctica del 55 %.")

        chart_df = ml_probs.set_index("label")[["probability"]]
        st.bar_chart(chart_df)

        st.caption(f"Inferencia local: {ml_ms:.3f} ms · API externas: 0")

    with right:
        st.markdown("### 🤖 LLM Bedrock")
        st.metric("Categoría forzada", LABEL_DISPLAY[cls.category])

        c1, c2 = st.columns(2)
        c1.metric("Dentro del dominio", "Sí" if cls.in_scope else "No")
        c2.metric("Revisión", "Sí" if cls.needs_review else "No")

        if not cls.in_scope:
            st.warning(
                "El LLM considera que el ticket no pertenece realmente a la taxonomía."
            )
        elif cls.needs_review:
            st.warning("El LLM marca el caso para revisión.")
        else:
            st.success("El LLM considera el caso dentro de alcance y sin revisión necesaria.")

        st.markdown("**Explicación breve**")
        st.write(cls.explanation)

        st.caption(
            f"Cliente: {llm['client_ms']} ms · "
            f"Bedrock: {llm['metrics'].get('latencyMs', 'n/d')} ms · "
            f"Tokens: {llm['usage'].get('totalTokens', 'n/d')}"
        )

    st.divider()
    st.subheader("Abrir la caja")

    with st.expander("🧮 Probabilidades completas del modelo clásico"):
        st.dataframe(
            ml_probs[["label", "category", "probability"]].style.format(
                {"probability": "{:.1%}"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("🤖 JSON validado del LLM"):
        st.json(cls.model_dump())

    with st.expander("📊 Recursos y latencia"):
        st.write(
            {
                "ml": {
                    "training_tickets": len(df),
                    "client_ms": round(ml_ms, 3),
                    "external_api_calls": 0,
                    "tokens": 0,
                },
                "llm": {
                    "model_id": llm["model_id"],
                    "client_ms": llm["client_ms"],
                    "bedrock_latency_ms": llm["metrics"].get("latencyMs"),
                    "usage": llm["usage"],
                    "stop_reason": llm["stop_reason"],
                    "external_api_calls": 1,
                },
            }
        )

st.divider()
st.caption(
    "No comparamos la probabilidad de Logistic Regression con una supuesta confianza numérica "
    "del LLM: no son magnitudes equivalentes."
)
