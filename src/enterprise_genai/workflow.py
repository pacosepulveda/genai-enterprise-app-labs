"""LangGraph incident workflow for M06-P04.

Combines read-only enterprise tools, retrieved operational guidance, a grounded
LLM briefing, deterministic routing, and a human approval gate.
"""

from __future__ import annotations

import json
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import NotRequired, TypedDict

from enterprise_genai.enterprise_tools import (
    get_contract_sla,
    get_open_incidents,
    get_service_status,
)
from enterprise_genai.models.bedrock import bedrock_runtime
from enterprise_genai.rag import build_rag_index, chunk_documents, retrieve_chunks
from enterprise_genai.config import get_settings


CORPUS_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge" / "m05_enterprise_chunks.json"


class IncidentWorkflowState(TypedDict):
    customer_name: str
    service_name: str
    question: str
    enterprise_data: NotRequired[dict[str, Any]]
    retrieved_sources: NotRequired[list[dict[str, Any]]]
    retrieval_query: NotRequired[str]
    assessment: NotRequired[dict[str, Any]]
    requires_human_approval: NotRequired[bool]
    approval_reason: NotRequired[str]
    approval_decision: NotRequired[dict[str, Any]]
    final_output: NotRequired[str]
    workflow_status: NotRequired[str]
    timeline: NotRequired[list[str]]
    usage: NotRequired[dict[str, int]]


def _append_timeline(state: IncidentWorkflowState, event: str) -> list[str]:
    return [*state.get("timeline", []), event]


def _sum_usage(total: dict[str, int], usage: dict[str, Any]) -> dict[str, int]:
    merged = dict(total)
    for key, value in usage.items():
        if isinstance(value, int):
            merged[key] = merged.get(key, 0) + value
    return merged


def _corpus_service(service_name: str) -> str:
    name = service_name.lower()
    if "vpn" in name:
        return "VPN"
    if "identity" in name or "mfa" in name:
        return "Identity"
    if "network" in name or "wan" in name:
        return "Network"
    return "Todos"


@lru_cache(maxsize=1)
def _knowledge_index() -> tuple[list[dict[str, Any]], Any]:
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Knowledge corpus not found: {CORPUS_PATH}")
    records = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    chunks = chunk_documents(records, chunk_size_words=36, overlap_words=8)
    index = build_rag_index(chunks, max_workers=8)
    return chunks, index["matrix"]


def collect_enterprise_data(state: IncidentWorkflowState) -> dict[str, Any]:
    customer = state["customer_name"]
    service = state["service_name"]
    enterprise_data = {
        "open_incidents": get_open_incidents(customer, service),
        "service_status": get_service_status(service),
        "contract_sla": get_contract_sla(customer, service),
    }
    return {
        "enterprise_data": enterprise_data,
        "timeline": _append_timeline(state, "collect_enterprise_data"),
        "workflow_status": "enterprise_data_collected",
    }


def retrieve_operational_guidance(state: IncidentWorkflowState) -> dict[str, Any]:
    chunks, matrix = _knowledge_index()
    data = state["enterprise_data"]
    incident_titles = [
        item.get("title", "")
        for item in data["open_incidents"].get("incidents", [])
    ]
    status_message = data["service_status"].get("message", "")
    retrieval_query = " ".join(
        [
            state["question"],
            *incident_titles,
            status_message,
            "procedimiento operativo diagnóstico autenticación impacto usuarios",
        ]
    ).strip()

    retrieval = retrieve_chunks(
        retrieval_query,
        chunks,
        matrix,
        top_k=3,
        filters={"service": _corpus_service(state["service_name"])},
    )
    sources = []
    for index, item in enumerate(retrieval["results"], start=1):
        doc = item["document"]
        sources.append(
            {
                "source": f"S{index}",
                "score": round(float(item["score"]), 4),
                "document_id": doc["document_id"],
                "title": doc["title"],
                "service": doc["service"],
                "source_type": doc["source_type"],
                "content": doc["content"],
            }
        )

    return {
        "retrieval_query": retrieval_query,
        "retrieved_sources": sources,
        "timeline": _append_timeline(state, "retrieve_operational_guidance"),
        "workflow_status": "guidance_retrieved",
    }


