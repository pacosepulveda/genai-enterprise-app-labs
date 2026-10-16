# Mapa definitivo de prácticas

Las prácticas están diseñadas para **leer, ejecutar, observar y modificar** código ya preparado. Los ejercicios que requieren escribir código se marcan explícitamente y son deliberadamente breves.

| ID | Práctica | Superficie principal | Qué hace el alumno | Aporta al producto |
|---|---|---|---|---|
| P00 | Preflight Codespaces + Bedrock | CLI + Jupyter | Verifica entorno y llamada real | Base técnica |
| M01-P01 | Exploring Bedrock LLMs | Jupyter | Modifica prompts/parámetros y compara | Cliente Bedrock |
| M01-P02 | Structured Incident Analyzer | Jupyter + Streamlit | Compara texto libre vs salida estructurada | Analyze v0.1 |
| M02-P01 | Enterprise Ticket Classifier | Jupyter + GUI | Entrena y explora errores/métricas | Conceptual |
| M02-P02 | Classical ML vs LLM | Jupyter + GUI | Compara ambos paradigmas | Opcional/router |
| M03-P01 | Neural Network Under the Hood | Jupyter | Observa forward/loss/backprop y parámetros | Conceptual |
| M03-P02 | Attention & Tiny Transformer | Jupyter | Visualiza atención y modifica secuencias | Conceptual |
| M04-P01 | VAE vs GAN vs Diffusion | Jupyter, CPU | Compara un VAE, entrena una DCGAN y observa el proceso de diffusion | Conceptual |
| M04-P01B | Diffusion in Action | Google Colab, **GPU T4+** | Observa una generación real paso a paso con Stable Diffusion | Conceptual / integración de modelo |
| M04-P02 | Multimodal Incident Analyzer | Jupyter + Streamlit | Amplía Analyze para trabajar con texto + imagen | Analyze multimodal |
| M04-P03 | Foundation Image Generation | Jupyter + GUI | Genera activos visuales con un foundation model y compara con entrenamiento propio | Create / GenAI visual real |
| M04-P04 | Visual GenAI Integration | Streamlit | Consolida análisis y generación visual en la aplicación | Analyze + Create |
| M05-P01 | Tokens & Generation | Jupyter | Observa tokenización/contexto/generación | Fundamento LLM |
| M05-P02 | Embeddings & Semantic Search | Jupyter + Streamlit | Explora similitud, top-k y metadata | Knowledge base |
| M05-P03 | Enterprise Document Analyzer | Streamlit + Jupyter | Analiza documentos con salida estructurada | Analyze |
| M06-P01 | RAG From Scratch | Jupyter + Streamlit | Inspecciona chunks, contexto y respuesta | Knowledge |
| M06-P02 | LangChain RAG & Evaluation | Jupyter + GUI | Compara configuraciones y mide retrieval | Knowledge fiable |
| M06-P03 | Tool Calling & Enterprise Data | Jupyter + Streamlit | Observa tool calls sobre SQLite | Investigate |
| M06-P04 | LangGraph Enterprise Workflow | Jupyter + Streamlit | Observa nodos, estado y routing | Investigate |
| M06-P05 | Enterprise GenAI Assistant | Streamlit | Integra, prueba y ataca el prototipo | Producto final |

## Regla de actividad del alumno

Cada práctica distinguirá tres tipos de acción:

- **OBSERVA:** ejecutar y entender qué ocurre.
- **MODIFICA:** cambiar parámetros, prompts, datos o una pequeña parte del código.
- **CONSTRUYE:** escribir una pieza breve cuando hacerlo sea didácticamente útil.

La mayoría del recorrido principal será **OBSERVA + MODIFICA**.

## Ruta avanzada

Los retos opcionales podrán incluir reranking, búsqueda híbrida, routing ML/LLM, nuevas tools, nuevos nodos LangGraph, FastAPI o comparación de modelos. Nunca serán requisito para completar la ruta principal.
