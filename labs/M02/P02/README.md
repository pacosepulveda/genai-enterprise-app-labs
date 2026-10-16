# M02-P02 — Classical ML vs LLM

Compara el clasificador local de **M02-P01** con un LLM real en Amazon Bedrock.

## Objetivos

- clasificar los mismos tipos de tickets con ambos enfoques;
- comparar latencia, recursos y necesidad de entrenamiento;
- estudiar casos semánticamente difíciles;
- diferenciar ambigüedad de fuera de distribución;
- observar que un clasificador cerrado siempre debe elegir una clase;
- evitar comparar una probabilidad de Logistic Regression con una supuesta “confianza” numérica del LLM;
- introducir un posible router híbrido.

## Archivos

- `classical_ml_vs_llm.ipynb`: recorrido didáctico principal.
- `classical_ml_vs_llm_app.py`: interfaz Streamlit para comparación lado a lado.

## Requisito AWS

La práctica usa el perfil configurado en P00:

```bash
aws sso login --profile genai-course --use-device-code
```

## Ejecutar la interfaz

```bash
streamlit run labs/M02/P02/classical_ml_vs_llm_app.py
```

## Idea clave

No buscamos decidir que un enfoque sea universalmente mejor.

```text
ML clásico
→ rápido, local, interpretable, necesita datos etiquetados

LLM
→ flexible, semántico, no necesita entrenar este clasificador, pero usa API/tokens

arquitectura híbrida
→ una posibilidad cuando queremos explotar fortalezas distintas
```

El umbral de confianza del ejemplo híbrido es didáctico y debe validarse con datos reales antes de usarlo como política de producción.
