"""
Inference script to predict price tier for a product using the saved model.
"""

import sys
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from typing import Dict, Any, Union
import joblib
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "best_price_tier_model.joblib"

PRICE_TIER_RANGES = {
    "Budget": {"min_inr": 999, "max_inr": 25000, "description": "Entry-level segment (<= Rs 25,000)"},
    "Mid-Range": {"min_inr": 25001, "max_inr": 65000, "description": "Mid-tier segment (Rs 25,001 - 65,000)"},
    "Premium": {"min_inr": 65001, "max_inr": 250000, "description": "High-end / premium segment (> Rs 65,000)"}
}


class PriceTierPredictor:
    def __init__(self, model_path: Union[str, Path] = ARTIFACT_PATH):
        self.model_path = Path(model_path)
        self.pipeline = None
        self.classes = []
        self.model_name = ""
        self.load_model()

    def load_model(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. "
                "Run `python run_pipeline.py` first to train the model."
            )
        payload = joblib.load(self.model_path)
        self.pipeline = payload["pipeline"]
        self.classes = payload["target_classes"]
        self.model_name = payload["model_name"]

    def predict_one(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        df = pd.DataFrame([product_info])

        defaults = {
            "title": "",
            "category_name": "Laptops",
            "brand_name": "Unknown",
            "processor": "Standard",
            "rating": 4.0,
            "review_count": 50,
            "discount_percentage": 0.0,
            "ram_gb": 0,
            "storage_gb": 0,
            "screen_size_inches": 0.0,
            "is_prime": 1
        }
        for k, v in defaults.items():
            if k not in df.columns:
                if k == "category_name" and "category" in df.columns:
                    df["category_name"] = df["category"]
                elif k == "brand_name" and "brand" in df.columns:
                    df["brand_name"] = df["brand"]
                else:
                    df[k] = v

        predicted_tier = self.pipeline.predict(df)[0]
        probabilities = self.pipeline.predict_proba(df)[0]
        prob_dict = {cls: round(float(prob), 4) for cls, prob in zip(self.classes, probabilities)}

        confidence = prob_dict.get(predicted_tier, 0.0)
        tier_info = PRICE_TIER_RANGES.get(predicted_tier, {})

        return {
            "predicted_tier": predicted_tier,
            "confidence": confidence,
            "confidence_percentage": f"{confidence * 100:.1f}%",
            "class_probabilities": prob_dict,
            "estimated_price_range_inr": f"Rs {tier_info.get('min_inr', 0):,} - Rs {tier_info.get('max_inr', 0):,}",
            "tier_description": tier_info.get("description", ""),
            "model_used": self.model_name
        }


if __name__ == "__main__":
    predictor = PriceTierPredictor()
    test_sample = {
        "title": "Apple MacBook Pro 16 M3 Max 36GB RAM 1TB SSD",
        "category_name": "Laptops",
        "brand_name": "Apple",
        "processor": "Apple M3",
        "ram_gb": 36,
        "storage_gb": 1024,
        "screen_size_inches": 16.0,
        "rating": 4.8,
        "review_count": 2400,
        "discount_percentage": 5.0,
        "is_prime": 1
    }
    pred = predictor.predict_one(test_sample)
    print("Prediction Result:")
    for k, v in pred.items():
        print(f"  {k}: {v}")
