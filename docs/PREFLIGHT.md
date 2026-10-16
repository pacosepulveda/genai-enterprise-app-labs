# Preflight del entorno

El objetivo del preflight es comprobar el entorno antes de comenzar las prácticas. No requiere instalar software en el equipo local.

## 1. Abrir el Codespace

Abre el repositorio con **Code > Codespaces > Create codespace on main**.

La creación ejecuta `.devcontainer/post-create.sh`, que instala las dependencias Python, usa PyTorch CPU y genera la base de datos local de ejemplo.

Espera a que termine la preparación antes de empezar. Si VS Code muestra temporalmente un aviso indicando que el intérprete Python no es válido, selecciona **Python 3.11.x (`/usr/local/bin/python`)**. El entorno ya incluye las dependencias necesarias.

## 2. Configurar AWS IAM Identity Center

El curso utiliza usuarios de Microsoft Entra ID sincronizados con AWS IAM Identity Center. El acceso a AWS se realiza con credenciales temporales; no se proporcionan Access Keys ni API keys permanentes.

La primera vez que uses el Codespace ejecuta exactamente:

```bash
aws configure sso --profile genai-course --use-device-code
```

El parámetro `--profile genai-course` es importante: todos los materiales del curso esperan que el perfil se llame exactamente `genai-course`.

Utiliza estos valores cuando los solicite la CLI:

```text
SSO session name: genai-course
SSO start URL: https://d-9067e18660.awsapps.com/start
SSO region: us-east-1
SSO registration scopes: sso:account:access
Default client region: us-east-1
CLI default output format: deja el valor por defecto
Profile name: genai-course
```

La CLI mostrará una URL y un código. Abre la URL en tu navegador e inicia sesión con el usuario del curso. Solo debes ver la cuenta y el rol que el instructor ha asignado a las prácticas.

Comprueba la identidad obtenida:

```bash
aws sts get-caller-identity --profile genai-course
```

Si este comando devuelve tu usuario, la cuenta AWS y un ARN que contiene `AWSReservedSSO_GenAI-Course-Bedrock`, la autenticación está preparada.

### Días siguientes

El Codespace conserva la configuración SSO cuando se detiene por inactividad. No es necesario repetir `aws configure sso` cada día.

Si la sesión temporal ha caducado, vuelve a iniciar sesión con:

```bash
aws sso login --profile genai-course --use-device-code
```

No guardes credenciales AWS en notebooks, archivos Python, `.env`, repositorios ni mensajes.

## 3. Modelo y región

El entorno del curso utiliza inicialmente:

```text
AWS_REGION=us-east-1
AWS_PROFILE=genai-course
BEDROCK_TEXT_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

El identificador de texto corresponde a un inference profile de Amazon Bedrock. El permission set del curso limita qué modelos se pueden invocar. Las prácticas posteriores podrán habilitar de forma controlada modelos adicionales para embeddings, visión o generación de imágenes.

La configuración por defecto del proyecto ya utiliza esos valores. `.env.example` puede copiarse a `.env` únicamente cuando necesites sobrescribir ajustes locales; no contiene secretos.

## 4. Comprobación automática

Desde VS Code abre **Terminal > Run Task...** y ejecuta:

**Course: Check environment**

También puedes ejecutar la misma comprobación desde terminal:

```bash
python scripts/check_environment.py
```

La comprobación informa de:

- versión de Python;
- librerías principales;
- base de datos local;
- identidad AWS obtenida mediante IAM Identity Center;
- acceso al catálogo de Amazon Bedrock;
- invocación real del modelo de texto;
- resultado final `READY` si todo está preparado.

Si aparece un error de sesión expirada, ejecuta:

```bash
aws sso login --profile genai-course --use-device-code
```

Si aparece `ProfileNotFound`, comprueba primero:

```bash
aws configure list-profiles
```

Debe aparecer exactamente:

```text
genai-course
```

Si no aparece, repite la configuración inicial con:

```bash
aws configure sso --profile genai-course --use-device-code
```

## 5. Notebook de preflight

Abre `labs/P00/preflight.ipynb` y selecciona el kernel **Python (GenAI Course)**. Ejecuta todas las celdas en orden.

El notebook comprueba la identidad temporal de AWS, consulta Bedrock e invoca el modelo configurado. Si todas las celdas terminan correctamente, el entorno está listo para M01.

## 6. Interfaz gráfica

Cuando una práctica lo indique, ejecuta la tarea:

**Course: Start Streamlit app**

Codespaces publicará el puerto 8501 y mostrará la interfaz del Enterprise GenAI Assistant.

## Problemas frecuentes

- **El Codespace se ha detenido:** vuelve a abrirlo. La configuración SSO permanece guardada.
- **La sesión AWS ha caducado:** ejecuta `aws sso login --profile genai-course --use-device-code`.
- **`ProfileNotFound`:** el perfil no se creó con el nombre `genai-course`; consulta la sección 4.
- **Aviso de intérprete Python:** selecciona Python 3.11.x en `/usr/local/bin/python`.
- **`AccessDeniedException` al usar un modelo:** no cambies el modelo por tu cuenta. El curso utiliza una lista controlada de modelos autorizados.
