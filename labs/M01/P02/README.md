# M01-P02 — Structured Incident Analyzer

En esta práctica pasamos de una respuesta en **texto libre** a una salida **estructurada, validada y utilizable por código**.

Trabajaremos directamente con **Amazon Bedrock Converse API**, JSON Schema y Pydantic. Después utilizaremos la misma idea desde la página **Analyze** de la aplicación Streamlit.

## Objetivos

Al finalizar la práctica podrás:

- explicar por qué el texto libre es cómodo para una persona pero incómodo para una aplicación;
- definir una estructura de salida con Pydantic;
- convertir esa estructura en JSON Schema;
- solicitar a Bedrock una salida que cumpla estrictamente el schema;
- convertir la respuesta JSON en un objeto Python validado;
- diferenciar hechos, hipótesis y recomendaciones;
- representar correctamente información ausente mediante `null`;
- observar tokens, latencia y `stopReason` también en structured output;
- utilizar la primera versión funcional de la capacidad **Analyze**.

## Requisitos

Debes haber completado:

- P00 — Preflight;
- M01-P01 — Exploring Bedrock LLMs.

Si tu sesión SSO ha caducado:

```bash
aws sso login --profile genai-course --use-device-code
```

## Materiales

- `structured_incident_analyzer.ipynb` — recorrido didáctico y transparente.
- `../../../app/pages/2_Analyze.py` — interfaz Streamlit.

## Ejecución

1. Abre `structured_incident_analyzer.ipynb`.
2. Selecciona el kernel **Python (GenAI Course)**.
3. Ejecuta las celdas en orden.
4. Observa primero el problema del texto libre.
5. Examina el modelo Pydantic y el JSON Schema generado.
6. Ejecuta la llamada de structured output.
7. Comprueba cómo Pydantic valida la respuesta.
8. Prueba el segundo caso, donde faltan datos.
9. Arranca Streamlit:

```bash
streamlit run app/Home.py
```

10. Abre la página **Analyze** y prueba varias incidencias.

## Primera compilación del schema

La primera vez que una cuenta utiliza un JSON Schema nuevo, Bedrock puede necesitar compilar la gramática asociada. Esa primera llamada puede tardar bastante más que las siguientes. Las ejecuciones posteriores con el mismo schema deberían ser mucho más rápidas.

## Qué debes observar

No te fijes solo en el texto generado. Comprueba también:

- que el JSON cumple siempre la misma estructura;
- que `affected_users` puede ser un entero o `null`;
- que `category` solo admite los valores definidos en el schema;
- que los hechos están separados de las hipótesis;
- que Pydantic rechaza estructuras que no cumplen el contrato;
- que la aplicación puede mostrar campos concretos sin tener que “entender” un párrafo libre.

## Idea clave

```text
Texto libre
   ↓
útil para leer
pero difícil de automatizar

Structured output
   ↓
JSON Schema
   ↓
Pydantic
   ↓
datos que una aplicación puede utilizar
```

Esta será la primera versión real de la capacidad **Analyze** del Enterprise GenAI Assistant.
