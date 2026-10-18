import pandas as pd
import streamlit as st

from enterprise_genai.final_validation import (
    CAPSTONE_KNOWLEDGE_QUERY,
    CAPSTONE_REPORT,
    resume_capstone_case,
    run_capstone_case,
    run_control_checks,
    run_rag_prompt_injection_probe,
)


st.set_page_config(page_title="Command Center", page_icon="🧭", layout="wide")

st.title("🧭 Enterprise GenAI Command Center")
st.caption("M06-P05 · Cierre del curso: caso 360º, trazabilidad y controles básicos")

st.success(
    "El prototipo final combina las capacidades construidas durante el curso. "
    "El objetivo no es ocultar la complejidad, sino mostrar qué aporta cada pieza y dónde están los controles."
)

view = st.radio(
    "Vista",
    ["🚀 Caso 360º", "🛡️ Assurance", "🧭 Arquitectura final"],
    horizontal=True,
)


if view.startswith("🚀"):
    st.subheader("Caso 360º · Asteria Retail / Managed VPN")
    st.info(
        "Una sola situación empresarial se observa desde tres capacidades distintas: "
        "Analyze interpreta el reporte, Knowledge recupera guía corporativa e Investigate "
        "contrasta datos empresariales y aplica un workflow con aprobación humana."
    )

    report = st.text_area(
        "Reporte recibido",
        value=CAPSTONE_REPORT,
        height=120,
        key="p05_report",
    )
    knowledge_query = st.text_input(
        "Pregunta a Knowledge",
        value=CAPSTONE_KNOWLEDGE_QUERY,
        key="p05_knowledge_query",
    )

    if st.button(
        "🚀 Ejecutar caso 360º",
        type="primary",
        use_container_width=True,
        key="p05_run_case",
    ):
        st.session_state.pop("p05_case", None)
        with st.spinner(
            "Analyze → Knowledge/RAG → datos empresariales → LangGraph → puerta de aprobación..."
        ):
            try:
                case = run_capstone_case(report, knowledge_query=knowledge_query)
            except Exception as exc:
                st.error(f"No se pudo completar el caso 360º: {exc}")
                st.stop()
        st.session_state["p05_case"] = case

    case = st.session_state.get("p05_case")
    if case:
        analysis = case["analysis"]["data"]
        knowledge = case["knowledge"]
        workflow = case["workflow"]

        route = ["Reporte recibido ✅", "Analyze ✅", "Knowledge/RAG ✅", "Investigate ✅"]
        route.append("Aprobación humana ⏸️" if workflow.get("_interrupted") else "Workflow finalizado ✅")
        st.markdown("### Ruta del caso")
        st.code("  →  ".join(route), language=None)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Categoría Analyze", analysis.get("category", "—"))
        m2.metric("Servicio", analysis.get("affected_service") or "—")
        m3.metric("Fuentes RAG", len(knowledge.get("sources", [])))
        m4.metric(
            "Workflow",
            "PAUSADO" if workflow.get("_interrupted") else workflow.get("workflow_status", "—"),
        )
        m5.metric("Tokens LLM", case.get("usage", {}).get("totalTokens", "—"))

        capability_tabs = st.tabs(
            ["📄 Analyze", "💬 Knowledge", "🔧 Investigate", "🔎 Trazabilidad 360º"]
        )

        with capability_tabs[0]:
            st.markdown("### Qué dice el reporte")
            a1, a2, a3 = st.columns(3)
            a1.metric("Categoría", analysis.get("category", "—"))
            a2.metric("Usuarios afectados", analysis.get("affected_users") or "No consta")
            a3.metric(
                "Revisión humana",
                "Sí" if analysis.get("human_review_required") else "No",
            )
            st.markdown(f"**Resumen:** {analysis.get('summary', '—')}")

            left, right = st.columns(2)
            with left:
                st.markdown("**Hechos observados**")
                for item in analysis.get("observed_facts", []):
                    st.markdown(f"- {item}")
                st.markdown("**Hipótesis**")
                for item in analysis.get("hypotheses", []):
                    st.markdown(f"- {item}")
            with right:
                st.markdown("**Acciones recomendadas**")
                for item in analysis.get("recommended_actions", []):
                    st.markdown(f"- {item}")
                st.markdown("**Motivo de revisión**")
                st.write(analysis.get("review_reason", "—"))

            with st.expander("🔎 Abrir la caja: salida estructurada y métricas"):
                st.json(analysis)
                st.write(
                    {
                        "model_id": case["analysis"].get("model_id"),
                        "usage": case["analysis"].get("usage", {}),
                        "metrics": case["analysis"].get("metrics", {}),
                        "stop_reason": case["analysis"].get("stop_reason"),
                    }
                )

        with capability_tabs[1]:
            st.markdown("### Qué dice el conocimiento corporativo")
            st.markdown(knowledge["answer"])

            source_rows = [
                {
                    "source": item["source"],
                    "rank": item["rank"],
                    "score": item["score"],
                    "document_id": item["document_id"],
                    "title": item["title"],
                }
                for item in knowledge["sources"]
            ]
            st.dataframe(pd.DataFrame(source_rows), use_container_width=True, hide_index=True)

            for item in knowledge["sources"]:
                with st.expander(
                    f"[{item['source']}] {item['title']} · score {item['score']:.4f}",
                    expanded=item["source"] == "S1",
                ):
                    st.write(item["content"])
                    st.caption(
                        f"{item['document_id']} · {item['service']} · {item['source_type']}"
                    )

            with st.expander("🔎 Abrir la caja: retrieval, contexto y tokens"):
                st.write(knowledge["retrieval"])
                st.write({"usage": knowledge["usage"], "metrics": knowledge["metrics"]})
                st.markdown("**Contexto exacto enviado al LLM**")
                st.code(knowledge["context"], language=None)

        with capability_tabs[2]:
            st.markdown("### Qué dicen los sistemas empresariales y el workflow")
            enterprise_data = workflow.get("enterprise_data", {})
            incidents = enterprise_data.get("open_incidents", {}).get("incidents", [])
            incident = incidents[0] if incidents else {}
            service_status = enterprise_data.get("service_status", {})
            contract = enterprise_data.get("contract_sla", {})

            i1, i2, i3, i4 = st.columns(4)
            i1.metric("Incidente", incident.get("incident_id", "—"))
            i2.metric("Prioridad", incident.get("severity", "—"))
            i3.metric("Estado", str(service_status.get("status", "—")).upper())
            i4.metric(
                "SLA P1",
                f"{contract.get('response_minutes_p1')} min"
                if contract.get("response_minutes_p1")
                else "—",
            )

            assessment = workflow.get("assessment", {})
            st.markdown(f"**Resumen de workflow:** {assessment.get('executive_summary', '—')}")

            if assessment.get("recommended_actions"):
                st.markdown("**Acciones recomendadas**")
                for item in assessment["recommended_actions"]:
                    st.markdown(f"- {item}")

            if assessment.get("uncertainties"):
                st.markdown("**Incertidumbres**")
                for item in assessment["uncertainties"]:
                    st.markdown(f"- {item}")

            draft = assessment.get("customer_update_draft", "")

            if workflow.get("_interrupted"):
                st.warning("⏸️ Workflow detenido: aprobación humana requerida")
                st.write(workflow.get("approval_reason"))
                st.caption(
                    "El caso ya ha combinado Analyze, Knowledge y datos empresariales. "
                    "LangGraph conserva el estado hasta que una persona decida."
                )

                edited_draft = st.text_area(
                    "Borrador al cliente — revisar o editar",
                    value=draft,
                    height=190,
                    key=f"p05_draft_{workflow['_thread_id']}",
                )
                reviewer_comment = st.text_input(
                    "Comentario del revisor",
                    key=f"p05_comment_{workflow['_thread_id']}",
                )

                approve_col, reject_col = st.columns(2)
                with approve_col:
                    approve = st.button(
                        "✅ Aprobar y reanudar",
                        type="primary",
                        use_container_width=True,
                        key=f"p05_approve_{workflow['_thread_id']}",
                    )
                with reject_col:
                    reject = st.button(
                        "⛔ Rechazar y reanudar",
                        use_container_width=True,
                        key=f"p05_reject_{workflow['_thread_id']}",
                    )

                if approve or reject:
                    with st.spinner("Reanudando exactamente el mismo workflow..."):
                        try:
                            completed = resume_capstone_case(
                                thread_id=workflow["_thread_id"],
                                approved=bool(approve),
                                comment=reviewer_comment,
                                edited_draft=edited_draft if approve else "",
                            )
                        except Exception as exc:
                            st.error(f"No se pudo reanudar el workflow: {exc}")
                            st.stop()
                    case["workflow"] = completed
                    st.session_state["p05_case"] = case
                    st.rerun()
            else:
                if workflow.get("workflow_status") == "completed_approved":
                    st.success("✅ Caso 360º completado con aprobación humana.")
                elif workflow.get("workflow_status") == "completed_rejected":
                    st.error("⛔ Caso 360º completado con rechazo humano.")
                else:
                    st.success(f"Workflow completado: {workflow.get('workflow_status')}")
                st.markdown(workflow.get("final_output", ""))

            with st.expander("🔎 Abrir la caja: datos, estado y checkpoint"):
                st.markdown("**Datos empresariales**")
                st.json(enterprise_data)
                st.markdown("**Timeline**")
                st.json(workflow.get("timeline", []))
                st.markdown("**Thread ID**")
                st.code(workflow.get("_thread_id", ""), language=None)
                st.markdown("**Uso del LLM en el briefing**")
                st.json(workflow.get("usage", {}))

        with capability_tabs[3]:
            st.markdown("### Trazabilidad de extremo a extremo")
            st.write(
                {
                    "case_id": case["case_id"],
                    "workflow_thread_id": workflow.get("_thread_id"),
                    "workflow_status": workflow.get("workflow_status"),
                    "workflow_interrupted": workflow.get("_interrupted"),
                }
            )

            usage_rows = [
                {"capability": "Analyze", **case["analysis"].get("usage", {})},
                {"capability": "Knowledge", **knowledge.get("usage", {})},
                {"capability": "Investigate briefing", **workflow.get("usage", {})},
            ]
            st.dataframe(pd.DataFrame(usage_rows), use_container_width=True, hide_index=True)
            st.markdown("**Uso LLM agregado al iniciar el caso**")
            st.json(case.get("usage", {}))
            st.markdown("**Timeline de Investigate**")
            st.json(workflow.get("timeline", []))

            st.info(
                "Tres capacidades pueden observar la misma situación desde perspectivas diferentes: "
                "Analyze estructura el reporte, Knowledge recupera conocimiento e Investigate "
                "contrasta sistemas y gobierna el proceso."
            )
    else:
        st.caption(
            "Ejecuta el caso para ver cómo las capacidades construidas durante el curso "
            "se combinan alrededor de una única situación empresarial."
        )


