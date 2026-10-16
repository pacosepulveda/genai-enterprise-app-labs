# Preflight del entorno

El objetivo del preflight es comprobar el entorno antes de comenzar las prácticas. No requiere instalar software en el equipo local.

## 1. Abrir el Codespace

Abre el repositorio con **Code > Codespaces > Create codespace on main**.

La creación ejecuta `.devcontainer/post-create.sh`, que instala las dependencias Python, usa PyTorch CPU y genera la base de datos local de ejemplo.

## 2. Autenticarse en AWS

El curso utilizará credenciales temporales mediante AWS IAM Identity Center. El instructor facilitará los datos de configuración del entorno (Start URL, región SSO, cuenta y rol/permission set).

Como Codespaces se ejecuta en una máquina remota, utilizamos el flujo **device code**: la URL de autorización se abre en el navegador del alumno, aunque la AWS CLI se esté ejecutando en el Codespace.

Configura el perfil una sola vez en el Codespace:

```bash
aws configure sso --use-device-code
```

Después inicia sesión:

```bash
aws sso login --profile <perfil> --use-device-code
```

La CLI mostrará una URL y un código. Abre la URL en tu navegador, introduce el código y completa el inicio de sesión.

Si utilizas un perfil distinto del predeterminado, expórtalo para el terminal actual o indícalo en `.env`:

```bash
export AWS_PROFILE=<perfil>
```

> No copies Access Keys permanentes al repositorio ni a notebooks.

## 3. Modelo y región

Copia `.env.example` a `.env` únicamente si el instructor te pide definir valores locales. Se proporcionarán los identificadores de los modelos habilitados para el curso.

Variables relevantes:

```text
AWS_REGION
AWS_PROFILE
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
- identidad AWS;
- acceso a Bedrock;
- invocación real del modelo de texto, si `BEDROCK_TEXT_MODEL_ID` está configurado.

También puedes ejecutar la misma comprobación desde terminal:

```bash
python scripts/check_environment.py
```

## 5. Notebook de preflight

Abre `labs/P00/preflight.ipynb` y selecciona el kernel **Python (GenAI Course)**. Ejecuta las celdas en orden.

## 6. Interfaz gráfica

Cuando una práctica lo indique, ejecuta la tarea:

**Course: Start Streamlit app**

Codespaces publicará el puerto 8501 y mostrará la interfaz del Enterprise GenAI Assistant.
