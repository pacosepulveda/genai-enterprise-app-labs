# P00 — Preflight

Esta comprobación no es una práctica curricular. Su objetivo es asegurar que Codespaces, las dependencias, AWS y Amazon Bedrock están listos antes de comenzar M01.

Sigue este orden:

1. Lee `docs/PREFLIGHT.md`.
2. Configura una sola vez el perfil AWS `genai-course` mediante IAM Identity Center.
3. Comprueba tu identidad con `aws sts get-caller-identity --profile genai-course`.
4. Ejecuta **Course: Check environment** desde las tareas de VS Code o `python scripts/check_environment.py`.
5. Verifica que el resultado termina en `READY`.
6. Abre `preflight.ipynb`, selecciona el kernel **Python (GenAI Course)** y ejecuta todas las celdas.

En días posteriores no es necesario volver a configurar SSO. Si la sesión temporal ha caducado, ejecuta únicamente:

```bash
aws sso login --profile genai-course --use-device-code
```

No guardes credenciales AWS en notebooks, archivos del repositorio ni mensajes.
