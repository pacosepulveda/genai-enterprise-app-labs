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

## Qué tiene que hacer el alumno

1. Al comenzar M02, crea o activa la rama del módulo:

```bash
git fetch --tags
git switch -c curso-m02 m02-complete
```

Si ya existe: `git switch curso-m02`.
2. Abre `enterprise_ticket_classifier.ipynb` con **Python (GenAI Course)** y ejecuta todas las celdas en orden.
3. Inspecciona el dataset, el split train/test, la matriz de confusión, las métricas y los términos con mayor peso.
4. Prueba al menos un ticket ambiguo y otro con vocabulario poco representado; compara las probabilidades.
5. Arranca `ticket_classifier_app.py` con Streamlit y repite una prueba desde la GUI.
6. No necesitas AWS en esta práctica. El objetivo es poder explicar qué ha aprendido el clasificador y dónde falla, no maximizar la accuracy.