elif view.startswith("🛡️"):
    st.subheader("Assurance · controles básicos y pruebas adversariales")
    st.info(
        "No intentamos demostrar que el prototipo sea 'seguro por definición'. "
        "Comprobamos controles concretos y hacemos visibles sus límites."
    )

    if st.button(
        "🛡️ Ejecutar checks deterministas",
        type="primary",
        use_container_width=True,
        key="p05_controls",
    ):
        try:
            st.session_state["p05_controls_result"] = run_control_checks()
        except Exception as exc:
            st.error(f"No se pudieron ejecutar los checks: {exc}")
            st.stop()

    controls = st.session_state.get("p05_controls_result")
    if controls:
        if controls["all_pass"]:
            st.success("Todos los checks deterministas han pasado.")
        else:
            st.error("Algún check determinista ha fallado. Revisa la evidencia.")

        checks_df = pd.DataFrame(controls["checks"])
        st.dataframe(checks_df, use_container_width=True, hide_index=True)

        with st.expander("🔎 Evidencia de controles"):
            st.markdown("**Base de datos**")
            st.json(controls["database"])
            st.markdown("**Workflow**")
            st.json(controls["workflow"])

    st.divider()
    st.markdown("### Prompt injection contra RAG")
    st.caption(
        "Esta prueba sí usa el LLM. No la reducimos a un PASS/FAIL ingenuo: mostramos la respuesta "
        "y la evaluamos contra criterios explícitos."
    )

    if st.button(
        "🧪 Lanzar prompt injection",
        use_container_width=True,
        key="p05_injection",
    ):
        with st.spinner("Ejecutando el ataque contra un contexto RAG controlado..."):
            try:
                st.session_state["p05_injection_result"] = run_rag_prompt_injection_probe()
            except Exception as exc:
                st.error(f"No se pudo ejecutar la prueba: {exc}")
                st.stop()

    injection = st.session_state.get("p05_injection_result")
    if injection:
        st.markdown("**Ataque enviado**")
        st.code(injection["attack"], language=None)
        st.markdown("**Respuesta del sistema**")
        st.markdown(injection["answer"])
        st.markdown("**Criterios de revisión**")
        for item in injection["review_criteria"]:
            st.markdown(f"- {item}")
        st.markdown("**Uso**")
        st.json(injection["usage"])
        with st.expander("Contexto que recibió el LLM"):
            st.code(injection["context"], language=None)


