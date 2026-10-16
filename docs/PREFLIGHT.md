# Preflight del entorno

El objetivo del preflight es comprobar el entorno antes de comenzar las prácticas. No requiere instalar software en el equipo local.

## 1. Abrir el Codespace

Abre el repositorio con **Code > Codespaces > Create codespace on main**.

La creación ejecuta `.devcontainer/post-create.sh`, que instala las dependencias Python, usa PyTorch CPU y genera la base de datos local de ejemplo.

## 2. Autenticarse en Amazon Bedrock

Las prácticas utilizan una API key de Amazon Bedrock proporcionada para el curso. La clave se expone al Codespace mediante la variable de entorno:

```text
AWS_BEARER_TOKEN_BEDROCK
```

La clave nunca debe escribirse en notebooks, archivos Python, `.env` ni commits.

La opción recomendada para el curso es guardarla como **Codespaces secret** con el nombre `AWS_BEARER_TOKEN_BEDROCK`, limitado a este repositorio. De este modo se inyecta automáticamente en los Codespaces nuevos.

Para una prueba temporal también puede cargarse solo en el terminal actual:

```bash
export AWS_BEARER_TOKEN_BEDROCK='CLAVE_PROPORCIONADA'
```

Comprueba que existe sin mostrar su valor:

```bash
test -n "$AWS_BEARER_TOKEN_BEDROCK" && echo "TOKEN_OK" || echo "TOKEN_MISSING"
```

## 3. Modelo y región

El entorno del curso utiliza inicialmente:

```text
AWS_REGION=us-east-1
BEDROCK_TEXT_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

El identificador de texto corresponde a un inference profile de Bedrock. Las prácticas posteriores podrán utilizar modelos distintos para embeddings, visión o generación de imágenes.

Copia `.env.example` a `.env` únicamente si necesitas sobrescribir valores locales. No guardes nunca la API key en ese archivo.

Variables relevantes:

```text
AWS_REGION
BEDROCK_TEXT_MODEL_ID
BEDROCK_EMBEDDING_MODEL_ID
BEDROCK_IMAGE_MODEL_ID
```

## 4. Comprobación automática

Desde VS Code abre **Terminal > Run Task...** y ejecuta:

**Course: Check environment**

La comprobación informa de:

- versión de Python;
- librerías principales;
- base de datos local;
- presencia de la credencial de Bedrock;
- acceso al catálogo de modelos;
- invocación real del modelo de texto;
- resultado final `READY` si todo está preparado.

También puedes ejecutar la misma comprobación desde terminal:

```bash
python scripts/check_environment.py
```

## 5. Notebook de preflight

Abre `labs/P00/preflight.ipynb` y selecciona el kernel **Python (GenAI Course)**. Ejecuta las celdas en orden.

El notebook no muestra la clave. Solo comprueba que está disponible, consulta Bedrock e invoca el modelo de texto configurado.

## 6. Interfaz gráfica

Cuando una práctica lo indique, ejecuta la tarea:

**Course: Start Streamlit app**

Codespaces publicará el puerto 8501 y mostrará la interfaz del Enterprise GenAI Assistant.
