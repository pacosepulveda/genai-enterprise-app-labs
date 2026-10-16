"""Transparent classical ML helpers for M02-P01.

The goal is educational rather than production optimisation: students can inspect
TF-IDF features, Logistic Regression probabilities and the errors the model makes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


LABEL_ORDER = ["access", "network", "application", "security", "hardware"]
LABEL_DISPLAY = {
    "access": "Acceso e identidad",
    "network": "Red y conectividad",
    "application": "Aplicaciones",
    "security": "Seguridad",
    "hardware": "Hardware",
}


def load_ticket_dataset(path: str | Path = "data/tickets/m02_tickets.csv") -> pd.DataFrame:
    """Load the small labelled support-ticket dataset used in M02."""

    df = pd.read_csv(path)
    expected = {"ticket_id", "text", "category"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
    return df


def split_ticket_dataset(
    df: pd.DataFrame,
    *,
    test_size: float = 0.25,
    random_state: int = 1,
):
    """Create a reproducible, stratified train/test split."""

    return train_test_split(
        df["text"],
        df["category"],
        test_size=test_size,
        random_state=random_state,
        stratify=df["category"],
    )


def build_ticket_classifier() -> Pipeline:
    """Build the intentionally simple TF-IDF + Logistic Regression pipeline."""

    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    lowercase=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    C=4.0,
                    random_state=42,
                ),
            ),
        ]
    )


def predict_with_probabilities(model: Pipeline, text: str) -> pd.DataFrame:
    """Return every class probability, highest first."""

    probabilities = model.predict_proba([text])[0]
    classes = model.named_steps["classifier"].classes_
    result = pd.DataFrame({"category": classes, "probability": probabilities})
    result["label"] = result["category"].map(LABEL_DISPLAY)
    return result.sort_values("probability", ascending=False).reset_index(drop=True)


def top_terms_by_class(model: Pipeline, n: int = 10) -> pd.DataFrame:
    """Show terms with the strongest positive weights for each class."""

    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    feature_names = np.asarray(vectorizer.get_feature_names_out())

    rows: list[dict] = []
    for class_name, coefficients in zip(classifier.classes_, classifier.coef_):
        top_indices = np.argsort(coefficients)[-n:][::-1]
        for rank, feature_index in enumerate(top_indices, start=1):
            rows.append(
                {
                    "category": class_name,
                    "label": LABEL_DISPLAY.get(class_name, class_name),
                    "rank": rank,
                    "term": feature_names[feature_index],
                    "weight": float(coefficients[feature_index]),
                }
            )
    return pd.DataFrame(rows)


def active_tfidf_terms(model: Pipeline, text: str, n: int = 12) -> pd.DataFrame:
    """Show the strongest TF-IDF features that are active in one ticket."""

    vectorizer = model.named_steps["tfidf"]
    vector = vectorizer.transform([text]).tocoo()
    names = np.asarray(vectorizer.get_feature_names_out())

    if vector.nnz == 0:
        return pd.DataFrame(columns=["term", "tfidf"])

    pairs = sorted(
        zip(vector.col, vector.data),
        key=lambda item: item[1],
        reverse=True,
    )[:n]
    return pd.DataFrame(
        [{"term": names[index], "tfidf": float(value)} for index, value in pairs]
    )
