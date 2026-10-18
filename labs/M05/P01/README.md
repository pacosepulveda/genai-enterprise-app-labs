# M05-P01 — Tokens, Context & Generation Budget

Práctica para convertir el concepto de token en una variable observable de diseño de aplicaciones.

## Objetivos

- contar tokens con el modelo real del curso antes de inferencia;
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

Claude Haiku 4.5 se utiliza mediante un perfil de inferencia geográfico en `bedrock-runtime`. Para este modelo, el recuento previo de tokens se realiza mediante la API oficial de Anthropic expuesta por `bedrock-mantle`; el notebook encapsula ese detalle para centrar la práctica en el presupuesto de contexto.

La práctica usa la ventana de contexto del modelo configurado actualmente en el curso. Si el modelo cambia, el instructor actualizará la configuración del entorno antes de impartirla.

## Qué tiene que hacer el alumno

1. Al comenzar M05, crea o activa la rama del módulo:

```bash
git fetch --tags
git switch -c curso-m05 m05-complete
```

Si ya existe: `git switch curso-m05`.
2. Renueva AWS SSO si la sesión ha caducado.
3. Abre `tokens_context_budget.ipynb` con **Python (GenAI Course)** y ejecuta las celdas en orden.
4. Compara caracteres, palabras y tokens y observa cuánto añaden el formato, el `system prompt` y el historial.
5. Comprueba que el recuento previo coincide con `usage.inputTokens` en la llamada real cuando se cuenta la misma entrada.
6. Ejecuta el experimento de crecimiento del contexto y calcula cuánto margen debes reservar para la salida.
7. Al terminar, debes poder explicar por qué que un contexto “quepa” en la ventana no significa que sea una buena idea enviarlo completo.
