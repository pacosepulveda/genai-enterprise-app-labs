# M05 — NLP generativo y representación semántica

M05 conecta los fundamentos de Transformers vistos en M03 con dos capacidades que necesitaremos para construir aplicaciones: **gestionar contexto** y **representar significado mediante embeddings**.

No repetimos los experimentos de temperatura, streaming o `maxTokens` de M01. El foco pasa a cómo entra el texto en el modelo y cómo preparar conocimiento empresarial para recuperación semántica.

## M05-P01 — Tokens, Context & Generation Budget

**Superficie:** Jupyter + Amazon Bedrock.  
**Alumno:** mide tokens reales con `CountTokens`, compara formatos, observa el crecimiento del historial y calcula presupuesto de contexto antes de inferencia.  
**Resultado:** tokens tratados como una variable observable de ingeniería, no solo como una definición teórica.  
**Puente:** prepara la necesidad de seleccionar información relevante antes de RAG.

## M05-P02 — Embeddings & Semantic Search

**Superficie:** Jupyter + Streamlit.  
**Alumno:** genera embeddings reales, consulta similitud, modifica `top-k` y filtros de metadata.  
**Resultado:** explorador visual de búsqueda semántica.  
**Producto:** base de `Knowledge`.

## M05-P03 — Enterprise Document Analyzer

**Superficie:** Streamlit + Jupyter.  
**Alumno:** analiza tickets, correos y documentos con resumen, clasificación, entidades y acciones estructuradas.  
**Producto:** amplía `Analyze` desde incidencias breves hacia documentos empresariales.
