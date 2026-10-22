"""
Unit tests for the scraper regex, database operations, and model pipeline.
"""

import sys
import tempfile
from pathlib import Path
import pytest
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scraper.amazon_scraper import AmazonScraper
from scraper.data_generator import generate_seed_catalog
from database.db_manager import DatabaseManager
from ml.feature_engineering import prepare_features_and_target, build_preprocessor
from ml.train_model import PriceTierClassifierTrainer
from ml.predict import PriceTierPredictor


def test_spec_regex_extraction():
    """Tests regex extraction for specs from titles."""
    scraper = AmazonScraper()

    # Case 1: Laptop specs
    laptop_title = "HP Pavilion 15 Gaming Laptop Intel Core i5 16GB RAM 512GB SSD 15.6 inch FHD"
    specs = scraper.extract_specs_from_title(laptop_title)
    assert specs["ram_gb"] == 16
    assert specs["storage_gb"] == 512
    assert specs["screen_size_inches"] == 15.6
    assert specs["processor"] == "Intel Core"

    # Case 2: Apple Silicon & TB Storage
    apple_title = "Apple MacBook Pro 14 M2 Pro 1TB SSD 32GB RAM Liquid Retina Display"
    specs2 = scraper.extract_specs_from_title(apple_title)
    assert specs2["ram_gb"] == 32
    assert specs2["storage_gb"] == 1024
    assert "Apple M2" in specs2["processor"]


def test_data_generator_validity():
    """Checks that sample catalog generator returns valid products."""
    catalog = generate_seed_catalog(50)
    assert len(catalog) == 50

    sample = catalog[0]
    required_keys = [
        "asin", "title", "brand", "category", "current_price",
        "original_price", "discount_percentage", "rating", "review_count",
        "price_tier"
    ]
    for k in required_keys:
        assert k in sample
        assert sample[k] is not None

    assert sample["current_price"] > 0
    assert 1.0 <= sample["rating"] <= 5.0
    assert sample["price_tier"] in ["Budget", "Mid-Range", "Premium"]


def test_database_schema_and_insert(tmp_path):
    """Tests SQLite database creation and inserting rows."""
    tmp_db_path = tmp_path / "test_products.db"

    db = DatabaseManager(str(tmp_db_path))
    catalog = generate_seed_catalog(100)
    inserted = db.insert_products(catalog)
    assert inserted == 100

    df = db.get_all_products_df()
    assert len(df) == 100
    assert "category_name" in df.columns
    assert "brand_name" in df.columns

    # Verify SQL queries
    queries = db.parse_queries_file()
    assert len(queries) >= 5

    # Execute macro benchmark query
    macro_df = db.execute_query(queries["category_macro_benchmark"]["sql"])
    assert len(macro_df) > 0
    assert "total_products" in macro_df.columns

    # Execute window function query
    top_df = db.execute_query(queries["top_products_per_category"]["sql"])
    assert len(top_df) > 0
    assert "rank_in_category" in top_df.columns


def test_ml_pipeline_and_prediction():
    """Tests feature engineering, model training, and inference."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        catalog = generate_seed_catalog(150)
        df = pd.DataFrame(catalog)
        df.rename(columns={"category": "category_name", "brand": "brand_name"}, inplace=True)

        X, y = prepare_features_and_target(df)
        assert len(X) == 150
        assert len(y) == 150

        preprocessor = build_preprocessor()
        X_trans = preprocessor.fit_transform(X)
        assert X_trans.shape[0] == 150

        # Run trainer
        trainer = PriceTierClassifierTrainer(random_state=42)
        # Use small model set for fast testing
        trainer.models = {
            "Random Forest": trainer.models["Random Forest"]
        }
        results = trainer.train_and_evaluate(df)

        assert results["best_model"] == "Random Forest"
        assert results["best_metrics"]["test_accuracy"] >= 0.70

        # Predict with best model
        predictor = PriceTierPredictor(results["model_path"])
        sample_item = {
            "title": "Apple MacBook Air 13 M2 8GB RAM 256GB SSD",
            "category_name": "Laptops",
            "brand_name": "Apple",
            "processor": "Apple M2",
            "ram_gb": 8,
            "storage_gb": 256,
            "screen_size_inches": 13.6,
            "rating": 4.7,
            "review_count": 1500,
            "discount_percentage": 10.0,
            "is_prime": 1
        }
        prediction = predictor.predict_one(sample_item)
        assert prediction["predicted_tier"] in ["Budget", "Mid-Range", "Premium"]
        assert 0.0 <= prediction["confidence"] <= 1.0
