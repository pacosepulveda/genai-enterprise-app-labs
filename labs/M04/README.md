# M04 — Visión artificial y generación visual

El módulo introduce las principales familias de generación de imágenes con la profundidad necesaria para un desarrollador de aplicaciones y vuelve rápidamente a la aplicación transversal.

## M04-P01 — VAE vs GAN vs Diffusion

**Superficie:** Jupyter en Codespaces, CPU.  
**Alumno:** compara visualmente un Convolutional VAE, una DCGAN y el proceso de diffusion usando MNIST 28×28.  
**Resultado:** entiende las diferencias entre entrenar un generador propio y consumir un foundation model sin entrar en detalle innecesario de todos los parámetros internos.

La DCGAN se entrena en CPU durante varios minutos y guarda muestras/checkpoints por epoch.

## M04-P01B — Diffusion in Action

**Superficie:** Google Colab.  
**Requisito:** **GPU NVIDIA con CUDA; T4 o superior recomendada.** No está pensado para ejecutarse en el Codespace CPU.  
**Alumno:** carga Stable Diffusion 1.5, fija una semilla, observa latentes intermedios decodificados durante el denoising y compara prompts, semillas y número de pasos.  
**Resultado:** conecta el forward diffusion conceptual de M04-P01 con una generación real realizada por un modelo ya entrenado.

Esta demostración es complementaria: Colab no sustituye a Codespaces como entorno principal del curso.

## M04-P02 — Multimodal Incident Analyzer

**Superficie:** Jupyter + Streamlit.  
**Alumno:** amplía `Analyze` para aceptar texto e imagen, por ejemplo capturas de errores, dashboards o fotografías de activos.  
**Resultado:** análisis multimodal estructurado integrado en Enterprise GenAI Assistant.

## M04-P03 — Foundation Image Generation

**Superficie:** Jupyter + GUI.  
**Alumno:** genera activos visuales empresariales con un modelo real de Bedrock y experimenta con prompt y parámetros de generación.  
**Resultado:** comparación práctica entre entrenar un modelo propio y consumir un foundation model.

## M04-P04 — Visual GenAI Integration

**Superficie:** Streamlit.  
**Alumno:** consolida las capacidades visuales en la aplicación.  
**Resultado:** `Analyze` acepta evidencias visuales y la aplicación incorpora una capacidad `Create` para activos generados, manteniendo separados contenido sintético y evidencias reales.
