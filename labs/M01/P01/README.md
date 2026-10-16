# M01-P01 — Exploring Bedrock LLMs

En esta práctica se utiliza **Amazon Bedrock Converse API** directamente desde Python para observar cómo se construye una petición a un LLM y cómo cambian los resultados al modificar los parámetros principales.

## Objetivos

Al finalizar la práctica podrás:

- identificar `modelId`, `system`, `messages` e `inferenceConfig` en una petición Converse;
- observar tokens de entrada y salida, latencia y motivo de finalización;
- comparar respuestas con y sin `system prompt`;
- experimentar con `temperature` y `maxTokens`;
- comprobar cómo el contexto proporcionado modifica la respuesta;
- visualizar una respuesta mediante streaming;
- comparar modelos si el instructor habilita un segundo modelo.

## Requisitos

Debes haber completado **P00 — Preflight** y tener configurado el perfil AWS:

```text
genai-course
```

Si la sesión de IAM Identity Center ha caducado, ejecuta:

```bash
aws sso login --profile genai-course --use-device-code
```

Puedes verificar la sesión con:

```bash
aws sts get-caller-identity --profile genai-course
```

## Ejecución

1. Abre `exploring_bedrock_llms.ipynb`.
2. Selecciona el kernel **Python (GenAI Course)**.
3. Ejecuta las celdas en orden.
4. Lee la petición que se muestra antes de la primera llamada a Bedrock.
5. Modifica únicamente los valores que propone cada experimento y vuelve a ejecutar la celda correspondiente.
6. Completa el mini-reto final con una observación propia.

## Qué debes observar

No busques solo si la respuesta parece buena. Fíjate también en:

- `inputTokens`;
- `outputTokens`;
- `totalTokens`;
- `latencyMs`;
- `stopReason`;
- diferencias de estilo y contenido entre configuraciones.

La práctica utiliza un caso ficticio de soporte empresarial y realiza llamadas reales al modelo autorizado para el curso.

## Reto opcional

La última sección permite comparar dos modelos si el instructor ha autorizado un segundo modelo y ha definido:

```text
BEDROCK_TEXT_MODEL_ID_ALT
```

Si no existe un segundo modelo autorizado, esa sección se omite automáticamente.
