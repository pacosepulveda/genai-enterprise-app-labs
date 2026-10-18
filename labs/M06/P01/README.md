# M06-P01 — RAG From Scratch

Práctica para construir un pipeline RAG completo sin frameworks, reutilizando el corpus empresarial de M05.

## Objetivos

- cargar los mismos 80 documentos usados en M05-P02;
- dividir documentos en chunks solapados preservando metadata;
- generar embeddings reales con Titan Text Embeddings V2;
- recuperar los chunks más próximos por similitud coseno;
- construir de forma explícita el contexto enviado al LLM;
- generar una respuesta fundamentada con citas `[S1]`, `[S2]`, etc.;
- observar tokens, latencia, retrieval, contexto, prompt y respuesta;
- evolucionar `Knowledge` desde retrieval semántico hasta RAG.

## Notebook

Abrir:

```text
labs/M06/P01/rag_from_scratch.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Corpus

Se reutiliza:

```text
data/knowledge/m05_enterprise_chunks.json
```

Aunque el nombre histórico del fichero contiene `chunks`, en M06 tratamos sus 80 registros como documentos fuente cortos. El notebook muestra de forma explícita cómo cada documento se convierte en uno o varios chunks para retrieval.

## Qué significa «from scratch» aquí

No significa implementar un modelo ni una base vectorial desde cero. Significa que no usamos todavía LangChain para ocultar el pipeline:

```text
documentos
→ chunking
→ embeddings
→ matriz vectorial
→ embedding de consulta
→ similitud coseno
→ top-k
→ contexto
→ prompt
→ LLM
→ respuesta con fuentes
```

En M06-P02 reconstruiremos este flujo con LangChain y añadiremos evaluación.

## Evolución de Knowledge

Después del notebook:

```bash
streamlit run app/Home.py
```

La página `Knowledge` mantiene el modo de búsqueda semántica de M05 y añade un modo RAG que permite inspeccionar:

- chunks recuperados y scores;
- contexto exacto enviado al modelo;
- respuesta generada;
- fuentes citadas;
- tokens y latencia.
