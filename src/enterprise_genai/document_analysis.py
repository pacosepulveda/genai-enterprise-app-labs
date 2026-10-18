"""Structured enterprise-document analysis for M05-P03."""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict

from enterprise_genai.config import get_settings
from enterprise_genai.models.bedrock import bedrock_runtime


class DocumentEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: Literal[
        "person",
        "team",
        "organization",
        "service",
        "system",
        "date",
        "time",
        "identifier",
        "other",
    ]
    evidence: str


class EnterpriseDocumentAnalysis(BaseModel):
    """Machine-readable analysis of a general enterprise document."""

    model_config = ConfigDict(extra="forbid")

    title: str
    document_type: Literal[
        "email",
        "support_ticket",
        "policy",
        "procedure",
        "report",
        "other",
    ]
    category: Literal[
        "operations",
        "support",
        "security",
        "workplace",
        "commercial",
        "other",
    ]
    summary: str
    entities: list[DocumentEntity]
    key_facts: list[str]
    requested_actions: list[str]
    recommended_actions: list[str]
    dates_or_deadlines: list[str]
    uncertainties: list[str]
    human_review_required: bool
    review_reason: str


def enterprise_document_json_schema() -> dict:
    return EnterpriseDocumentAnalysis.model_json_schema()


def _structured_output_config(schema: dict) -> dict:
    return {
        "textFormat": {
            "type": "json_schema",
            "structure": {
                "jsonSchema": {
                    "schema": json.dumps(schema),
                    "name": "enterprise_document_analysis",
                    "description": "Structured analysis of an enterprise document",
                }
            },
        }
    }


def analyze_enterprise_document(text: str) -> dict:
    """Analyze an email, ticket, policy, procedure or report with Bedrock."""

    if not text.strip():
        raise ValueError("text cannot be empty")

    settings = get_settings()
    model_id = settings.bedrock_text_model_id
    if not model_id:
        raise ValueError("BEDROCK_TEXT_MODEL_ID is not configured")

    schema = enterprise_document_json_schema()

    request = {
        "modelId": model_id,
        "system": [
            {
                "text": (
                    "Analiza documentos empresariales usando únicamente el contenido proporcionado. "
                    "No inventes personas, fechas, prioridades, compromisos ni causas. "
                    "Distingue hechos explícitos de recomendaciones generadas por el modelo. "
                    "En requested_actions incluye solo acciones solicitadas explícitamente en el documento. "
                    "En recommended_actions puedes proponer pasos razonables, pero deben quedar separados de los hechos. "
                    "En dates_or_deadlines conserva las fechas u horas tal como aparecen; no completes años ni zonas horarias. "
                    "Cada entidad debe incluir una evidencia textual breve que justifique su extracción. "
                    "Usa uncertainties para señalar información relevante que falta o resulta ambigua. "
                    "Marca revisión humana cuando el documento implique una decisión sensible, una excepción, "
                    "una acción con impacto operativo relevante o incertidumbre que no deba resolverse automáticamente."
                )
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "Convierte el siguiente documento empresarial en la estructura solicitada.\n\n"
                            f"DOCUMENTO:\n{text}"
                        )
                    }
                ],
            }
        ],
        "inferenceConfig": {
            "temperature": 0.0,
            "maxTokens": 1400,
        },
        "outputConfig": _structured_output_config(schema),
    }

    response = bedrock_runtime().converse(**request)
    raw_text = response["output"]["message"]["content"][0]["text"]
    stop_reason = response.get("stopReason")

    if stop_reason == "max_tokens":
        usage = response.get("usage", {})
        raise RuntimeError(
            "Bedrock alcanzó el límite de salida antes de completar el JSON "
            f"(outputTokens={usage.get('outputTokens')})."
        )

    parsed = EnterpriseDocumentAnalysis.model_validate_json(raw_text)

    return {
        "analysis": parsed,
        "raw_text": raw_text,
        "schema": schema,
        "usage": response.get("usage", {}),
        "metrics": response.get("metrics", {}),
        "stop_reason": stop_reason,
        "model_id": model_id,
    }
