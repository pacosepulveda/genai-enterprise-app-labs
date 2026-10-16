# M01-P01 — Exploring Bedrock LLMs

En esta práctica se utiliza **Amazon Bedrock Converse API** directamente desde Python para observar cómo se construye una petición a un LLM y cómo cambian los resultados al modificar los parámetros principales.

La práctica está diseñada para cambiar **una variable cada vez** y evitar conclusiones confusas.

## Objetivos

Al finalizar la práctica podrás:

- identificar `modelId`, `system`, `messages` e `inferenceConfig` en una petición Converse;
- observar tokens de entrada y salida, latencia y motivo de finalización;
- comparar respuestas con y sin `system prompt`;
- observar el efecto probabilístico de `temperature`;
- distinguir entre una instrucción de longitud y el límite duro `maxTokens`;
- comprobar cómo el contexto empresarial modifica una respuesta;
- entender la diferencia entre latencia total y tiempo hasta el primer fragmento en streaming;
- detectar afirmaciones plausibles pero no sustentadas por los datos de entrada.

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
5. En cada experimento observa qué variable se mantiene fija y cuál cambia.
6. Completa el mini-reto final y revisa si la salida contiene información que no aparecía en la incidencia.

## Experimentos

### A — `system prompt`

Se mantienen los mismos datos, formato, temperatura y límite de salida. Solo cambia el `system prompt` para observar cómo afecta al rol, la prudencia y la separación entre hechos e hipótesis.

### B — `temperature`

Se ejecuta tres veces la misma tarea con `temperature=0.0` y tres veces con `temperature=0.8`. Los resultados se muestran en una tabla compacta para comparar estabilidad y variación.

### C — `maxTokens`

Se compara un límite pequeño con uno amplio sobre la misma tarea. El objetivo es observar la diferencia entre:

```text
stopReason = max_tokens
```

y:

```text
stopReason = end_turn
```

### D — contexto

Se formula la misma pregunta con los mismos parámetros, primero sin información interna y después añadiendo manualmente un procedimiento corporativo.

La idea que reutilizaremos posteriormente en RAG es:

```text
pregunta + contexto relevante → respuesta fundamentada
```

### E — streaming

Se utiliza `converse_stream()` y se muestran:

- tiempo hasta que el stream está disponible;
- tiempo hasta el primer fragmento de texto;
- tiempo total del cliente;
- métricas de Bedrock;
- tokens;
- `stopReason`;
- número de reintentos HTTP reportado por boto3.

## Mini-reto final

El modelo debe preparar una actualización para un director de operaciones utilizando únicamente los hechos conocidos de la incidencia. La acción recomendada puede ser una propuesta, pero no debe presentarse como un hecho observado.

El objetivo es detectar un riesgo frecuente en aplicaciones GenAI: una respuesta puede sonar profesional y convincente y, aun así, introducir información no sustentada.

## Qué debes observar

No busques solo si la respuesta parece buena. Fíjate también en:

- `inputTokens`;
- `outputTokens`;
- `totalTokens`;
- `latencyMs`;
- `stopReason`;
- diferencias entre latencia de Bedrock y tiempo medido por el cliente;
- diferencias de estilo y contenido entre configuraciones;
- posibles afirmaciones que no estén respaldadas por los datos de entrada.

La práctica utiliza un caso ficticio de soporte empresarial y realiza llamadas reales al modelo autorizado para el curso.
