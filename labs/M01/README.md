# M01 — Primeras aplicaciones con IA generativa

## M01-P01 — Exploring Bedrock LLMs

**Superficie:** Jupyter.  
**Alumno:** OBSERVA + MODIFICA prompts, temperatura, longitud, contexto y system prompt.  
**Resultado:** llamadas reales a Bedrock con tokens, latencia, `stopReason` y streaming visibles.  
**Producto:** establece la capa transparente de acceso al LLM.

Materiales:

- [`P01/README.md`](P01/README.md)
- [`P01/exploring_bedrock_llms.ipynb`](P01/exploring_bedrock_llms.ipynb)

## M01-P02 — Structured Incident Analyzer

**Superficie:** Jupyter + Streamlit.  
**Alumno:** compara texto libre con structured output, inspecciona JSON Schema y Pydantic y prueba casos con información ausente.  
**Resultado:** analizador visual de una incidencia empresarial con salida validada y utilizable por código.  
**Producto:** primera versión funcional de `Analyze`.

Materiales:

- [`P02/README.md`](P02/README.md)
- [`P02/structured_incident_analyzer.ipynb`](P02/structured_incident_analyzer.ipynb)
- [`../../app/pages/2_Analyze.py`](../../app/pages/2_Analyze.py)
