# M05-P02 — Embeddings & Semantic Search

Práctica para pasar de **medir contexto** a **encontrar contexto relevante**.

## Objetivos

- generar embeddings reales con Amazon Bedrock;
- observar dimensión, norma y consumo de entrada de un vector;
- medir similitud coseno entre textos;
- comprobar que similitud semántica no es lo mismo que coincidencia literal de palabras;
- construir un índice vectorial en memoria sobre el corpus empresarial del curso;
- modificar `top-k` y filtros de metadata;
- visualizar una proyección 2D de los embeddings;
- convertir la superficie `Knowledge` de la aplicación en un explorador de recuperación semántica.

## Modelo

La práctica usa el modelo configurado en:

```text
BEDROCK_EMBEDDING_MODEL_ID
```

Por defecto:

```text
amazon.titan-embed-text-v2:0
```

Usamos vectores normalizados de **512 dimensiones**.

## Corpus

El corpus se encuentra en:

```text
data/knowledge/m05_enterprise_chunks.json
```

Contiene **80 documentos empresariales cortos** de VPN, identidad, web corporativa, red, endpoints, seguridad, bases de datos, workplace, observabilidad e incident management. Cada documento conserva metadata como:

- `service`;
- `source_type`;
- `audience`;
- identificador y título.

Este mismo corpus se reutiliza en M06. En M05 tratamos cada documento corto como una unidad semántica para centrarnos en embeddings y retrieval; en M06 introduciremos chunking, vector store y RAG sobre el mismo conocimiento.

## Notebook

Abrir:

```text
labs/M05/P02/embeddings_semantic_search.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Evolución de la aplicación

Después del notebook, iniciar:

```bash
streamlit run app/Home.py
```

La página `Knowledge` permite:

- escribir una consulta;
- elegir `top-k`;
- filtrar por servicio y tipo de fuente;
- inspeccionar score, contenido y metadata;
- abrir la caja para ver dimensiones, norma, tokens y latencia del embedding de consulta.

## Límite funcional

En esta práctica `Knowledge` **recupera documentos relevantes**, pero todavía **no genera una respuesta con un LLM**.

```text
M05-P02
consulta → embeddings → ranking → documentos

M06
consulta → chunking → retrieval → contexto → LLM → respuesta con fuentes
```

Mantener esta separación permite entender qué parte del futuro RAG corresponde realmente al retrieval.

## Qué tiene que hacer el alumno

1. Continúa en `curso-m05` y comprueba que AWS SSO está activo.
2. Abre `embeddings_semantic_search.ipynb` con **Python (GenAI Course)** y ejecuta las celdas en orden.
3. Observa dimensión, norma y tokens de los embeddings y compara similitud semántica con coincidencia literal.
4. Construye el índice de los 80 documentos y prueba distintas consultas, `top-k` y filtros de metadata.
5. Examina la proyección 2D como ayuda visual, sin confundirla con la geometría completa de 512 dimensiones.
6. Arranca `streamlit run app/Home.py`, abre **Knowledge** y repite una consulta desde la GUI inspeccionando score, contenido y metadata.
7. Recuerda que en P02 solo hacemos retrieval: no esperes todavía una respuesta generada por el LLM.
