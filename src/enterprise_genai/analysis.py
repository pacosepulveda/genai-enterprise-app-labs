"""Structured incident analysis using Amazon Bedrock Converse.

M01-P02 introduces structured text analysis.
M04-P02 extends the same capability with optional visual evidence.
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict

from enterprise_genai.config import get_settings
from enterprise_genai.models.bedrock import bedrock_runtime


class IncidentAnalysis(BaseModel):
    """Machine-readable result produced by the text incident analyzer."""

    model_config = ConfigDict(extra="forbid")

    summary: str
    category: Literal[
        "authentication",
        "network",
        "application",
        "security",
        "other",
    ]
    affected_users: int | None
    affected_service: str | None
    observed_facts: list[str]
    hypotheses: list[str]
    recommended_actions: list[str]
    human_review_required: bool
    review_reason: str


class MultimodalIncidentAnalysis(IncidentAnalysis):
    """Structured analysis that keeps visual evidence explicit."""

    visual_summary: str | None
    visual_evidence: list[str]
    visual_uncertainties: list[str]
    text_image_consistency: Literal[
        "consistent",
        "partially_consistent",
        "inconsistent",
        "not_enough_information",
    ]


def incident_json_schema() -> dict:
    """Return the JSON Schema used by the text analyzer."""

    return IncidentAnalysis.model_json_schema()


def multimodal_incident_json_schema() -> dict:
    """Return the JSON Schema used by the multimodal analyzer."""

    return MultimodalIncidentAnalysis.model_json_schema()


def _structured_output_config(schema: dict, name: str, description: str) -> dict:
    return {
        "textFormat": {
            "type": "json_schema",
            "structure": {
                "jsonSchema": {
                    "schema": json.dumps(schema),
                    "name": name,
                    "description": description,
                }
            },
        }
    }


def analyze_incident(text: str) -> dict:
    """Analyze free-form incident text and return validated structured data."""

    settings = get_settings()
    model_id = settings.bedrock_text_model_id
    if not model_id:
        raise ValueError("BEDROCK_TEXT_MODEL_ID is not configured")

    schema = incident_json_schema()

    request = {
        "modelId": model_id,
        "system": [
            {
                "text": (
                    "Analiza incidencias empresariales usando únicamente la información "
                    "disponible. No inventes cifras, severidades, SLA ni causas raíz. "
                    "Si un dato no consta, usa null cuando el schema lo permita. "
                    "Separa hechos observados de hipótesis y marca revisión humana cuando "
                    "haya incertidumbre relevante."
                )
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "Convierte la siguiente incidencia en la estructura solicitada.\n\n"
                            + text
                        )
                    }
                ],
            }
        ],
        "inferenceConfig": {
            "temperature": 0.0,
            "maxTokens": 700,
        },
        "outputConfig": _structured_output_config(
            schema,
            "incident_analysis",
            "Structured analysis of an enterprise support incident",
        ),
    }

    response = bedrock_runtime().converse(**request)
    raw_text = response["output"]["message"]["content"][0]["text"]
    parsed = IncidentAnalysis.model_validate_json(raw_text)

    return {
        "analysis": parsed,
        "raw_text": raw_text,
        "schema": schema,
        "usage": response.get("usage", {}),
        "metrics": response.get("metrics", {}),
        "stop_reason": response.get("stopReason"),
        "model_id": model_id,
    }


def analyze_incident_multimodal(
    text: str,
    *,
    image_bytes: bytes,
    image_format: Literal["png", "jpeg", "gif", "webp"],
) -> dict:
    """Analyze incident text together with one visual evidence item.

    Image observations are kept separate from hypotheses so the application can
    show exactly what the model claims to have seen.
    """

    if not image_bytes:
        raise ValueError("image_bytes cannot be empty")

    settings = get_settings()
    model_id = settings.bedrock_text_model_id
    if not model_id:
        raise ValueError("BEDROCK_TEXT_MODEL_ID is not configured")

    schema = multimodal_incident_json_schema()

    request = {
        "modelId": model_id,
        "system": [
            {
                "text": (
                    "Analiza incidencias empresariales usando únicamente el texto y la imagen "
                    "proporcionados. No inventes cifras, severidades, SLA ni causas raíz. "
                    "Distingue rigurosamente entre hechos, evidencia visual e hipótesis. "
                    "En visual_evidence incluye solo elementos directamente observables en la "
                    "imagen. Si algo no se puede leer o inferir con seguridad, indícalo en "
                    "visual_uncertainties. Evalúa si texto e imagen son consistentes entre sí. "
                    "Una evidencia visual de degradación no equivale por sí sola a una causa raíz. "
                    "Marca revisión humana cuando exista incertidumbre o contradicción relevante."
                )
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "Analiza conjuntamente la descripción de la incidencia y la captura "
                            "adjunta. Produce exactamente la estructura solicitada.\n\n"
                            f"INCIDENCIA:\n{text}"
                        )
                    },
                    {
                        "image": {
                            "format": image_format,
                            "source": {"bytes": image_bytes},
                        }
                    },
                ],
            }
        ],
        "inferenceConfig": {
            "temperature": 0.0,
            "maxTokens": 1600,
        },
        "outputConfig": _structured_output_config(
            schema,
            "multimodal_incident_analysis",
            "Structured multimodal analysis of an enterprise support incident",
        ),
    }

    response = bedrock_runtime().converse(**request)
    raw_text = response["output"]["message"]["content"][0]["text"]
    stop_reason = response.get("stopReason")

    if stop_reason == "max_tokens":
        usage = response.get("usage", {})
        raise RuntimeError(
            "Bedrock alcanzó el límite de salida antes de completar el JSON "
            f"(outputTokens={usage.get('outputTokens')}). Aumenta maxTokens o reduce la salida."
        )

    parsed = MultimodalIncidentAnalysis.model_validate_json(raw_text)

    return {
        "analysis": parsed,
        "raw_text": raw_text,
        "schema": schema,
        "usage": response.get("usage", {}),
        "metrics": response.get("metrics", {}),
        "stop_reason": stop_reason,
        "model_id": model_id,
    }