def _parse_json_text(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
        if candidate.lower().startswith("json"):
            candidate = candidate[4:].lstrip()
    return json.loads(candidate)


def build_incident_brief(state: IncidentWorkflowState) -> dict[str, Any]:
    settings = get_settings()
    if not settings.bedrock_text_model_id:
        raise ValueError("BEDROCK_TEXT_MODEL_ID is not configured")

    data = state["enterprise_data"]
    sources = state.get("retrieved_sources", [])
    source_context = "\n\n".join(
        f"[{item['source']}] {item['document_id']} | {item['title']}\n{item['content']}"
        for item in sources
    )

    incidents = data["open_incidents"].get("incidents", [])
    severities = {str(item.get("severity", "")).upper() for item in incidents}
    service_status = str(data["service_status"].get("status", "")).lower()

    requires_approval = bool(
        "P1" in severities
        or service_status in {"degraded", "outage", "major_outage", "unavailable"}
    )
    if "P1" in severities and service_status == "degraded":
        approval_reason = (
            "Incidente P1 con servicio degradado: cualquier comunicación externa "
            "debe ser revisada por una persona responsable."
        )
    elif "P1" in severities:
        approval_reason = "Incidente P1: la comunicación externa requiere revisión humana."
    elif service_status != "operational":
        approval_reason = (
            f"El servicio está en estado {service_status}: la comunicación externa requiere revisión."
        )
    else:
        approval_reason = "No se activa la regla de aprobación humana."

    prompt = f"""
PREGUNTA DEL USUARIO:
{state['question']}

DATOS EMPRESARIALES ESTRUCTURADOS:
{json.dumps(data, ensure_ascii=False, indent=2)}

GUÍA OPERATIVA RECUPERADA:
{source_context}

REGLA DE APROBACIÓN CALCULADA POR LA APLICACIÓN:
requires_human_approval={requires_approval}
approval_reason={approval_reason}

Devuelve exclusivamente JSON válido con esta estructura:
{{
  "executive_summary": "resumen breve y factual",
  "priority": "P1/P2/P3/unknown",
  "evidence": ["hecho 1", "hecho 2"],
  "recommended_actions": ["acción soportada por datos o fuentes"],
  "customer_update_draft": "borrador breve para el cliente; no afirmes causa raíz si no está demostrada",
  "uncertainties": ["dato que no conocemos"]
}}

Reglas:
- Usa solo los datos estructurados y la guía recuperada.
- Cita las fuentes documentales como [S1], [S2], etc. en recommended_actions cuando proceda.
- `opened_at` indica cuándo se abrió el incidente; no lo conviertas en hora confirmada de inicio del fallo salvo que otra evidencia lo diga explícitamente.
- `response_minutes_p1` es un objetivo contractual de respuesta P1; no implica frecuencia de actualizaciones, tiempo de resolución ni incumplimiento del SLA.
- Las acciones descritas por un runbook son recomendaciones. No afirmes que ya se están ejecutando salvo que los datos estructurados lo confirmen.
- No inventes ventanas temporales, frecuencias, plazos, causas, resolución ni detalles operativos que no aparezcan explícitamente en los datos o fuentes.
- Si una acción contiene un término genérico como `cambios recientes`, consérvalo como tal; no lo conviertas en `últimas 24 horas`, `última semana` u otra ventana inventada.
- Separa claramente hechos observados, acciones recomendadas e incertidumbres.
- El customer_update_draft es solo un borrador sujeto a aprobación y debe ser especialmente conservador con hechos no confirmados.
""".strip()

    response = bedrock_runtime().converse(
        modelId=settings.bedrock_text_model_id,
        system=[
            {
                "text": (
                    "Eres un asistente de gestión de incidentes empresariales. "
                    "Construye un briefing basado exclusivamente en evidencia proporcionada. "
                    "Distingue hechos, recomendaciones e incertidumbres sin convertir unos en otros. "
                    "Devuelve JSON válido y nada más."
                )
            }
        ],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"temperature": 0.0, "maxTokens": 900},
    )
    text = response["output"]["message"]["content"][0]["text"]
    assessment = _parse_json_text(text)
    usage = _sum_usage(state.get("usage", {}), response.get("usage", {}))

    return {
        "assessment": assessment,
        "requires_human_approval": requires_approval,
        "approval_reason": approval_reason,
        "usage": usage,
        "timeline": _append_timeline(state, "build_incident_brief"),
        "workflow_status": "brief_ready",
    }


def route_after_brief(state: IncidentWorkflowState) -> str:
    if state.get("requires_human_approval", False):
        return "human_review"
    return "finalize"


def human_review(state: IncidentWorkflowState) -> dict[str, Any]:
    assessment = state["assessment"]
    payload = {
        "type": "customer_update_approval",
        "customer_name": state["customer_name"],
        "service_name": state["service_name"],
        "priority": assessment.get("priority", "unknown"),
        "reason": state.get("approval_reason"),
        "executive_summary": assessment.get("executive_summary"),
        "recommended_actions": assessment.get("recommended_actions", []),
        "customer_update_draft": assessment.get("customer_update_draft", ""),
        "uncertainties": assessment.get("uncertainties", []),
    }
    decision = interrupt(payload)

    if isinstance(decision, dict):
        approved = bool(decision.get("approved", False))
        comment = str(decision.get("comment", "")).strip()
        edited_draft = str(decision.get("edited_draft", "")).strip()
    else:
        approved = bool(decision)
        comment = ""
        edited_draft = ""

    return {
        "approval_decision": {
            "approved": approved,
            "comment": comment,
            "edited_draft": edited_draft,
        },
        "timeline": _append_timeline(
            state, "human_review_approved" if approved else "human_review_rejected"
        ),
        "workflow_status": "approved" if approved else "rejected",
    }


