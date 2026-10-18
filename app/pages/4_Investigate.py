import json

import pandas as pd
import streamlit as st

from enterprise_genai.enterprise_tools import (
    TOOL_CONFIG,
    database_overview,
    investigate_with_tools,
)


st.set_page_config(page_title="Investigate", page_icon="🔧", layout="wide")

st.title("🔧 Investigate — Tool Calling & Enterprise Data")
st.caption("M06-P03 · LLM → toolUse → funciones Python → SQLite read-only → toolResult → LLM")

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
    )
with c2:
    st.metric("Tablas", len(overview["tables"]))
    st.metric("Tools disponibles", len(TOOL_CONFIG["tools"]))

with st.expander("🧰 Tools disponibles"):
    for item in TOOL_CONFIG["tools"]:
        spec = item["toolSpec"]
        st.markdown(f"**`{spec['name']}`** — {spec['description']}")
        st.code(json.dumps(spec["inputSchema"]["json"], ensure_ascii=False, indent=2), language="json")

run = st.button("Investigar con tools", type="primary", use_container_width=True)

if run:
    if not question.strip():
        st.warning("Introduce una pregunta antes de continuar.")
        st.stop()

    with st.spinner("El modelo decide qué datos necesita, ejecuta tools permitidas y resume resultados..."):
        try:
            investigation = investigate_with_tools(question)
        except Exception as exc:
            st.error(f"No se pudo completar la investigación: {exc}")
            st.stop()

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

st.divider()
st.caption(
    "M06-P03 añade herramientas y datos estructurados. M06-P04 convertirá este patrón en un workflow "
    "LangGraph con estado, routing y aprobación humana."
)
