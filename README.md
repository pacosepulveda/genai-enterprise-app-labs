# Enterprise GenAI Application Labs

Laboratorios de la segunda edición del curso **Desarrollo de Aplicaciones con IA Generativa**.

Este repositorio es a la vez:

- la plantilla de los entornos **GitHub Codespaces** del alumnado;
- el código base de las prácticas M01–M06;
- el proyecto incremental del **Enterprise GenAI Assistant**;
- un entorno que el alumno puede conservar y reutilizar al terminar el curso.

## Principios de diseño

1. **IA real por defecto.** Los LLM, embeddings y capacidades generativas se consumen desde Amazon Bedrock.
2. **Aprender leyendo, ejecutando y modificando.** El código necesario se entrega preparado; solo se escribe código cuando hacerlo aporta aprendizaje.
3. **Resultado observable.** Las prácticas combinan Jupyter, Streamlit y CLI según cuál sea la mejor forma de comprender el concepto.
4. **La GUI también enseña.** Siempre que sea útil se visualizan retrieval, chunks, tool calls, estado, métricas y otros procesos internos.
5. **La CLI se usa cuando aporta valor.** La configuración repetitiva se automatiza en Codespaces.
6. **Primero el problema, después la abstracción.** Structured output, LangChain, LangGraph, evaluación y controles se introducen cuando resuelven una necesidad visible.
7. **Ruta principal + ampliación.** La ruta principal debe ser accesible para perfiles con poca experiencia; los retos opcionales permiten profundizar.
8. **Sin mocks innecesarios.** Los sistemas empresariales ficticios se representan con datos y servicios locales reales; Bedrock no se simula salvo contingencia explícita.

## Aplicación transversal

Durante el curso se construye un **Enterprise GenAI Assistant** con tres capacidades:

- **Knowledge:** preguntas sobre conocimiento corporativo mediante RAG con fuentes.
- **Analyze:** análisis estructurado de tickets, correos y documentos.
- **Investigate:** investigación asistida de incidencias mediante RAG, herramientas y workflows.

La arquitectura objetivo utiliza Python, Jupyter, Streamlit, Amazon Bedrock, LangChain, LangGraph, un vector store local y una pequeña base SQLite que representa sistemas corporativos.

## Cómo empezar

La forma recomendada de trabajar es abrir el repositorio en **GitHub Codespaces**. El contenedor de desarrollo instala automáticamente las dependencias necesarias y prepara los datos locales del curso.

Una vez abierto:

1. revisa `docs/PREFLIGHT.md`;
2. configura la autenticación temporal con AWS;
3. ejecuta la tarea **Course: Check environment** de VS Code;
4. abre `labs/P00/preflight.ipynb`;
5. ejecuta la tarea **Course: Start Streamlit app** cuando una práctica utilice interfaz gráfica.

> No es necesario instalar software en el equipo local.

## Mapa de prácticas

El mapa definitivo se mantiene en [`docs/LAB-MAP.md`](docs/LAB-MAP.md).

## Estructura

```text
.devcontainer/   Entorno reproducible de Codespaces
.vscode/         Tareas y ajustes para reducir fricción de CLI
app/             Interfaz Streamlit del Enterprise GenAI Assistant
docs/            Arquitectura, preflight y documentación del curso
labs/            Prácticas guiadas M01–M06
scripts/         Utilidades de preparación y diagnóstico
src/             Código reutilizable de la aplicación
data/            Datos empresariales, conocimiento y evaluación
models/          Checkpoints locales de prácticas de ML/DL
tests/           Pruebas útiles de componentes críticos
```

## Importante

Este repositorio contiene material para el alumno, no soluciones duplicadas. Las prácticas están diseñadas para que el código de partida ya sea funcional y legible, con modificaciones pequeñas y deliberadas durante el laboratorio.
