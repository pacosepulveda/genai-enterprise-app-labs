"""LLM ticket classifier used in M02-P02.

The classifier intentionally mirrors the five labels from the classical ML
baseline while adding two application-oriented signals: whether the ticket is
inside the taxonomy and whether human review is advisable.
"""

from __future__ import annotations

import json
import time
from typing import Literal

from pydantic import BaseModel, ConfigDict

from enterprise_genai.config import get_settings
from enterprise_genai.models.bedrock import bedrock_runtime


TicketCategory = Literal[
    "access",
    "network",
    "application",
    "security",
    "hardware",
]


class LLMTicketClassification(BaseModel):
    """Structured classification returned by the Bedrock model."""

    model_config = ConfigDict(extra="forbid")

    category: TicketCategory
    in_scope: bool
    needs_review: bool
    explanation: str


def ticket_classification_schema() -> dict:
    """Return the JSON Schema used for Bedrock structured output."""

    return LLMTicketClassification.model_json_schema()


def classify_ticket_with_llm(text: str) -> dict:
    """Classify one support ticket with Bedrock and return validated metadata."""

    settings = get_settings()
    model_id = settings.bedrock_text_model_id
    if not model_id:
        raise ValueError("BEDROCK_TEXT_MODEL_ID is not configured")

    schema = ticket_classification_schema()

    taxonomy = """
Clasifica tickets de soporte usando esta taxonomía:

- access: autenticación, contraseñas, MFA, identidad, permisos o acceso de usuario.
- network: conectividad, Wi-Fi, DNS, transporte VPN, latencia, pérdida de paquetes o enlaces.
- application: fallos funcionales de software, ERP, CRM, portales o aplicaciones.
- security: phishing, malware, actividad sospechosa, compromiso, alertas EDR/SOC o MFA no solicitado.
- hardware: fallos físicos de portátil, monitor, dock, teclado, ratón, batería, webcam o periféricos.

Reglas:
- Usa únicamente la información del ticket.
- `category` debe ser siempre una de las cinco categorías anteriores para permitir una comparación cerrada.
- Si el ticket no pertenece realmente a ninguna categoría, elige la categoría más cercana solo como comparación forzada y marca `in_scope=false`.
- Marca `needs_review=true` si el ticket es ambiguo, mezcla categorías relevantes o está fuera de alcance.
- No inventes hechos.
- `explanation` debe ser breve y explicar la decisión sin razonamiento paso a paso.
""".strip()

    request = {
        "modelId": model_id,
        "system": [{"text": taxonomy}],
        "messages": [
            {
                "role": "user",
                "content": [{"text": f"Ticket:\n{text}"}],
            }
        ],
        "inferenceConfig": {
            "temperature": 0.0,
            "maxTokens": 180,
        },
        "outputConfig": {
            "textFormat": {
                "type": "json_schema",
                "structure": {
                    "jsonSchema": {
                        "schema": json.dumps(schema),
                        "name": "ticket_classification",
                        "description": "Structured enterprise support ticket classification",
                    }
                },
            }
        },
    }

    started = time.perf_counter()
    response = bedrock_runtime().converse(**request)
    client_ms = round((time.perf_counter() - started) * 1000)

    raw_text = response["output"]["message"]["content"][0]["text"]
    classification = LLMTicketClassification.model_validate_json(raw_text)

    return {
        "classification": classification,
        "raw_text": raw_text,
        "schema": schema,
        "usage": response.get("usage", {}),
        "metrics": response.get("metrics", {}),
        "stop_reason": response.get("stopReason"),
        "model_id": model_id,
        "client_ms": client_ms,
    }
