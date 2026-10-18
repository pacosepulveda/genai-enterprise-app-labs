# M04-P03 — Foundation Image Generation

Práctica de generación visual real mediante Amazon Bedrock.

## Objetivos

- invocar un foundation model de imagen con `InvokeModel`;
- inspeccionar el payload nativo y la respuesta Base64;
- comparar un prompt simple con otro más específico manteniendo la misma semilla;
- observar el efecto de cambiar la semilla;
- experimentar con `negative_prompt` y relación de aspecto;
- guardar metadatos de procedencia junto al activo generado;
- conectar la generación visual con la futura superficie `Create` de Enterprise GenAI Assistant.

## Modelo y región

El proyecto usa por defecto:

```text
BEDROCK_IMAGE_MODEL_ID=stability.stable-image-core-v1:1
BEDROCK_IMAGE_REGION=us-west-2
```

`Stable Image Core v1.1` se invoca mediante Bedrock Runtime `InvokeModel`. La región de imagen es independiente de `AWS_REGION`, que sigue utilizándose para las prácticas de texto.

Los valores están centralizados en `src/enterprise_genai/config.py` y pueden sobrescribirse mediante `.env`.

## Requisitos de acceso

La identidad utilizada por el alumno necesita permiso para `bedrock:InvokeModel` sobre el modelo configurado en `us-west-2`.

Como Stable Image Core es un modelo de terceros distribuido mediante AWS Marketplace, la cuenta debe tener habilitado el acceso al modelo. La activación inicial debe realizarse **una sola vez por cuenta** con una identidad que tenga permisos suficientes de Bedrock y AWS Marketplace. No es necesario conceder permisos de suscripción de Marketplace a los alumnos.

### Pre-activación recomendada por el instructor

Antes del curso, el instructor debe comprobar el modelo con una identidad administrativa o de preparación de laboratorio:

```bash
aws bedrock-runtime invoke-model \
  --region us-west-2 \
  --model-id stability.stable-image-core-v1:1 \
  --content-type application/json \
  --accept application/json \
  --body '{"prompt":"A blue circle on a white background","seed":42,"output_format":"png"}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/stable-core-response.json
```

Una respuesta correcta contendrá un array `images` con una imagen codificada en Base64. Después de esta activación, el rol de laboratorio solo necesita los permisos de inferencia previstos por el curso.

La primera invocación puede ser sensiblemente más lenta si coincide con la activación inicial del modelo. Las invocaciones posteriores suelen ser mucho más rápidas; la latencia real debe observarse en cada ejecución en lugar de asumir un valor fijo.

Si aparece `AccessDeniedException`, comprobar en este orden:

1. que la invocación se realiza en `us-west-2`;
2. que el rol permite `bedrock:InvokeModel` sobre `arn:aws:bedrock:us-west-2::foundation-model/stability.stable-image-core-v1:1`;
3. que el modelo ya fue activado en la cuenta por una identidad con permisos suficientes de AWS Marketplace;
4. que no existe una SCP u otra política que bloquee el modelo.

## Notebook

Abrir:

```text
labs/M04/P03/foundation_image_generation.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Salidas

Las imágenes y metadatos se guardan en:

```text
outputs/m04_p03/
```

La práctica termina creando un activo de formación interna y un JSON de procedencia con:

- indicador `synthetic`;
- propósito del activo;
- modelo;
- región;
- prompt;
- `negative_prompt`;
- semilla;
- relación de aspecto;
- formato;
- latencia.

## Límite funcional importante

Las imágenes de esta práctica son **contenido sintético**.

```text
Analyze
→ interpreta evidencia real

Create
→ produce contenido sintético
```

Una imagen generada puede utilizarse en formación, documentación o prototipos, pero nunca debe incorporarse a una investigación como si fuese evidencia de un incidente real.

## Relación con M04-P01 y M04-P04

M04-P01 mostraba el coste y las limitaciones de entrenar generadores propios.

M04-P03 cambia la pregunta:

```text
¿cómo entreno un generador?
        ↓
¿cómo integro una capacidad visual ya entrenada?
```

El helper `src/enterprise_genai/image_generation.py` creado para esta práctica se reutilizará en M04-P04 para implementar la superficie `Create` de la aplicación.
