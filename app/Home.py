import streamlit as st

st.set_page_config(page_title="Enterprise GenAI Assistant", page_icon="🧠", layout="wide")

st.title("Enterprise GenAI Assistant")
st.caption("Aplicación transversal del curso — entorno de aprendizaje")

st.info(
    "Esta interfaz crece durante M01–M06. El código de cada capacidad se construye "
    "primero de forma observable en los laboratorios y después se integra aquí."
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("💬 Knowledge")
    st.write("Consulta de conocimiento corporativo mediante RAG y fuentes.")
    st.caption("Se construye principalmente en M05–M06.")
with col2:
    st.subheader("📄 Analyze")
    st.write("Análisis estructurado de texto y evidencias visuales.")
    st.caption("M01 introduce texto; M04 añade multimodalidad.")
with col3:
    st.subheader("🎨 Create")
    st.write("Generación de activos visuales sintéticos con modelos de Bedrock.")
    st.caption("Se incorpora en M04 y mantiene procedencia explícita.")
with col4:
    st.subheader("🔧 Investigate")
    st.write("Investigación de incidencias mediante tools y workflows.")
    st.caption("Se construye en M06.")

st.divider()
st.markdown("### Separación importante en M04")
left, right = st.columns(2)
with left:
    st.markdown("**Analyze → evidencia**")
    st.write(
        "Una captura, dashboard o fotografía puede aportar información observada a una incidencia."
    )
with right:
    st.markdown("**Create → contenido sintético**")
    st.write(
        "Una imagen generada sirve para formación, documentación o prototipos, pero no como evidencia real."
    )

with st.expander("¿Por qué esta aplicación muestra detalles técnicos?"):
    st.write(
        "Porque la interfaz también es una herramienta didáctica. A medida que avancemos podrá "
        "mostrar documentos recuperados, prompts, tool calls, estado de LangGraph, tokens y latencia."
    )
