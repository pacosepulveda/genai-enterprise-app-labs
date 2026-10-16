# M04-P01 — Exploring VAE Latent Space

Práctica visual y CPU-only para entender cómo funciona un Variational Autoencoder (VAE).

## Objetivos

- observar el flujo `imagen → encoder → μ/logvar → z → decoder → reconstrucción`;
- entender qué significa `latent_dim`;
- separar reconstruction loss y KL divergence;
- visualizar directamente un espacio latente 2D;
- interpolar entre dos dígitos;
- comparar `latent_dim=2`, `4` y `8`;
- generar muestras desde `z ~ N(0, I)`.

## Entorno

Todo se ejecuta localmente en el Codespace. No usa AWS ni Bedrock.

Abrir:

```text
labs/M04/P01/exploring_vae_latent_space.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Nota

El dataset `load_digits` y la red son deliberadamente pequeños. El objetivo no es obtener imágenes de alta calidad, sino hacer visible el espacio latente y el mecanismo generativo.

Esta práctica es principalmente conceptual y no se integra directamente en Enterprise GenAI Assistant.
