import json
from pathlib import Path

import pandas as pd
import streamlit as st

from enterprise_genai.analysis import (
    MultimodalIncidentAnalysis,
    analyze_incident,
    analyze_incident_multimodal,
)
from enterprise_genai.document_analysis import analyze_enterprise_document


st.set_page_config(page_title="Analyze", page_icon="📄", layout="wide")

st.title("📄 Analyze — Structured Enterprise Analysis")
st.caption(
    "Incidencias, evidencia visual y documentos empresariales → salida estructurada y validada con Amazon Bedrock"
)

mode = st.radio(
    "Tipo de análisis",
    ["Incidencia", "Documento empresarial"],
    horizontal=True,
)

if mode == "Incidencia":
    DEFAULT_INCIDENT = (
        "Desde las 08:15, 73 usuarios de ACME no pueden autenticarse en la VPN. "
        "El servicio web corporativo funciona correctamente. "
        "El equipo de operaciones está investigando."
    )

    incident = st.text_area(
        "Incidencia",
        value=DEFAULT_INCIDENT,
        height=150,
        help="Puedes modificar el texto y volver a analizarlo.",
    )

    uploaded = st.file_uploader(
        "Evidencia visual opcional",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        help=(
            "Adjunta una captura de error, dashboard o fotografía. "
            "Sin imagen se mantiene el análisis de texto."
        ),
    )

    image_bytes = None
    image_format = None

    if uploaded is not None:
        image_bytes = uploaded.getvalue()
        mime_to_format = {
            "image/png": "png",
            "image/jpeg": "jpeg",
            "image/gif": "gif",
            "image/webp": "webp",
        }
        image_format = mime_to_format.get(uploaded.type)

        if image_format is None:
            st.error(f"Formato de imagen no compatible: {uploaded.type}")
            st.stop()

        st.image(image_bytes, caption=f"Evidencia visual: {uploaded.name}", width="stretch")

    mode_label = "Texto + imagen" if image_bytes else "Solo texto"
    st.caption(f"Modo de incidencia: **{mode_label}**")

    analyze = st.button("Analizar incidencia", type="primary", use_container_width=True)

    if analyze:
        if not incident.strip():
            st.warning("Introduce una incidencia antes de ejecutar el análisis.")
            st.stop()

        with st.spinner("Analizando con Bedrock..."):
            try:
                if image_bytes:
                    result = analyze_incident_multimodal(
                        incident,
                        image_bytes=image_bytes,
                        image_format=image_format,
                    )
                else:
                    result = analyze_incident(incident)
            except Exception as exc:
                st.error(f"No se pudo completar el análisis: {exc}")
                st.stop()

        analysis = result["analysis"]
        multimodal = isinstance(analysis, MultimodalIncidentAnalysis)

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

        if multimodal:
            st.divider()
            st.subheader("👁️ Evidencia visual")

            v1, v2 = st.columns([2, 1])
            with v1:
                st.markdown("**Resumen visual**")
                st.write(analysis.visual_summary or "No consta")

                st.markdown("**Elementos directamente observados**")
                if analysis.visual_evidence:
                    for evidence in analysis.visual_evidence:
                        st.markdown(f"- {evidence}")
                else:
                    st.write("No se extrajo evidencia visual concluyente.")

            with v2:
                consistency_labels = {
                    "consistent": "Consistente",
                    "partially_consistent": "Parcialmente consistente",
                    "inconsistent": "Inconsistente",
                    "not_enough_information": "Información insuficiente",
                }
                st.metric(
                    "Consistencia texto / imagen",
                    consistency_labels.get(
                        analysis.text_image_consistency,
                        analysis.text_image_consistency,
                    ),
                )

                st.markdown("**Incertidumbres visuales**")
                if analysis.visual_uncertainties:
                    for uncertainty in analysis.visual_uncertainties:
                        st.markdown(f"- {uncertainty}")
                else:
                    st.write("No declaradas.")

            if analysis.text_image_consistency == "inconsistent":
                st.error(
                    "La evidencia visual contradice el texto. "
                    "La discrepancia debe revisarse antes de tomar decisiones."
                )

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
                    "mode": mode_label,
                    "model_id": result["model_id"],
                    "input_tokens": usage.get("inputTokens"),
                    "output_tokens": usage.get("outputTokens"),
                    "total_tokens": usage.get("totalTokens"),
                    "latency_ms": metrics.get("latencyMs"),
                    "stop_reason": result["stop_reason"],
                }
            )

else:
    samples_path = Path("data/documents/m05_document_samples.json")
    samples = json.loads(samples_path.read_text(encoding="utf-8"))
    labels = [item["label"] for item in samples]

    selected_label = st.selectbox("Documento de ejemplo", labels)
    selected = next(item for item in samples if item["label"] == selected_label)

    document_text = st.text_area(
        "Documento",
        value=selected["text"],
        height=300,
        key=f"document_text_{selected['id']}",
        help="Puedes editar el contenido antes de analizarlo.",
    )

    st.caption(
        "M05-P03 · El modelo separa hechos, acciones explícitas, recomendaciones, entidades e incertidumbres."
    )

    analyze_document = st.button(
        "Analizar documento",
        type="primary",
        use_container_width=True,
    )

    if analyze_document:
        if not document_text.strip():
            st.warning("Introduce un documento antes de ejecutar el análisis.")
            st.stop()

        with st.spinner("Analizando documento con Bedrock..."):
            try:
                result = analyze_enterprise_document(document_text)
            except Exception as exc:
                st.error(f"No se pudo completar el análisis: {exc}")
                st.stop()

        analysis = result["analysis"]
        st.success("Salida estructurada recibida y validada con Pydantic.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Tipo", analysis.document_type)
        c2.metric("Categoría", analysis.category)
        c3.metric("Revisión humana", "Sí" if analysis.human_review_required else "No")

        st.subheader(analysis.title)
        st.write(analysis.summary)

        st.subheader("Entidades extraídas")
        if analysis.entities:
            st.dataframe(
                pd.DataFrame([entity.model_dump() for entity in analysis.entities]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.write("No se extrajeron entidades.")

        left, right = st.columns(2)

        with left:
            st.subheader("Hechos clave")
            for item in analysis.key_facts:
                st.markdown(f"- {item}")

            st.subheader("Acciones solicitadas explícitamente")
            if analysis.requested_actions:
                for item in analysis.requested_actions:
                    st.markdown(f"- {item}")
            else:
                st.write("No constan acciones solicitadas.")

            st.subheader("Fechas / plazos")
            if analysis.dates_or_deadlines:
                for item in analysis.dates_or_deadlines:
                    st.markdown(f"- {item}")
            else:
                st.write("No constan.")

        with right:
            st.subheader("Recomendaciones del modelo")
            if analysis.recommended_actions:
                for item in analysis.recommended_actions:
                    st.markdown(f"- {item}")
            else:
                st.write("No se proponen acciones.")

            st.subheader("Incertidumbres")
            if analysis.uncertainties:
                for item in analysis.uncertainties:
                    st.markdown(f"- {item}")
            else:
                st.write("No declaradas.")

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
    "Analyze mantiene separados hechos observados, información extraída y contenido recomendado por el modelo."
)
