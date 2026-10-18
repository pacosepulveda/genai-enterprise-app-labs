# M04-P01B — Diffusion in Action (GPU)

Demostración complementaria de M04-P01 para observar una generación real con un modelo de difusión latente ya entrenado.

> ⚠️ **Requiere GPU NVIDIA con CUDA.** Está pensada para ejecutarse en **Google Colab con una T4 o superior**. No debe ejecutarse como práctica CPU en GitHub Codespaces.

## Objetivos

- conectar el `forward diffusion` visto en M04-P01 con un proceso real de generación;
- observar cómo evolucionan los latentes durante el denoising;
- visualizar estados intermedios decodificándolos con el VAE del pipeline;
- comparar diferentes prompts, semillas y números de pasos;
- distinguir entre entrenar un generador propio e integrar un modelo ya entrenado.

## Entorno

1. Abre Google Colab.
2. Selecciona **Runtime / Entorno de ejecución → Change runtime type / Cambiar tipo de entorno de ejecución**.
3. Elige **T4 GPU** o una GPU superior.
4. Ejecuta el notebook desde el principio.

El notebook comprueba `torch.cuda.is_available()` y detiene la ejecución con un mensaje claro si no hay una GPU CUDA disponible.

## Notebook

```text
labs/M04/P01B/diffusion_in_action_colab.ipynb
```

## Qué se observa

```text
prompt
  ↓
representación de texto
  ↓
latentes inicialmente ruidosos
  ↓
denoising iterativo
  ↓
latentes progresivamente estructurados
  ↓
VAE decoder
  ↓
imagen visible
```

Los estados intermedios se decodifican únicamente para poder observarlos. Stable Diffusion trabaja durante el denoising en espacio latente; no genera una imagen RGB completa en cada paso.

## Relación con M04-P01

M04-P01 se mantiene como práctica principal CPU:

- VAE convolucional;
- DCGAN entrenada por el alumno;
- demostración conceptual de Diffusion.

M04-P01B añade una demostración GPU con un modelo de difusión real ya entrenado. No sustituye la GAN ni convierte Colab en el entorno principal del curso.

## Relación con Enterprise GenAI Assistant

Esta demo sigue siendo conceptual. La evolución funcional de la aplicación continúa en:

- **M04-P02:** `Analyze` acepta texto + imagen;
- **M04-P03:** generación visual mediante un foundation model vía API;
- **M04-P04:** integración de capacidades visuales en la aplicación.

## Qué tiene que hacer el alumno

1. Esta práctica es complementaria y se realiza únicamente si el instructor indica que hay una GPU disponible.
2. Mantén tu trabajo del módulo en `curso-m04`; el notebook se abre en Google Colab, no en el Codespace CPU.
3. Abre `diffusion_in_action_colab.ipynb` en Colab y selecciona una **T4 GPU** o superior antes de ejecutar nada.
4. Ejecuta el notebook desde el principio y verifica que CUDA está disponible.
5. Observa los estados intermedios del denoising y compara al menos un cambio de prompt, semilla o número de pasos.
6. No interpretes las imágenes intermedias como imágenes RGB que el modelo genera en cada paso: son visualizaciones de latentes decodificados para poder inspeccionarlos.
7. Si no hay GPU disponible, no intentes forzar esta práctica en Codespaces; continúa con M04-P02.