else:
    st.subheader("Arquitectura final del prototipo")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("### 💬 Knowledge")
        st.write("Embeddings → retrieval → RAG → fuentes → evaluación.")
        st.page_link("pages/1_Knowledge.py", label="Abrir Knowledge")
    with c2:
        st.markdown("### 📄 Analyze")
        st.write("Texto, documentos e imagen → salida estructurada validada.")
        st.page_link("pages/2_Analyze.py", label="Abrir Analyze")
    with c3:
        st.markdown("### 🎨 Create")
        st.write("Generación visual sintética con procedencia explícita.")
        st.page_link("pages/3_Create.py", label="Abrir Create")
    with c4:
        st.markdown("### 🔧 Investigate")
        st.write("Tools + datos + RAG + LangGraph + aprobación humana.")
        st.page_link("pages/4_Investigate.py", label="Abrir Investigate")

    st.markdown("### Evolución durante el curso")
    st.code(
        "\n".join(
            [
                "M01  → LLM + salida estructurada",
                "M02  → ML clásico + LLM + routing híbrido",
                "M03  → fundamentos de redes neuronales y atención",
                "M04  → multimodalidad + generación visual",
                "M05  → tokens + embeddings + análisis documental",
                "M06  → RAG + LangChain + tools + LangGraph + aplicación integrada",
            ]
        ),
        language=None,
    )

    st.markdown("### Fronteras del prototipo")
    st.warning(
        "Production-shaped no significa production-ready. El curso muestra patrones reales, "
        "pero deliberadamente no implementa todos los requisitos de una plataforma productiva."
    )
    st.markdown(
        """
- El vector store principal del laboratorio es local/en memoria.
- El workflow usa `InMemorySaver`; producción requiere checkpointing durable.
- No hay autenticación, RBAC ni segregación real de clientes.
- No se ejecutan side effects operativos reales desde el workflow.
- La evaluación y las pruebas adversariales son introductorias, no una certificación de seguridad.
- Las respuestas del LLM siguen requiriendo grounding, observabilidad y revisión según el riesgo.
"""
    )

    st.markdown("### Principio de diseño final")
    st.code(
        "IA flexible donde aporta valor\n+\nsoftware determinista donde importa el control\n+\npersonas donde el riesgo lo exige",
        language=None,
    )

st.divider()
st.caption(
    "M06-P05 no añade una quinta capacidad aislada: integra y somete a revisión el sistema construido durante todo el curso."
)
