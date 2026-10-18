# M04-P01 — VAE vs GAN vs Diffusion

Práctica visual y CPU-only para comparar tres familias de generación de imágenes sin profundizar innecesariamente en todos sus parámetros internos.

## Objetivos

- entender a alto nivel qué diferencia a un VAE, una GAN y un modelo de difusión;
- entrenar un Convolutional VAE sobre MNIST 28×28 y observar reconstrucciones y muestras;
- entrenar una DCGAN pequeña pero suficientemente capaz como para producir dígitos reconocibles;
- observar la evolución visual de la GAN por epochs usando siempre el mismo ruido de entrada;
- demostrar el proceso de forward diffusion y qué objetivo aprende un denoiser;
- conectar estas técnicas con la decisión práctica de entrenar un modelo propio frente a consumir un foundation model.

## Entorno

Todo el notebook principal se ejecuta localmente en el Codespace y utiliza CPU.

La GAN puede tardar varios minutos. El notebook guarda checkpoints y muestras por epoch en:

```text
outputs/m04_p01/
```

Abrir:

```text
labs/M04/P01/vae_gan_diffusion.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Alcance de Diffusion

No se entrena un diffusion model completo desde cero. Se demuestra visualmente el proceso de añadir ruido, se construyen los pares `x_t / epsilon` que usaría el entrenamiento y se explica el proceso inverso.

Como complemento existe **M04-P01B — Diffusion in Action**, donde se utiliza Stable Diffusion 1.5 para observar una generación real paso a paso.

> ⚠️ **M04-P01B requiere GPU NVIDIA con CUDA y está pensada para Google Colab con T4 o superior.** No debe ejecutarse en el Codespace CPU.

```text
labs/M04/P01B/diffusion_in_action_colab.ipynb
```

La generación de imágenes empresariales mediante un foundation model de la arquitectura del curso se aborda posteriormente en M04-P03.

## Relación con Enterprise GenAI Assistant

Esta práctica es conceptual. La DCGAN de MNIST no se integra en la aplicación.

Sirve para entender el coste y las limitaciones de entrenar modelos generativos propios antes de ampliar la aplicación en:

- **M04-P02:** análisis multimodal `texto + imagen`;
- **M04-P03:** generación de activos visuales con un foundation model;
- **M04-P04:** integración de capacidades visuales en la aplicación.

## Qué tiene que hacer el alumno

1. Al comenzar M04, crea o activa la rama del módulo:

```bash
git fetch --tags
git switch -c curso-m04 m04-complete
```

Si ya existe: `git switch curso-m04`.
2. Abre `vae_gan_diffusion.ipynb` con **Python (GenAI Course)** y ejecuta las celdas en orden.
3. En VAE, compara reconstrucciones, muestras y el papel del espacio latente.
4. En GAN, observa la evolución por epochs y relaciona el generador y el discriminador con el resultado visual; no juzgues la práctica únicamente por la calidad final de los dígitos.
5. En Diffusion, sigue visualmente cómo se añade ruido y qué tendría que aprender el proceso inverso.
6. No ejecutes P01B en el Codespace CPU. Si el instructor realiza la demo GPU, sigue las instrucciones específicas de P01B.
7. Al terminar, debes poder explicar por qué en una aplicación empresarial puede ser más práctico integrar un foundation model que entrenar un generador propio.
