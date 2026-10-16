import pandas as pd
import streamlit as st

from enterprise_genai.classical_ml import (
    LABEL_DISPLAY,
    active_tfidf_terms,
    build_ticket_classifier,
    load_ticket_dataset,
    predict_with_probabilities,
    top_terms_by_class,
)


st.set_page_config(page_title="Ticket Classifier Explorer", page_icon="🎫", layout="wide")

st.title("🎫 Enterprise Ticket Classifier")
st.caption("M02-P01 · TF-IDF + Logistic Regression · modelo clásico ejecutado localmente")

DATASET_PATH = "data/tickets/m02_tickets.csv"


@st.cache_resource
def train_model():
    df = load_ticket_dataset(DATASET_PATH)
    model = build_ticket_classifier()
    model.fit(df["text"], df["category"])
    return df, model


df, model = train_model()

st.info(
    "En el notebook evaluamos el modelo con train/test. Para esta interfaz, una vez evaluado, "
    "lo reentrenamos con los 80 tickets etiquetados disponibles."
)

example_ticket = (
    "No puedo completar el acceso al CRM porque el código MFA no llega al móvil."
)

ticket = st.text_area(
    "Ticket",
    value=example_ticket,
    height=120,
    help="Modifica el texto para observar cómo cambian la clase y las probabilidades.",
)

if st.button("Clasificar ticket", type="primary", use_container_width=True):
    if not ticket.strip():
        st.warning("Introduce un ticket antes de clasificar.")
        st.stop()

    probabilities = predict_with_probabilities(model, ticket)
    best = probabilities.iloc[0]
    predicted = str(best["category"])
    confidence = float(best["probability"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Categoría", LABEL_DISPLAY[predicted])
    col2.metric("Valor interno", predicted)
    col3.metric("Probabilidad máxima", f"{confidence:.1%}")

    if confidence < 0.55:
        st.warning(
            "Confianza baja: este ticket podría ser ambiguo o diferente de los ejemplos de entrenamiento."
        )
    else:
        st.success("El modelo muestra una preferencia clara por una categoría.")

    st.subheader("Probabilidades por categoría")
    chart_df = probabilities.set_index("label")[["probability"]]
    st.bar_chart(chart_df)

    st.dataframe(
        probabilities[["label", "category", "probability"]].style.format(
            {"probability": "{:.1%}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("🔎 Abrir la caja: términos TF-IDF activos en este ticket"):
        active = active_tfidf_terms(model, ticket)
        if active.empty:
            st.warning(
                "Ninguna palabra del ticket aparece en el vocabulario aprendido. "
                "El modelo está fuera de su zona de conocimiento léxico."
            )
        else:
            st.dataframe(
                active.style.format({"tfidf": "{:.3f}"}),
                use_container_width=True,
                hide_index=True,
            )

    with st.expander("🧠 Términos con mayor peso para la categoría predicha"):
        terms = top_terms_by_class(model, n=12)
        terms = terms[terms["category"] == predicted][["term", "weight"]]
        st.dataframe(
            terms.style.format({"weight": "{:.3f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("📦 Datos del modelo"):
        vectorizer = model.named_steps["tfidf"]
        classifier = model.named_steps["classifier"]
        st.write(
            {
                "training_tickets": len(df),
                "classes": list(classifier.classes_),
                "vocabulary_size": len(vectorizer.get_feature_names_out()),
                "algorithm": "LogisticRegression",
                "representation": "TF-IDF word unigrams + bigrams",
                "external_api_calls": 0,
            }
        )

st.divider()
st.caption(
    "Este modelo no entiende el lenguaje como un LLM: aprende asociaciones estadísticas entre "
    "términos TF-IDF y categorías a partir de ejemplos etiquetados."
)
