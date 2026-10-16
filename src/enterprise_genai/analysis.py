"""Structured incident analysis using Amazon Bedrock Converse.

This module is intentionally small: the M01-P02 notebook first shows the raw
Converse request, then the Streamlit page reuses the same ideas through this
helper.
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict

from enterprise_genai.config import get_settings
from enterprise_genai.models.bedrock import bedrock_runtime


class IncidentAnalysis(BaseModel):
    """Machine-readable result produced by the incident analyzer."""

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


def incident_json_schema() -> dict:
    """Return the JSON Schema used by Bedrock structured outputs."""

    return IncidentAnalysis.model_json_schema()


def analyze_incident(text: str) -> dict:
    """Analyze free-form incident text and return validated structured data.

    The model is constrained by Bedrock structured outputs and the result is
    validated again locally with Pydantic before being returned to the app.
    """

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
        "outputConfig": {
            "textFormat": {
                "type": "json_schema",
                "structure": {
                    "jsonSchema": {
                        "schema": json.dumps(schema),
                        "name": "incident_analysis",
                        "description": (
                            "Structured analysis of an enterprise support incident"
                        ),
                    }
                },
            }
        },
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
