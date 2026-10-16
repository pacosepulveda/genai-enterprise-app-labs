# M04-P02 — Multimodal Incident Analyzer

Esta práctica hace evolucionar la capacidad `Analyze` de **Enterprise GenAI Assistant**.

En M01-P02:

```text
texto
→ Bedrock
→ salida estructurada
```

En M04-P02:

```text
texto + imagen
→ modelo multimodal de Bedrock
→ salida estructurada
```

## Objetivos

- enviar texto e imagen en una misma petición mediante Bedrock Converse;
- comprobar qué información aporta realmente una captura visual;
- separar hechos textuales, evidencia visual e hipótesis;
- detectar posibles contradicciones entre texto e imagen;
- mantener salida estructurada mediante JSON Schema + Pydantic;
- integrar la nueva capacidad en la página `Analyze` de Streamlit.

## Caso de uso

Trabajaremos con una incidencia de acceso VPN y una captura sintética de un dashboard.

El texto informa de usuarios afectados, pero la imagen añade señales visuales sobre el estado del backend de autenticación.

La pregunta principal es:

> ¿Qué puede aportar la imagen que no estaba ya en el texto?

## Entorno

Se ejecuta en el Codespace habitual.

Requiere:

- credenciales AWS activas;
- `BEDROCK_TEXT_MODEL_ID` configurado con un modelo multimodal compatible;
- acceso a Amazon Bedrock.

El modelo usado actualmente en el curso puede recibir imágenes mediante Converse.

## Notebook

Abrir:

```text
labs/M04/P02/multimodal_incident_analyzer.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Aplicación

Al finalizar, ejecutar:

```bash
streamlit run app/Home.py
```

En `Analyze`:

- sin adjunto se conserva el comportamiento de M01-P02;
- con adjunto se activa el análisis multimodal;
- se muestran evidencia visual, incertidumbres y consistencia texto/imagen.

## Regla importante

```text
evidencia visual
≠
causa raíz
```

Que un dashboard muestre un componente degradado permite registrar esa observación, pero no confirma por sí solo la causa del incidente.

## Reto opcional

Modifica la captura para crear una contradicción entre el texto y la imagen.

Por ejemplo:

```text
Texto:
"El servicio web funciona correctamente"

Imagen:
"CORPORATE WEB — DEGRADED"
```

Comprueba si el análisis marca la inconsistencia y recomienda revisión humana.
