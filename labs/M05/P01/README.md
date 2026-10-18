# M05-P01 — Tokens, Context & Generation Budget

Práctica para convertir el concepto de token en una variable observable de diseño de aplicaciones.

## Objetivos

- usar `CountTokens` con el modelo real del curso;
- comprobar que palabras, caracteres y tokens no son equivalentes;
- observar el coste de formato, `system prompt` e historial;
- comparar el recuento previo con `usage.inputTokens` de una inferencia real;
- calcular un presupuesto de contexto reservando espacio para la salida;
- preparar el puente hacia embeddings, retrieval y RAG.

## Notebook

Abrir:

```text
labs/M05/P01/tokens_context_budget.ipynb
```

Kernel:

```text
Python (GenAI Course)
```

## Criterio de la práctica

M01 ya cubrió temperatura, límites de salida, contexto/no contexto y streaming. Aquí evitamos repetir esos experimentos.

La pregunta es:

```text
¿cuánto contexto estoy enviando,
qué lo hace crecer
y cómo puedo medirlo antes de inferencia?
```

La práctica usa la ventana de contexto del modelo configurado actualmente en el curso. Si el modelo cambia, el instructor actualizará la configuración del entorno antes de impartirla.
