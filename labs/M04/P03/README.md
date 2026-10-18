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

`Stable Image Core 1.0` se invoca mediante Bedrock Runtime `InvokeModel`. La región de imagen es independiente de `AWS_REGION`, que sigue utilizándose para las prácticas de texto.

Los valores están centralizados en `src/enterprise_genai/config.py` y pueden sobrescribirse mediante `.env`.

## Requisitos de acceso

La identidad utilizada por el alumno necesita permiso para `bedrock:InvokeModel` sobre el modelo configurado.

Como Stable Image Core es un modelo de terceros, la cuenta debe tener habilitado el acceso al modelo. En la primera utilización, Bedrock puede iniciar automáticamente la suscripción correspondiente. Si el rol de laboratorio no dispone de permisos de AWS Marketplace para realizar esa activación inicial, el instructor debe habilitar el modelo una vez en la cuenta antes del curso. Una vez habilitado, los alumnos solo necesitan los permisos de inferencia previstos por el entorno.

Si aparece `AccessDeniedException`, comprobar primero:

1. que el modelo está habilitado para la cuenta;
2. que la invocación se realiza en `us-west-2`;
3. que el rol permite `bedrock:InvokeModel`;
4. que no existe una SCP o política que bloquee el modelo.

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
