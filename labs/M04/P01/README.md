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

Todo se ejecuta localmente en el Codespace y utiliza CPU.

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

La generación de imágenes de alta calidad mediante un foundation model real se aborda posteriormente en M04-P03.

## Relación con Enterprise GenAI Assistant

Esta práctica es conceptual. La DCGAN de MNIST no se integra en la aplicación.

Sirve para entender el coste y las limitaciones de entrenar modelos generativos propios antes de ampliar la aplicación en:

- **M04-P02:** análisis multimodal `texto + imagen`;
- **M04-P03:** generación de activos visuales con un foundation model;
- **M04-P04:** integración de capacidades visuales en la aplicación.
