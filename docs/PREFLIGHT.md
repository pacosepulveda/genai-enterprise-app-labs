# Preflight del entorno

El objetivo del preflight es comprobar el entorno antes de comenzar las prácticas. No requiere instalar software en el equipo local.

## 1. Abrir el Codespace

Abre el repositorio con **Code > Codespaces > Create codespace on main**.

La creación ejecuta `.devcontainer/post-create.sh`, que instala las dependencias Python, usa PyTorch CPU y genera la base de datos local de ejemplo.

## 2. Configurar AWS IAM Identity Center

El curso utiliza usuarios de Microsoft Entra ID sincronizados con AWS IAM Identity Center. El acceso a AWS se realiza con credenciales temporales; no se proporcionan Access Keys ni API keys permanentes.

La primera vez que uses el Codespace ejecuta:

```bash
aws configure sso --use-device-code
```

Utiliza los siguientes valores cuando los solicite:

```text
SSO session name: genai-course
SSO start URL: https://d-9067e18660.awsapps.com/start
SSO region: us-east-1
SSO registration scopes: sso:account:access
Default client region: us-east-1
Profile name: genai-course
```

La CLI mostrará una URL y un código. Abre la URL en tu navegador e inicia sesión con el usuario del curso.

El Codespace conserva la configuración SSO cuando se detiene. Si la sesión temporal ha caducado, basta con volver a iniciar sesión:

```bash
aws sso login --profile genai-course --use-device-code
```

Comprueba la identidad obtenida:

```bash
aws sts get-caller-identity --profile genai-course
```

No guardes credenciales AWS en notebooks, archivos Python ni commits.

## 3. Modelo y región

El entorno del curso utiliza inicialmente:

```text
AWS_REGION=us-east-1
AWS_PROFILE=genai-course
BEDROCK_TEXT_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

El identificador de texto corresponde a un inference profile de Amazon Bedrock. Las prácticas posteriores podrán utilizar modelos distintos para embeddings, visión o generación de imágenes.

La configuración por defecto del proyecto ya utiliza esos valores. `.env.example` puede copiarse a `.env` únicamente cuando necesites sobrescribir ajustes locales; no contiene secretos.

## 4. Comprobación automática

Desde VS Code abre **Terminal > Run Task...** y ejecuta:

**Course: Check environment**

La comprobación informa de:

- versión de Python;
- librerías principales;
- base de datos local;
- identidad AWS obtenida mediante IAM Identity Center;
- acceso al catálogo de Amazon Bedrock;
- invocación real del modelo de texto;
- resultado final `READY` si todo está preparado.

También puedes ejecutar la misma comprobación desde terminal:

```bash
python scripts/check_environment.py
```

Si la sesión SSO ha caducado, ejecuta de nuevo:

```bash
aws sso login --profile genai-course --use-device-code
```

## 5. Notebook de preflight

Abre `labs/P00/preflight.ipynb` y selecciona el kernel **Python (GenAI Course)**. Ejecuta las celdas en orden.

El notebook comprueba la identidad temporal de AWS, consulta Bedrock e invoca el modelo de texto configurado.

## 6. Interfaz gráfica

Cuando una práctica lo indique, ejecuta la tarea:

**Course: Start Streamlit app**

Codespaces publicará el puerto 8501 y mostrará la interfaz del Enterprise GenAI Assistant.
