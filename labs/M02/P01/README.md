# M02-P01 — Enterprise Ticket Classifier

En esta práctica construiremos un clasificador de tickets **sin utilizar un LLM**. El objetivo es entender primero un enfoque clásico y medible antes de compararlo con Bedrock en M02-P02.

## Qué vamos a utilizar

- un dataset local de 80 tickets etiquetados;
- TF-IDF para convertir texto en números;
- Logistic Regression para clasificar;
- train/test split para medir con datos no usados durante el entrenamiento;
- precision, recall y F1;
- matriz de confusión;
- probabilidades por clase;
- pesos del modelo para inspeccionar qué términos ha aprendido;
- una pequeña interfaz Streamlit para probar tickets nuevos.

## Categorías

| Valor interno | Significado |
|---|---|
| `access` | Acceso e identidad |
| `network` | Red y conectividad |
| `application` | Aplicaciones |
| `security` | Seguridad |
| `hardware` | Hardware |

## Materiales

- `enterprise_ticket_classifier.ipynb`: recorrido didáctico completo.
- `ticket_classifier_app.py`: explorador interactivo del clasificador.
- `../../../data/tickets/m02_tickets.csv`: dataset etiquetado.
- `../../../src/enterprise_genai/classical_ml.py`: helpers reutilizables y transparentes.

## Ejecución

Abre:

```text
labs/M02/P01/enterprise_ticket_classifier.ipynb
```

y selecciona el kernel:

```text
Python (GenAI Course)
```

Esta práctica **no necesita AWS ni Bedrock**: todo el entrenamiento y la inferencia se ejecutan localmente en el Codespace.

Para iniciar la interfaz al final:

```bash
streamlit run labs/M02/P01/ticket_classifier_app.py
```

## Qué debes observar

No buscamos únicamente una cifra de accuracy. Queremos responder preguntas como:

- ¿Qué diferencia hay entre entrenamiento y test?
- ¿Cómo convierte TF-IDF una frase en un vector?
- ¿Qué significa precision, recall y F1?
- ¿Qué clases confunde el modelo?
- ¿Qué términos tienen mayor peso para cada categoría?
- ¿Qué significa una probabilidad de clasificación?
- ¿Qué ocurre con tickets ambiguos o con vocabulario poco visto?

El dataset es deliberadamente pequeño. Sirve para hacer visible el proceso; no representa un sistema de clasificación listo para producción.