def finalize(state: IncidentWorkflowState) -> dict[str, Any]:
    assessment = state["assessment"]
    decision = state.get(
        "approval_decision",
        {"approved": not state.get("requires_human_approval", False), "comment": "", "edited_draft": ""},
    )
    approved = bool(decision.get("approved", False))
    draft = decision.get("edited_draft") or assessment.get("customer_update_draft", "")
    actions = assessment.get("recommended_actions", [])
    action_text = "\n".join(f"- {item}" for item in actions) or "- Sin acciones propuestas."

    if approved:
        final_output = (
            "## ✅ Briefing aprobado\n\n"
            f"**Resumen ejecutivo:** {assessment.get('executive_summary', '')}\n\n"
            f"**Prioridad:** {assessment.get('priority', 'unknown')}\n\n"
            f"**Acciones recomendadas:**\n{action_text}\n\n"
            "### Borrador de actualización al cliente aprobado para el siguiente paso\n\n"
            f"{draft}"
        )
        status = "completed_approved"
    else:
        comment = decision.get("comment", "")
        final_output = (
            "## ⛔ Comunicación externa no aprobada\n\n"
            f"**Resumen interno:** {assessment.get('executive_summary', '')}\n\n"
            f"**Prioridad:** {assessment.get('priority', 'unknown')}\n\n"
            f"**Acciones recomendadas:**\n{action_text}\n\n"
            f"**Comentario del revisor:** {comment or 'Sin comentario.'}\n\n"
            "El borrador de comunicación queda retenido y no se considera aprobado."
        )
        status = "completed_rejected"

    return {
        "final_output": final_output,
        "workflow_status": status,
        "timeline": _append_timeline(state, "finalize"),
    }


def build_workflow_graph():
    builder = StateGraph(IncidentWorkflowState)
    builder.add_node("collect_enterprise_data", collect_enterprise_data)
    builder.add_node("retrieve_operational_guidance", retrieve_operational_guidance)
    builder.add_node("build_incident_brief", build_incident_brief)
    builder.add_node("human_review", human_review)
    builder.add_node("finalize", finalize)

    builder.add_edge(START, "collect_enterprise_data")
    builder.add_edge("collect_enterprise_data", "retrieve_operational_guidance")
    builder.add_edge("retrieve_operational_guidance", "build_incident_brief")
    builder.add_conditional_edges(
        "build_incident_brief",
        route_after_brief,
        {"human_review": "human_review", "finalize": "finalize"},
    )
    builder.add_edge("human_review", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile(checkpointer=InMemorySaver())


WORKFLOW_GRAPH = build_workflow_graph()


def _normalize_result(result: dict[str, Any], thread_id: str) -> dict[str, Any]:
    interrupts = result.get("__interrupt__", [])
    payload = None
    if interrupts:
        first = interrupts[0]
        payload = getattr(first, "value", first)
    normalized = dict(result)
    normalized["_thread_id"] = thread_id
    normalized["_interrupted"] = bool(interrupts)
    normalized["_interrupt_payload"] = payload
    return normalized


def start_incident_workflow(
    *,
    customer_name: str,
    service_name: str,
    question: str,
    thread_id: str | None = None,
) -> dict[str, Any]:
    if not customer_name.strip() or not service_name.strip() or not question.strip():
        raise ValueError("customer_name, service_name and question are required")
    resolved_thread_id = thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": resolved_thread_id}}
    initial: IncidentWorkflowState = {
        "customer_name": customer_name,
        "service_name": service_name,
        "question": question,
        "timeline": [],
        "usage": {},
        "workflow_status": "started",
    }
    result = WORKFLOW_GRAPH.invoke(initial, config=config)
    return _normalize_result(result, resolved_thread_id)


def resume_incident_workflow(
    *,
    thread_id: str,
    approved: bool,
    comment: str = "",
    edited_draft: str = "",
) -> dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    result = WORKFLOW_GRAPH.invoke(
        Command(
            resume={
                "approved": approved,
                "comment": comment,
                "edited_draft": edited_draft,
            }
        ),
        config=config,
    )
    return _normalize_result(result, thread_id)


def workflow_definition() -> dict[str, Any]:
    return {
        "nodes": [
            "collect_enterprise_data",
            "retrieve_operational_guidance",
            "build_incident_brief",
            "human_review",
            "finalize",
        ],
        "edges": [
            "START → collect_enterprise_data",
            "collect_enterprise_data → retrieve_operational_guidance",
            "retrieve_operational_guidance → build_incident_brief",
            "build_incident_brief → human_review (P1/degraded)",
            "build_incident_brief → finalize (no approval required)",
            "human_review → finalize",
            "finalize → END",
        ],
        "human_in_the_loop": {
            "mechanism": "interrupt() + Command(resume=...)",
            "checkpointer": "InMemorySaver",
            "production_note": "Use a durable checkpointer in production.",
        },
    }
