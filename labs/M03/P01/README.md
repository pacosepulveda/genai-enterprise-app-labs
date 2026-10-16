# M03-P01 — Neural Network Under the Hood

En esta práctica abrimos una red neuronal pequeña para observar el ciclo de aprendizaje sin ocultarlo detrás de una API.

## Objetivos

Al finalizar podrás explicar y observar directamente:

- parámetros entrenables;
- `forward pass`;
- activaciones y logits;
- `loss`;
- `backward()` y gradientes;
- `optimizer.step()`;
- evolución de train y validation;
- frontera de decisión;
- efecto del `learning rate`;
- efecto de la capacidad de la red;
- sobreajuste;
- predicciones cercanas a la frontera.

## Entorno

La práctica se ejecuta completamente en CPU dentro del Codespace. No utiliza AWS ni Bedrock.

Abre:

```text
labs/M03/P01/neural_network_under_the_hood.ipynb
```

Selecciona el kernel:

```text
Python (GenAI Course)
```

## Dataset

Usamos un problema sintético 2D basado en `make_moons`. Es deliberadamente pequeño porque queremos visualizar los datos, la frontera de decisión y el proceso de aprendizaje.

No es un benchmark de producción.

## Idea central

```text
entrada
  ↓
forward
  ↓
logit / probabilidad
  ↓
loss
  ↓
backward
  ↓
gradientes
  ↓
optimizer.step()
  ↓
parámetros actualizados
```

El alumno no implementa autograd ni backpropagation desde cero. El objetivo es ver qué hace PyTorch y relacionar cada operación con su función.

## Experimentos

El notebook incluye experimentos guiados sobre:

- learning rates demasiado pequeños, razonables y excesivos;
- redes con distinta cantidad de neuronas ocultas;
- un escenario artificial con pocas muestras y etiquetas ruidosas para hacer visible el sobreajuste.

Modifica los valores indicados al final y compara las curvas y métricas.