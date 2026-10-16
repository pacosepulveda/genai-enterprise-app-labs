import json

import streamlit as st

from enterprise_genai.analysis import analyze_incident


st.set_page_config(page_title="Analyze", page_icon="📄", layout="wide")

st.title("📄 Analyze — Structured Incident Analyzer")
st.caption(
    "M01-P02 · Texto libre → salida estructurada y validada con Amazon Bedrock"
)

DEFAULT_INCIDENT = (
    "Desde las 08:15, 73 usuarios de ACME no pueden autenticarse en la VPN. "
    "El servicio web corporativo funciona correctamente. "
    "El equipo de red informa de errores intermitentes en el backend de autenticación."
)

incident = st.text_area(
    "Incidencia",
    value=DEFAULT_INCIDENT,
    height=150,
    help="Puedes modificar el texto y volver a analizarlo.",
)

analyze = st.button("Analizar incidencia", type="primary", use_container_width=True)

if analyze:
    if not incident.strip():
        st.warning("Introduce una incidencia antes de ejecutar el análisis.")
        st.stop()

    with st.spinner("Analizando con Bedrock..."):
        try:
            result = analyze_incident(incident)
        except Exception as exc:
            st.error(f"No se pudo completar el análisis: {exc}")
            st.stop()

    analysis = result["analysis"]

    st.success("Salida estructurada recibida y validada con Pydantic.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Categoría", analysis.category)
    col2.metric(
        "Usuarios afectados",
        analysis.affected_users if analysis.affected_users is not None else "No consta",
    )
    col3.metric(
        "Revisión humana",
        "Sí" if analysis.human_review_required else "No",
    )

    st.subheader("Resumen")
    st.write(analysis.summary)

    left, right = st.columns(2)

    with left:
        st.subheader("Hechos observados")
        for fact in analysis.observed_facts:
            st.markdown(f"- {fact}")

        st.subheader("Servicio afectado")
        st.write(analysis.affected_service or "No consta")

    with right:
        st.subheader("Hipótesis")
        if analysis.hypotheses:
            for hypothesis in analysis.hypotheses:
                st.markdown(f"- {hypothesis}")
        else:
            st.write("No se han formulado hipótesis.")

        st.subheader("Acciones recomendadas")
        for action in analysis.recommended_actions:
            st.markdown(f"- {action}")

    if analysis.human_review_required:
        st.warning(f"Revisión humana recomendada: {analysis.review_reason}")
    else:
        st.info(f"Revisión humana: {analysis.review_reason}")

    with st.expander("🔎 Abrir la caja: JSON validado"):
        st.json(analysis.model_dump())

    with st.expander("🧩 JSON Schema utilizado"):
        st.json(result["schema"])

    with st.expander("📦 Respuesta JSON cruda de Bedrock"):
        st.code(result["raw_text"], language="json")

    with st.expander("📊 Métricas de inferencia"):
        usage = result["usage"]
        metrics = result["metrics"]
        st.write(
            {
                "model_id": result["model_id"],
                "input_tokens": usage.get("inputTokens"),
                "output_tokens": usage.get("outputTokens"),
                "total_tokens": usage.get("totalTokens"),
                "latency_ms": metrics.get("latencyMs"),
                "stop_reason": result["stop_reason"],
            }
        )

st.divider()
st.caption(
    "La salida estructurada hace que el resultado sea utilizable por código: "
    "interfaces, validadores, reglas, bases de datos y workflows."
)
