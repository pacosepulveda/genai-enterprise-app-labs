# M04-P04 — Visual GenAI Integration

Práctica de consolidación de las capacidades visuales de `Enterprise GenAI Assistant`.

## Objetivos

- validar que `Analyze` acepta texto + imagen como evidencia multimodal;
- validar que `Create` genera activos visuales reales mediante Amazon Bedrock;
- mantener separadas las rutas de evidencia y contenido sintético;
- inspeccionar metadatos de inferencia y procedencia desde la GUI;
- cerrar la evolución visual de la aplicación antes de continuar con M05.

## Qué se integra

Después de M04-P02 y M04-P03, la aplicación dispone de dos rutas visuales distintas:

```text
Analyze
texto + imagen real
        ↓
análisis estructurado
        ↓
evidencia / hipótesis / incertidumbre

Create
prompt + parámetros
        ↓
foundation model
        ↓
imagen sintética + procedencia
```

La separación es deliberada:

```text
imagen observada ≠ imagen generada
```

Una imagen producida por `Create` nunca debe utilizarse como evidencia de una incidencia.

## Ejecución

Desde la raíz del repositorio:

```bash
streamlit run app/Home.py
```

Abre la URL que exponga Codespaces para el puerto de Streamlit.

## Parte A — Revisar Home

La página principal debe mostrar cuatro capacidades:

- `Knowledge`;
- `Analyze`;
- `Create`;
- `Investigate`.

En M04, las dos capacidades funcionales que nos interesan son:

```text
Analyze → visión como evidencia
Create  → generación sintética
```

## Parte B — Validar Analyze

Abre `Analyze`.

Utiliza una incidencia y una captura de dashboard como en M04-P02.

Comprueba que la interfaz muestra:

- resumen;
- hechos observados;
- hipótesis;
- acciones recomendadas;
- evidencia visual;
- incertidumbres visuales;
- consistencia texto/imagen;
- revisión humana;
- JSON validado;
- métricas de inferencia.

No es necesario repetir todos los experimentos de M04-P02. Aquí solo comprobamos que la capacidad ya forma parte de la aplicación.

## Parte C — Validar Create

Abre `Create`.

La página permite configurar:

- propósito del activo;
- prompt;
- `negative_prompt`;
- relación de aspecto;
- seed;
- formato de salida.

Genera un activo con los valores por defecto.

La interfaz debe mostrar:

- la imagen generada;
- latencia;
- seed devuelta;
- dimensiones;
- `synthetic = true`;
- procedencia completa;
- request enviado al modelo;
- response metadata de Bedrock;
- descarga de imagen y JSON.

## Acceso al modelo

`Create` usa por defecto:

```text
BEDROCK_IMAGE_MODEL_ID=stability.stable-image-core-v1:1
BEDROCK_IMAGE_REGION=us-west-2
```

La cuenta debe tener activado previamente el modelo de Stability AI. Esa activación debe realizarla el instructor/administrador antes del curso.

El rol de los alumnos solo necesita el permiso de inferencia previsto para el modelo; no debe recibir permisos generales de suscripción a AWS Marketplace.

## Resultado esperado

Al terminar M04, la aplicación ha evolucionado desde:

```text
M01
Analyze(texto)
```

hasta:

```text
M04
Analyze(texto + imagen)
Create(prompt → imagen)
```

Esto cierra el bloque de visión generativa sin introducir todavía RAG, tools ni workflows, que se desarrollarán en módulos posteriores.

## Criterio de validación

M04-P04 queda validada si:

1. `Home` presenta claramente las cuatro capacidades;
2. `Analyze` sigue funcionando con evidencia visual;
3. `Create` genera una imagen real desde Streamlit;
4. `Create` etiqueta el resultado como sintético;
5. se muestran modelo, región, seed, latencia y procedencia;
6. no existe ningún flujo que convierta automáticamente una imagen generada en evidencia de `Analyze`.
