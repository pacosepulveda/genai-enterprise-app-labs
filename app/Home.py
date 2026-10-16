import streamlit as st

st.set_page_config(page_title="Enterprise GenAI Assistant", page_icon="🧠", layout="wide")

st.title("Enterprise GenAI Assistant")
st.caption("Aplicación transversal del curso — entorno de aprendizaje")

st.info(
    "Esta interfaz crecerá durante M01–M06. El código de cada capacidad se construye "
    "primero de forma observable en los laboratorios y después se integra aquí."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("💬 Knowledge")
    st.write("Consulta de conocimiento corporativo mediante RAG y fuentes.")
    st.caption("Se construye principalmente en M05–M06.")
with col2:
    st.subheader("📄 Analyze")
    st.write("Análisis estructurado de tickets, correos y documentos.")
    st.caption("Empieza en M01 y se amplía en M05.")
with col3:
    st.subheader("🔧 Investigate")
    st.write("Investigación de incidencias mediante tools y workflows.")
    st.caption("Se construye en M06.")

with st.expander("¿Por qué esta aplicación muestra detalles técnicos?"):
    st.write(
        "Porque la interfaz también es una herramienta didáctica. A medida que avancemos podrá "
        "mostrar documentos recuperados, prompts, tool calls, estado de LangGraph, tokens y latencia."
    )
