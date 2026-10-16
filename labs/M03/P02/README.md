# M03-P02 — Attention & Tiny Transformer

## Objetivo

Abrir el mecanismo de **self-attention** y visualizar cómo una secuencia pasa por:

```text
texto → tokens → IDs → embeddings → posiciones → Q/K/V → scores → softmax → attention → contexto
```

Después se entrena un **Tiny Transformer** de una sola cabeza y una sola capa para observar cómo cambian los pesos de attention y las representaciones contextuales cuando cambia el contexto.

## Superficie

Jupyter Notebook en GitHub Codespaces. Todo se ejecuta en CPU. No usa AWS ni Bedrock.

## Qué hace el alumno

- inspecciona tokenización, vocabulario y máscaras;
- observa embeddings de token y posición;
- abre las proyecciones Q, K y V;
- calcula y visualiza scores y softmax;
- interpreta una matriz de atención;
- entrena un Tiny Transformer sobre una tarea sintética simple;
- compara `vpn no funciona` y `vpn sí funciona`;
- observa cómo el mismo token `funciona` parte del mismo embedding y termina con una representación contextual distinta;
- modifica `d_model`, `ff_dim`, épocas y frases para observar cambios.

## Archivos

- `attention_tiny_transformer.ipynb` — práctica principal.

## Idea clave

La práctica no pretende construir un Transformer completo desde cero. El objetivo es hacer visible el mecanismo:

```text
representación inicial
→ relaciones Q/K
→ pesos de attention
→ combinación de V
→ representación contextual
```

Un peso de attention alto es una señal observable del mecanismo, pero no debe presentarse automáticamente como una explicación causal completa de una predicción.
