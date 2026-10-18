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

## Qué tiene que hacer el alumno

1. Al comenzar M06, crea o activa la rama del módulo:

```bash
git fetch --tags
git switch -c curso-m06 m06-complete
```

Si ya existe: `git switch curso-m06`.
2. Renueva AWS SSO si la sesión ha caducado.
3. Abre `rag_from_scratch.ipynb` con **Python (GenAI Course)** y ejecuta las celdas en orden.
4. Sigue cada etapa del pipeline y comprueba qué documentos/chunks se recuperan antes de mirar la respuesta final.
5. Inspecciona el contexto exacto y las citas `[S1]...` y verifica que el modelo no añade procedimientos que no estén en las fuentes.
6. Arranca `streamlit run app/Home.py`, abre **Knowledge → RAG from scratch** y repite la consulta desde la GUI.
7. Considera la práctica completada cuando puedes explicar qué parte corresponde a chunking, retrieval, contexto y generación.
