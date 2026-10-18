"""Read-only enterprise tools and transparent Bedrock tool-calling loop for M06-P03."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from enterprise_genai.config import get_settings
from enterprise_genai.models.bedrock import bedrock_runtime


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "enterprise.db"


def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Enterprise database not found at {DB_PATH}. Run: python scripts/init_database.py"
        )
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def database_overview() -> dict[str, Any]:
    """Return table names and row counts without exposing arbitrary SQL execution."""
    tables = ["customers", "services", "contracts", "service_status", "incidents"]
    with _connect() as conn:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            for table in tables
        }
    return {"database": str(DB_PATH), "tables": counts}


def get_service_status(service_name: str) -> dict[str, Any]:
    """Read the current status for one named managed service."""
    query = """
    SELECT s.service_id, s.name AS service_name, ss.status, ss.message, ss.updated_at
    FROM services s
    JOIN service_status ss ON ss.service_id = s.service_id
    WHERE lower(s.name) = lower(?) OR lower(s.name) LIKE '%' || lower(?) || '%'
    ORDER BY CASE WHEN lower(s.name) = lower(?) THEN 0 ELSE 1 END
    LIMIT 1
    """
    with _connect() as conn:
        row = conn.execute(query, (service_name, service_name, service_name)).fetchone()
    if row is None:
        return {"found": False, "service_name": service_name}
    return {"found": True, **dict(row)}


def get_open_incidents(customer_name: str, service_name: str) -> dict[str, Any]:
    """Return open incidents for a customer and managed service."""
    query = """
    SELECT i.incident_id, c.name AS customer_name, s.name AS service_name,
           i.severity, i.status, i.title, i.opened_at
    FROM incidents i
    JOIN customers c ON c.customer_id = i.customer_id
    JOIN services s ON s.service_id = i.service_id
    WHERE lower(c.name) = lower(?)
      AND (lower(s.name) = lower(?) OR lower(s.name) LIKE '%' || lower(?) || '%')
      AND lower(i.status) = 'open'
    ORDER BY i.opened_at DESC
    """
    with _connect() as conn:
        rows = conn.execute(query, (customer_name, service_name, service_name)).fetchall()
    return {
        "customer_name": customer_name,
        "service_name": service_name,
        "count": len(rows),
        "incidents": [dict(row) for row in rows],
    }


def get_contract_sla(customer_name: str, service_name: str) -> dict[str, Any]:
    """Return the contracted P1 response target for a customer/service pair."""
    query = """
    SELECT ctr.contract_id, c.name AS customer_name, c.tier,
           s.name AS service_name, ctr.response_minutes_p1
    FROM contracts ctr
    JOIN customers c ON c.customer_id = ctr.customer_id
    JOIN services s ON s.service_id = ctr.service_id
    WHERE lower(c.name) = lower(?)
      AND (lower(s.name) = lower(?) OR lower(s.name) LIKE '%' || lower(?) || '%')
    ORDER BY CASE WHEN lower(s.name) = lower(?) THEN 0 ELSE 1 END
    LIMIT 1
    """
    with _connect() as conn:
        row = conn.execute(
            query,
            (customer_name, service_name, service_name, service_name),
        ).fetchone()
    if row is None:
        return {
            "found": False,
            "customer_name": customer_name,
            "service_name": service_name,
        }
    return {"found": True, **dict(row)}


TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_service_status",
                "description": "Obtiene el estado actual de un servicio gestionado.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Nombre del servicio, por ejemplo Managed VPN.",
                            }
                        },
                        "required": ["service_name"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "get_open_incidents",
                "description": "Lista incidentes abiertos de un cliente para un servicio gestionado.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "customer_name": {"type": "string"},
                            "service_name": {"type": "string"},
                        },
                        "required": ["customer_name", "service_name"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "get_contract_sla",
                "description": "Obtiene el tiempo de respuesta P1 contratado para un cliente y servicio.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "customer_name": {"type": "string"},
                            "service_name": {"type": "string"},
                        },
                        "required": ["customer_name", "service_name"],
                    }
                },
            }
        },
    ]
}


def execute_tool(name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """Dispatch one allow-listed, read-only tool call."""
    if name == "get_service_status":
        return get_service_status(**tool_input)
    if name == "get_open_incidents":
        return get_open_incidents(**tool_input)
    if name == "get_contract_sla":
        return get_contract_sla(**tool_input)
    raise ValueError(f"Tool not allowed: {name}")


def _sum_usage(total: dict[str, int], usage: dict[str, Any]) -> None:
    for key, value in usage.items():
        if isinstance(value, int):
            total[key] = total.get(key, 0) + value


def investigate_with_tools(question: str, *, max_turns: int = 4) -> dict[str, Any]:
    """Run a transparent Bedrock Converse tool-calling loop.

    The model may request one or several tools. Python executes only the allow-listed
    read-only functions above and returns their JSON results to the model.
    """
    if not question.strip():
        raise ValueError("question cannot be empty")

    settings = get_settings()
    model_id = settings.bedrock_text_model_id
    if not model_id:
        raise ValueError("BEDROCK_TEXT_MODEL_ID is not configured")

    system_prompt = (
        "Eres un asistente de investigación de operaciones. Para cualquier dato factual sobre "
        "clientes, incidentes, estado de servicios o SLA debes usar las herramientas disponibles; "
        "no lo inventes ni lo deduzcas de memoria. Resume solo lo que devuelvan las tools. "
        "Si un dato no está disponible, dilo explícitamente."
    )
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": [{"text": question}]}
    ]
    tool_trace: list[dict[str, Any]] = []
    model_trace: list[dict[str, Any]] = []
    total_usage: dict[str, int] = {}

    for turn in range(1, max_turns + 1):
        response = bedrock_runtime().converse(
            modelId=model_id,
            system=[{"text": system_prompt}],
            messages=messages,
            toolConfig=TOOL_CONFIG,
            inferenceConfig={"temperature": 0.0, "maxTokens": 700},
        )
        message = response["output"]["message"]
        stop_reason = response.get("stopReason")
        usage = response.get("usage", {})
        _sum_usage(total_usage, usage)
        model_trace.append(
            {
                "turn": turn,
                "stop_reason": stop_reason,
                "usage": usage,
                "content": message.get("content", []),
            }
        )
        messages.append(message)

        tool_uses = [
            block["toolUse"]
            for block in message.get("content", [])
            if "toolUse" in block
        ]

        if not tool_uses:
            answer = "\n".join(
                block["text"]
                for block in message.get("content", [])
                if "text" in block
            ).strip()
            return {
                "answer": answer,
                "tool_trace": tool_trace,
                "model_trace": model_trace,
                "messages": messages,
                "usage": total_usage,
                "model_id": model_id,
                "system_prompt": system_prompt,
            }

        tool_results = []
        for tool_use in tool_uses:
            tool_name = tool_use["name"]
            tool_input = tool_use.get("input", {})
            try:
                result = execute_tool(tool_name, tool_input)
                status = "success"
            except Exception as exc:
                result = {"error": str(exc)}
                status = "error"

            tool_trace.append(
                {
                    "turn": turn,
                    "tool_use_id": tool_use["toolUseId"],
                    "name": tool_name,
                    "input": tool_input,
                    "result": result,
                    "status": status,
                }
            )
            tool_results.append(
                {
                    "toolResult": {
                        "toolUseId": tool_use["toolUseId"],
                        "content": [{"json": result}],
                        "status": status,
                    }
                }
            )

        messages.append({"role": "user", "content": tool_results})

    raise RuntimeError(f"Tool-calling loop exceeded max_turns={max_turns}")
