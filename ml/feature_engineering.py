"""
Feature preprocessing for product data using Scikit-Learn.
Combines numerical columns, one-hot encoded categories, and TF-IDF on product titles.
"""

from typing import Tuple, List
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

NUMERICAL_FEATURES: List[str] = [
    "rating",
    "review_count",
    "discount_percentage",
    "ram_gb",
    "storage_gb",
    "screen_size_inches",
    "is_prime"
]

CATEGORICAL_FEATURES: List[str] = [
    "category_name",
    "brand_name",
    "processor"
]

TEXT_FEATURE: str = "title"
TARGET_FEATURE: str = "price_tier"


def build_preprocessor() -> ColumnTransformer:
    num_pipeline = Pipeline([
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    text_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=60, stop_words="english", ngram_range=(1, 2)))
    ])

    return ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERICAL_FEATURES),
            ("cat", cat_pipeline, CATEGORICAL_FEATURES),
            ("text", text_pipeline, TEXT_FEATURE)
        ],
        remainder="drop"
    )


def prepare_features_and_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    clean_df = df.copy()

    if "category" in clean_df.columns and "category_name" not in clean_df.columns:
        clean_df.rename(columns={"category": "category_name"}, inplace=True)
    if "brand" in clean_df.columns and "brand_name" not in clean_df.columns:
        clean_df.rename(columns={"brand": "brand_name"}, inplace=True)

    clean_df["rating"] = clean_df["rating"].fillna(4.0)
    clean_df["review_count"] = clean_df["review_count"].fillna(10)
    clean_df["discount_percentage"] = clean_df["discount_percentage"].fillna(0.0)
    clean_df["ram_gb"] = clean_df["ram_gb"].fillna(0)
    clean_df["storage_gb"] = clean_df["storage_gb"].fillna(0)
    clean_df["screen_size_inches"] = clean_df["screen_size_inches"].fillna(0.0)
    clean_df["is_prime"] = clean_df["is_prime"].fillna(0)
    clean_df["processor"] = clean_df["processor"].fillna("Standard")
    clean_df["title"] = clean_df["title"].fillna("")

    X = clean_df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES + [TEXT_FEATURE]]
    y = clean_df[TARGET_FEATURE]
    return X, y
