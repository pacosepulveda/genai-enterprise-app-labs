# M06-P02 — LangChain RAG & Evaluation

Práctica para reconstruir el pipeline RAG de M06-P01 con abstracciones de LangChain y, sobre todo, **medir la calidad del retrieval**.

## Objetivos

- representar el corpus como `Document` de LangChain;
- comparar dos estrategias de chunking;
- indexar chunks en Chroma usando embeddings reales de Bedrock;
- recuperar documentos con `top-k` configurable;
- aplicar filtros de metadata;
- medir `Hit Rate@k` y `MRR@k` sobre un benchmark etiquetado;
- construir una cadena LCEL `prompt → modelo → parser`;
- comparar qué simplifica LangChain y qué sigue siendo responsabilidad de la aplicación.

## Notebook

Abrir:

```text
labs/M06/P02/langchain_rag_evaluation.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Corpus y benchmark

Se reutilizan los mismos 80 documentos de M05/M06-P01:

```text
data/knowledge/m05_enterprise_chunks.json
```

La evaluación usa 10 consultas etiquetadas:

```text
data/evaluation/m06_rag_eval.json
```

Cada caso indica qué documento debería aparecer entre los resultados.

## Métricas

### Hit Rate@k

Porcentaje de consultas en las que el documento esperado aparece entre los `k` primeros resultados.

```text
Hit Rate@k = consultas con al menos un hit / total de consultas
```

### MRR@k

Premia que el primer documento relevante aparezca lo más arriba posible.

```text
rank 1 → 1.0
rank 2 → 0.5
rank 3 → 0.333...
no aparece → 0
```

El MRR es la media de esos reciprocal ranks.

## Comparaciones

El notebook evalúa:

- chunks grandes: 300 caracteres, overlap 40;
- chunks pequeños: 120 caracteres, overlap 30;
- distintos valores de `top-k`;
- retrieval global frente a filtro por `service`.

La intención no es declarar una configuración universalmente mejor, sino observar que retrieval es un componente que debe **medirse**.

## Qué añade LangChain

M06-P01 hacía visibles manualmente todas las piezas. Ahora usamos:

```text
Document
RecursiveCharacterTextSplitter
Chroma
Retriever / similarity search
ChatPromptTemplate
ChatBedrockConverse
LCEL
StrOutputParser
```

LangChain reduce código de integración, pero no decide por nosotros:

- cómo partir documentos;
- qué metadata conservar;
- qué `top-k` usar;
- qué filtros aplicar;
- cómo evaluar retrieval;
- qué prompt de grounding utilizar.

## Evolución de Knowledge

Después del notebook se añadirá un modo LangChain a `Knowledge` para ejecutar el mismo flujo desde la aplicación y mostrar métricas de evaluación junto al retrieval.
