"""
Model training and evaluation script.
Compares Logistic Regression, Random Forest, and Gradient Boosting on price tier classification.
Saves the best model and generates confusion matrix and feature importance plots.
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
import joblib
import pandas as pd
import numpy as np

os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
    balanced_accuracy_score
)

from .feature_engineering import (
    build_preprocessor,
    prepare_features_and_target,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ARTIFACT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
FIGURES_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"


class PriceTierClassifierTrainer:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=random_state),
            "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=12, min_samples_split=4, random_state=random_state, n_jobs=-1),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=120, learning_rate=0.1, max_depth=5, random_state=random_state)
        }
        self.best_pipeline: Optional[Pipeline] = None
        self.best_model_name: str = ""
        self.classes: List[str] = ["Budget", "Mid-Range", "Premium"]

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

        X, y = prepare_features_and_target(df)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.20,
            random_state=self.random_state,
            stratify=y
        )
        logger.info(f"Split data: {len(X_train)} train, {len(X_test)} test")

        results = {}
        best_f1 = -1.0
        best_pipe = None
        best_name = ""

        preprocessor = build_preprocessor()

        for name, clf in self.models.items():
            logger.info(f"Training {name}...")
            pipe = Pipeline([
                ("preprocessor", preprocessor),
                ("classifier", clf)
            ])

            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)
            cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1_weighted")

            pipe.fit(X_train, y_train)
            y_pred = pipe.predict(X_test)

            acc = accuracy_score(y_test, y_pred)
            bal_acc = balanced_accuracy_score(y_test, y_pred)
            f1_macro = f1_score(y_test, y_pred, average="macro")
            f1_weighted = f1_score(y_test, y_pred, average="weighted")
            report_dict = classification_report(y_test, y_pred, output_dict=True)

            logger.info(f"[{name}] Test Acc: {acc:.4f} | Test F1: {f1_weighted:.4f}")

            results[name] = {
                "cv_f1_mean": round(float(cv_scores.mean()), 4),
                "cv_f1_std": round(float(cv_scores.std()), 4),
                "test_accuracy": round(float(acc), 4),
                "test_balanced_accuracy": round(float(bal_acc), 4),
                "test_f1_macro": round(float(f1_macro), 4),
                "test_f1_weighted": round(float(f1_weighted), 4),
                "classification_report": report_dict
            }

            if f1_weighted > best_f1:
                best_f1 = f1_weighted
                best_pipe = pipe
                best_name = name

        self.best_pipeline = best_pipe
        self.best_model_name = best_name
        logger.info(f"Selected best model: {self.best_model_name} (F1: {best_f1:.4f})")

        y_test_pred = self.best_pipeline.predict(X_test)
        cm_path = self._plot_confusion_matrix(y_test, y_test_pred)
        fi_path = self._plot_feature_importance()

        model_artifact_path = ARTIFACT_DIR / "best_price_tier_model.joblib"
        artifact_payload = {
            "model_name": self.best_model_name,
            "pipeline": self.best_pipeline,
            "target_classes": list(self.best_pipeline.classes_),
            "metrics": results[self.best_model_name]
        }
        joblib.dump(artifact_payload, model_artifact_path)
        logger.info(f"Saved model to {model_artifact_path}")

        return {
            "best_model": self.best_model_name,
            "best_metrics": results[self.best_model_name],
            "benchmark_comparison": results,
            "confusion_matrix_figure": str(cm_path),
            "feature_importance_figure": str(fi_path) if fi_path else None,
            "model_path": str(model_artifact_path)
        }

    def _plot_confusion_matrix(self, y_true: pd.Series, y_pred: np.ndarray) -> Path:
        labels = ["Budget", "Mid-Range", "Premium"]
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(
            cm_norm,
            annot=True,
            fmt=".1%",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            linewidths=0.5,
            ax=ax
        )
        ax.set_title(f"Confusion Matrix ({self.best_model_name})")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")

        plt.tight_layout()
        out_path = FIGURES_DIR / "06_ml_confusion_matrix.png"
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
        return out_path

    def _plot_feature_importance(self) -> Optional[Path]:
        clf = self.best_pipeline.named_steps["classifier"]
        if not hasattr(clf, "feature_importances_"):
            return None

        preprocessor = self.best_pipeline.named_steps["preprocessor"]
        feature_names = []
        feature_names.extend(NUMERICAL_FEATURES)

        cat_transformer = preprocessor.named_transformers_["cat"]
        onehot_encoder = cat_transformer.named_steps["onehot"]
        cat_encoded_names = onehot_encoder.get_feature_names_out(CATEGORICAL_FEATURES)
        feature_names.extend(cat_encoded_names)

        text_transformer = preprocessor.named_transformers_["text"]
        tfidf_vec = text_transformer.named_steps["tfidf"]
        text_names = [f"word_{w}" for w in tfidf_vec.get_feature_names_out()]
        feature_names.extend(text_names)

        importances = clf.feature_importances_
        if len(feature_names) != len(importances):
            return None

        feat_imp_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importances
        }).sort_values(by="importance", ascending=False).head(15)

        fig, ax = plt.subplots(figsize=(9, 6))
        sns.barplot(
            data=feat_imp_df,
            x="importance",
            y="feature",
            hue="feature",
            palette="viridis",
            ax=ax,
            legend=False
        )
        ax.set_title(f"Top 15 Features ({self.best_model_name})")
        ax.set_xlabel("Importance")
        ax.set_ylabel("Feature")

        plt.tight_layout()
        out_path = FIGURES_DIR / "07_ml_feature_importance.png"
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
        return out_path


if __name__ == "__main__":
    from ..database.db_manager import DatabaseManager
    db = DatabaseManager()
    df = db.get_all_products_df()
    trainer = PriceTierClassifierTrainer()
    res = trainer.train_and_evaluate(df)
    print(f"Trained. Best model: {res['best_model']}")
