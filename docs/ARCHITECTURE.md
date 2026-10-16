# Arquitectura objetivo

## Producto

El proyecto transversal es un **Enterprise GenAI Assistant** para soporte y operaciones internas con tres capacidades:

- **Knowledge:** consulta de conocimiento corporativo mediante RAG y fuentes.
- **Analyze:** análisis estructurado de tickets, correos y documentos.
- **Investigate:** investigación de incidencias con RAG, herramientas, estado y aprobación humana.

## Arquitectura lógica

```text
                         USER
                           |
                           v
                  +-----------------+
                  |   Streamlit UI  |
                  +--------+--------+
                           |
          +----------------+-----------------+
          |                |                 |
          v                v                 v
      KNOWLEDGE          ANALYZE         INVESTIGATE
          |                |                 |
          v                |                 v
      LangChain            |             LangGraph
          |                |                 |
          v                v                 +-- Tools
         RAG          Bedrock LLM            +-- RAG
          |                                  +-- State
          v                                  +-- Approval
     Vector Store                                |
          |                                      |
          +------------------+-------------------+
                             v
                       AMAZON BEDROCK
                             |
                 +-----------+------------+
                 v           v            v
                LLM      Embeddings    Multimodal
```

## Decisiones deliberadas

### Codespaces como puesto de desarrollo

El entorno contiene Python, Jupyter, Streamlit, PyTorch, LangChain y LangGraph. La inferencia generativa se realiza en Bedrock.

### Streamlit sin FastAPI en la ruta principal

La UI llama directamente a una capa Python reutilizable. FastAPI puede añadirse como reto avanzado sin introducir una frontera HTTP innecesaria en la ruta principal.

### Datos empresariales locales

`data/enterprise.db` representa clientes, contratos, servicios, estado e incidencias. No es un mock de funciones: las tools consultan una base real. En una industrialización podría sustituirse por ServiceNow, Salesforce, SAP o APIs internas.

### Vector store local

El curso usa almacenamiento vectorial local para centrarse en retrieval y RAG. En producción podría sustituirse por OpenSearch, pgvector, Qdrant, Pinecone u otra plataforma.

### LangChain después de comprender RAG

M06-P01 construye el flujo de forma explícita. M06-P02 introduce LangChain cuando el alumno ya conoce qué abstrae.

### LangGraph solo cuando existe un workflow

Se introduce cuando `Investigate` necesita estado, routing, tools, decisiones y human-in-the-loop. No se usa para convertir una llamada sencilla en un grafo artificial.
