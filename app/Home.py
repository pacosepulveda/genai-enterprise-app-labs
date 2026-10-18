import streamlit as st


st.set_page_config(page_title="Enterprise GenAI Assistant", page_icon="🧠", layout="wide")

st.title("🧠 Enterprise GenAI Assistant")
st.caption("Aplicación transversal del curso · de la primera llamada al LLM a un workflow empresarial controlado")

st.success(
    "M06-P05 · Prototipo integrado. Las capacidades construidas durante el curso ya pueden "
    "observarse como partes de un único sistema empresarial."
)

st.markdown("### Capacidades")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("💬 Knowledge")
    st.write("Conocimiento corporativo mediante embeddings, retrieval y RAG con fuentes visibles.")
    st.caption("M05 → M06")
    st.page_link("pages/1_Knowledge.py", label="Abrir Knowledge")

with col2:
    st.subheader("📄 Analyze")
    st.write("Análisis estructurado de incidencias, documentos y evidencia visual.")
    st.caption("M01 → M04 → M05")
    st.page_link("pages/2_Analyze.py", label="Abrir Analyze")

with col3:
    st.subheader("🎨 Create")
    st.write("Generación de activos visuales sintéticos con procedencia explícita.")
    st.caption("M04")
    st.page_link("pages/3_Create.py", label="Abrir Create")

with col4:
    st.subheader("🔧 Investigate")
    st.write("Datos empresariales, tools, RAG, LangGraph y aprobación humana.")
    st.caption("M06")
    st.page_link("pages/4_Investigate.py", label="Abrir Investigate")

st.divider()

left, right = st.columns([2, 1])
with left:
    st.markdown("### 🧭 Cierre del curso · Command Center")
    st.write(
        "M06-P05 ejecuta un caso 360º sobre una misma situación empresarial, combina Analyze, "
        "Knowledge e Investigate, muestra trazabilidad de extremo a extremo y añade comprobaciones "
        "básicas de control y prompt injection."
    )
    st.page_link(
        "pages/5_Command_Center.py",
        label="🚀 Abrir Enterprise GenAI Command Center",
    )

with right:
    st.markdown("### Principio de diseño")
    st.code(
        "IA flexible\ndonde aporta valor\n\n+\n\nsoftware determinista\ndonde importa el control\n\n+\n\npersonas\ndonde el riesgo lo exige",
        language=None,
    )

st.divider()
st.markdown("### Evolución M01 → M06")
st.code(
    "\n".join(
        [
            "M01  LLM + salidas estructuradas",
            "  ↓",
            "M02  ML clásico + LLM + routing híbrido",
            "  ↓",
            "M03  redes neuronales + atención bajo el capó",
            "  ↓",
            "M04  multimodalidad + generación visual",
            "  ↓",
            "M05  tokens + embeddings + documentos",
            "  ↓",
            "M06  RAG + LangChain + tools + LangGraph + aplicación integrada",
        ]
    ),
    language=None,
)

st.markdown("### Separaciones que mantenemos deliberadamente")
sep1, sep2, sep3 = st.columns(3)
with sep1:
    st.markdown("**Evidencia ≠ contenido sintético**")
    st.write(
        "Analyze interpreta información observada. Create genera contenido sintético y conserva su procedencia."
    )
with sep2:
    st.markdown("**LLM ≠ política empresarial**")
    st.write(
        "El modelo puede redactar y sintetizar; las reglas críticas de routing y aprobación permanecen en código."
    )
with sep3:
    st.markdown("**Prototipo ≠ producción**")
    st.write(
        "La aplicación tiene forma de sistema real, pero mantiene límites explícitos de seguridad, persistencia y operación."
    )

with st.expander("¿Por qué la aplicación enseña prompts, chunks, tokens, tool calls y estado?"):
    st.write(
        "Porque la observabilidad forma parte del objetivo del curso. Una respuesta útil no basta: "
        "queremos poder inspeccionar qué contexto recibió el modelo, qué herramientas se ejecutaron, "
        "qué ruta siguió el workflow y qué decisiones correspondieron al software o a una persona."
    )
