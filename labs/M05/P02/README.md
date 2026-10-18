# M05-P02 — Embeddings & Semantic Search

Práctica para pasar de **medir contexto** a **encontrar contexto relevante**.

## Objetivos

- generar embeddings reales con Amazon Bedrock;
- observar dimensión, norma y consumo de entrada de un vector;
- medir similitud coseno entre textos;
- comprobar que similitud semántica no es lo mismo que coincidencia literal de palabras;
- construir un pequeño índice vectorial en memoria;
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

Usamos vectores normalizados de **512 dimensiones** para que el alumno pueda trabajar con una representación real sin introducir todavía una base de datos vectorial.

## Corpus

El corpus didáctico se encuentra en:

```text
data/knowledge/m05_enterprise_chunks.json
```

Contiene fragmentos pequeños de documentación empresarial con metadata como:

- `service`;
- `source_type`;
- `audience`;
- identificador y título.

No es todavía un pipeline de chunking. En M06 construiremos recuperación y RAG a partir de documentos de forma más completa.

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

La página `Knowledge` ya no es un placeholder. Permite:

- escribir una consulta;
- elegir `top-k`;
- filtrar por servicio y tipo de fuente;
- inspeccionar score, contenido y metadata;
- abrir la caja para ver dimensiones, norma, tokens y latencia del embedding de consulta.

## Límite funcional

En esta práctica `Knowledge` **recupera fragmentos**, pero todavía **no genera una respuesta con un LLM**.

```text
M05-P02
consulta → embeddings → ranking → fragmentos

M06
consulta → retrieval → contexto → LLM → respuesta con fuentes
```

Mantener esta separación permite entender qué parte del futuro RAG corresponde realmente al retrieval.
