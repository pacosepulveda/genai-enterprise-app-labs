import json

import pandas as pd
import streamlit as st

from enterprise_genai.enterprise_tools import (
    TOOL_CONFIG,
    database_overview,
    investigate_with_tools,
)
from enterprise_genai.workflow import (
    resume_incident_workflow,
    start_incident_workflow,
    workflow_definition,
)


st.set_page_config(page_title="Investigate", page_icon="🔧", layout="wide")

st.title("🔧 Investigate")
st.caption("M06 · Tool calling → LangGraph workflow empresarial con aprobación humana")

mode = st.radio(
    "Modo",
    ["Tool Calling (M06-P03)", "Workflow LangGraph (M06-P04)"],
    horizontal=True,
)


def render_p03() -> None:
    st.subheader("Tool Calling & Enterprise Data")
    st.info(
        "El modelo no recibe acceso libre a la base de datos. Solo puede solicitar tools permitidas; "
        "la aplicación ejecuta consultas parametrizadas sobre SQLite en modo de solo lectura."
    )

    try:
        overview = database_overview()
    except Exception as exc:
        st.error(str(exc))
        st.code("python scripts/init_database.py", language="bash")
        st.stop()

    c1, c2 = st.columns([2, 1])
    with c1:
        question = st.text_area(
            "Pregunta de investigación",
            value=(
                "Asteria Retail informa de fallos de autenticación en Managed VPN. "
                "Investiga si hay un incidente abierto, cuál es el estado actual del servicio "
                "y qué tiempo de respuesta P1 tiene contratado. Resume la situación sin inventar datos."
            ),
            height=120,
            key="p03_question",
        )
    with c2:
        st.metric("Tablas", len(overview["tables"]))
        st.metric("Tools disponibles", len(TOOL_CONFIG["tools"]))

    with st.expander("🧰 Tools disponibles"):
        for item in TOOL_CONFIG["tools"]:
            spec = item["toolSpec"]
            st.markdown(f"**`{spec['name']}`** — {spec['description']}")
            st.code(
                json.dumps(spec["inputSchema"]["json"], ensure_ascii=False, indent=2),
                language="json",
            )

    run = st.button(
        "Investigar con tools",
        type="primary",
        use_container_width=True,
        key="p03_run",
    )

    if run:
        if not question.strip():
            st.warning("Introduce una pregunta antes de continuar.")
            st.stop()

        with st.spinner(
            "El modelo decide qué datos necesita, ejecuta tools permitidas y resume resultados..."
        ):
            try:
                investigation = investigate_with_tools(question)
            except Exception as exc:
                st.error(f"No se pudo completar la investigación: {exc}")
                st.stop()
        st.session_state["p03_investigation"] = investigation

    investigation = st.session_state.get("p03_investigation")
    if not investigation:
        return

    st.success(
        f"Investigación completada · {len(investigation['tool_trace'])} tool calls · "
        f"{len(investigation['model_trace'])} turnos del modelo"
    )

    st.subheader("Respuesta")
    st.markdown(investigation["answer"])

    st.subheader("Tool calls")
    rows = []
    for item in investigation["tool_trace"]:
        rows.append(
            {
                "turn": item["turn"],
                "tool": item["name"],
                "status": item["status"],
                "input": json.dumps(item["input"], ensure_ascii=False),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    for index, item in enumerate(investigation["tool_trace"], start=1):
        with st.expander(
            f"#{index} · {item['name']} · {item['status']}",
            expanded=index == 1,
        ):
            st.markdown("**Argumentos solicitados por el modelo**")
            st.json(item["input"])
            st.markdown("**Resultado devuelto por la aplicación**")
            st.json(item["result"])

    with st.expander("🔎 Abrir la caja: turnos, tokens y control"):
        turn_rows = []
        for turn in investigation["model_trace"]:
            turn_rows.append(
                {
                    "turn": turn["turn"],
                    "stop_reason": turn["stop_reason"],
                    "input_tokens": turn["usage"].get("inputTokens"),
                    "output_tokens": turn["usage"].get("outputTokens"),
                    "total_tokens": turn["usage"].get("totalTokens"),
                    "content_blocks": len(turn["content"]),
                }
            )
        st.dataframe(pd.DataFrame(turn_rows), use_container_width=True, hide_index=True)
        st.markdown("**Uso agregado**")
        st.json(investigation["usage"])
        st.markdown("**System prompt**")
        st.code(investigation["system_prompt"], language=None)
        st.markdown("**Controles de ejecución**")
        st.write(
            {
                "sqlite_mode": "read-only",
                "arbitrary_sql_tool_exposed": False,
                "allow_listed_tools": [
                    item["toolSpec"]["name"] for item in TOOL_CONFIG["tools"]
                ],
                "database_tables": overview["tables"],
            }
        )


def _workflow_path(run: dict) -> str:
    timeline = run.get("timeline", [])
    labels = {
        "collect_enterprise_data": "Datos empresariales ✅",
        "retrieve_operational_guidance": "RAG operativo ✅",
        "build_incident_brief": "Briefing IA ✅",
        "human_review_approved": "Aprobación humana ✅",
        "human_review_rejected": "Rechazo humano ⛔",
        "finalize": "Finalizado ✅",
    }
    parts = [labels.get(item, item) for item in timeline]
    if run.get("_interrupted"):
        parts.append("Aprobación humana ⏸️")
    return "  →  ".join(parts)


def render_p04() -> None:
    st.subheader("LangGraph Enterprise Workflow")
    st.info(
        "Este workflow combina datos operativos, documentación RAG y un briefing generado. "
        "Una regla de negocio —no el LLM— decide si debe detenerse para aprobación humana."
    )

    definition = workflow_definition()

    left, right = st.columns([2, 1])
    with left:
        question = st.text_area(
            "Objetivo de la investigación",
            value=(
                "Asteria Retail informa de fallos de autenticación en Managed VPN. "
                "Construye un briefing de incidente usando datos empresariales y guía operativa relevante. "
                "Prepara un borrador breve de actualización al cliente, pero no lo consideres aprobado "
                "sin revisión humana."
            ),
            height=130,
            key="p04_question",
        )
    with right:
        customer = st.selectbox(
            "Cliente",
            ["Asteria Retail", "BlueWave Logistics", "NovaHealth Services"],
            key="p04_customer",
        )
        service = st.selectbox(
            "Servicio",
            ["Managed VPN", "Managed Network", "Identity Platform"],
            key="p04_service",
        )

    with st.expander("🗺️ Workflow antes de ejecutarlo"):
        st.code(
            "\n".join(
                [
                    "START",
                    "  ↓",
                    "collect_enterprise_data",
                    "  ↓",
                    "retrieve_operational_guidance",
                    "  ↓",
                    "build_incident_brief",
                    "  ↓",
                    "¿P1 o servicio degradado?",
                    "  ├─ no → finalize → END",
                    "  └─ sí → human_review ⏸ → finalize → END",
                ]
            ),
            language=None,
        )
        st.json(definition["human_in_the_loop"])

    if st.button(
        "▶️ Ejecutar workflow",
        type="primary",
        use_container_width=True,
        key="p04_run",
    ):
        st.session_state.pop("p04_run_state", None)
        if not question.strip():
            st.warning("Introduce un objetivo antes de continuar.")
            st.stop()
        with st.spinner(
            "Reuniendo datos empresariales, recuperando guía operativa y construyendo el briefing..."
        ):
            try:
                run = start_incident_workflow(
                    customer_name=customer,
                    service_name=service,
                    question=question,
                )
            except Exception as exc:
                st.error(f"No se pudo ejecutar el workflow: {exc}")
                st.stop()
        st.session_state["p04_run_state"] = run

    run = st.session_state.get("p04_run_state")
    if not run:
        st.caption(
            "El valor empresarial del ejemplo es reunir contexto disperso y detenerse "
            "exactamente en el punto donde debe decidir una persona."
        )
        return

    st.markdown("### Ruta ejecutada")
    st.code(_workflow_path(run), language=None)

    data = run.get("enterprise_data", {})
    incidents = data.get("open_incidents", {}).get("incidents", [])
    first_incident = incidents[0] if incidents else {}
    service_status = data.get("service_status", {})
    sla = data.get("contract_sla", {})

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Prioridad", first_incident.get("severity", "—"))
    k2.metric("Estado servicio", str(service_status.get("status", "—")).upper())
    k3.metric(
        "SLA P1",
        f"{sla.get('response_minutes_p1')} min" if sla.get("response_minutes_p1") else "—",
    )
    k4.metric("Fuentes RAG", len(run.get("retrieved_sources", [])))

    st.markdown("### Paquete de decisión")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 📊 Evidencia operativa")
        st.json(data)

    with col_b:
        st.markdown("#### 📚 Guía operativa recuperada")
        for source in run.get("retrieved_sources", []):
            with st.expander(
                f"[{source['source']}] {source['title']} · score {source['score']:.4f}",
                expanded=source["source"] == "S1",
            ):
                st.caption(
                    f"{source['document_id']} · {source['service']} · {source['source_type']}"
                )
                st.write(source["content"])

    assessment = run.get("assessment", {})
    st.markdown("#### 🧠 Briefing generado")
    st.markdown(f"**Resumen ejecutivo:** {assessment.get('executive_summary', '—')}")
    st.markdown(f"**Prioridad propuesta:** `{assessment.get('priority', 'unknown')}`")

    if assessment.get("evidence"):
        st.markdown("**Evidencias sintetizadas**")
        for item in assessment["evidence"]:
            st.markdown(f"- {item}")

    if assessment.get("recommended_actions"):
        st.markdown("**Acciones recomendadas**")
        for item in assessment["recommended_actions"]:
            st.markdown(f"- {item}")

    if assessment.get("uncertainties"):
        st.markdown("**Incertidumbres**")
        for item in assessment["uncertainties"]:
            st.markdown(f"- {item}")

    st.markdown("#### ✉️ Borrador de actualización al cliente")
    draft = assessment.get("customer_update_draft", "")
    st.info(draft or "No se generó borrador.")

    if run.get("_interrupted"):
        st.warning("⏸️ Aprobación humana requerida")
        st.write(run.get("approval_reason"))
        st.caption(
            "LangGraph ha guardado el estado del workflow. La ejecución no continúa "
            "hasta recibir una decisión para este mismo thread."
        )

        edited_draft = st.text_area(
            "Editar borrador antes de aprobar (opcional)",
            value=draft,
            height=150,
            key=f"p04_draft_{run['_thread_id']}",
        )
        review_comment = st.text_input(
            "Comentario del revisor",
            value="",
            key=f"p04_comment_{run['_thread_id']}",
        )

        approve_col, reject_col = st.columns(2)
        with approve_col:
            approve = st.button(
                "✅ Aprobar y reanudar",
                type="primary",
                use_container_width=True,
                key=f"p04_approve_{run['_thread_id']}",
            )
        with reject_col:
            reject = st.button(
                "⛔ Rechazar y reanudar",
                use_container_width=True,
                key=f"p04_reject_{run['_thread_id']}",
            )

        if approve or reject:
            with st.spinner("Reanudando el mismo workflow desde su checkpoint..."):
                try:
                    completed = resume_incident_workflow(
                        thread_id=run["_thread_id"],
                        approved=bool(approve),
                        comment=review_comment,
                        edited_draft=edited_draft if approve else "",
                    )
                except Exception as exc:
                    st.error(f"No se pudo reanudar el workflow: {exc}")
                    st.stop()
            st.session_state["p04_run_state"] = completed
            st.rerun()
    else:
        status = run.get("workflow_status", "")
        if status == "completed_approved":
            st.success("✅ Workflow completado con aprobación humana.")
        elif status == "completed_rejected":
            st.error("⛔ Workflow completado: la comunicación externa fue rechazada.")
        else:
            st.success(f"Workflow completado: {status}")
        st.markdown(run.get("final_output", ""))

    with st.expander("🔎 Abrir la caja: estado, routing, checkpoint y tokens"):
        st.markdown("**Thread ID / checkpoint**")
        st.code(run.get("_thread_id", ""), language=None)
        st.markdown("**Timeline**")
        st.json(run.get("timeline", []))
        st.markdown("**Routing de aprobación**")
        st.write(
            {
                "requires_human_approval": run.get("requires_human_approval"),
                "approval_reason": run.get("approval_reason"),
                "decision_source": "deterministic application rule",
                "rule": "P1 OR service_status != operational",
            }
        )
        st.markdown("**Uso del LLM en el briefing**")
        st.json(run.get("usage", {}))
        st.markdown("**Human-in-the-loop**")
        st.json(definition["human_in_the_loop"])
        st.markdown("**Estado completo visible para el laboratorio**")
        debug_state = {
            key: value
            for key, value in run.items()
            if key not in {"__interrupt__"}
        }
        st.json(debug_state)


if mode.startswith("Tool Calling"):
    render_p03()
else:
    render_p04()

st.divider()
st.caption(
    "M06-P03 añade tools y datos estructurados. M06-P04 coordina datos + RAG + LLM + "
    "routing + aprobación humana. M06-P05 cerrará el prototipo empresarial completo."
)
