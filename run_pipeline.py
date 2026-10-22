"""
Main script to run the full pipeline:
1. Data collection / scraping
2. Database setup & SQL reports
3. Exploratory Data Analysis (EDA) charts
4. Model training & evaluation
5. Sample prediction test
"""

import sys
import json
import argparse
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scraper.amazon_scraper import AmazonScraper
from database.db_manager import DatabaseManager
from eda.eda_analyzer import EDAAnalyzer
from ml.train_model import PriceTierClassifierTrainer
from ml.predict import PriceTierPredictor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("Pipeline")


def run_full_pipeline(live: bool = False, count: int = 1200) -> None:
    print("\n" + "=" * 60)
    print("  E-Commerce Product Intelligence Pipeline")
    print("=" * 60)

    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    reports_dir = PROJECT_ROOT / "reports"
    figures_dir = reports_dir / "figures"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Data Collection
    print("\n[Step 1/5] Collecting product data...")
    scraper = AmazonScraper()
    products = scraper.collect_dataset(live=live, count=count)

    raw_json_path = raw_dir / "raw_scraped_products.json"
    raw_csv_path = raw_dir / "raw_scraped_products.csv"

    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)

    pd.DataFrame(products).to_csv(raw_csv_path, index=False)
    print(f"Collected {len(products)} products.")
    print(f"Saved raw files to {raw_dir}")

    # Step 2: Database & SQL
    print("\n[Step 2/5] Setting up SQLite database and running SQL analysis...")
    db_path = processed_dir / "amazon_products.db"
    db = DatabaseManager(str(db_path))
    inserted = db.insert_products(products)

    report_md_path = reports_dir / "sql_insights.md"
    db.generate_analytics_report(str(report_md_path))
    print(f"Inserted {inserted} rows into SQLite database.")
    print(f"SQL analysis report written to {report_md_path}")

    # Step 3: EDA Visualizations
    print("\n[Step 3/5] Generating EDA charts...")
    flat_df = db.get_all_products_df()
    eda = EDAAnalyzer(flat_df, output_dir=figures_dir)
    eda_results = eda.run_full_eda()
    print(f"Saved {len(eda_results['figures'])} charts to {figures_dir}")

    # Step 4: Model Training
    print("\n[Step 4/5] Training classification models...")
    trainer = PriceTierClassifierTrainer(random_state=42)
    ml_results = trainer.train_and_evaluate(flat_df)

    print(f"\nBest Model: {ml_results['best_model']}")
    print(f"Test Accuracy: {ml_results['best_metrics']['test_accuracy'] * 100:.2f}%")
    print(f"Weighted F1:   {ml_results['best_metrics']['test_f1_weighted']:.4f}")
    print(f"Model saved to: {ml_results['model_path']}")

    # Step 5: Test Prediction
    print("\n[Step 5/5] Testing sample prediction...")
    predictor = PriceTierPredictor(ml_results["model_path"])

    sample = {
        "title": "Lenovo IdeaPad Slim 3 15.6 inch FHD Laptop Intel Core i5 16GB RAM 512GB SSD",
        "category_name": "Laptops",
        "brand_name": "Lenovo",
        "processor": "Intel Core",
        "ram_gb": 16,
        "storage_gb": 512,
        "screen_size_inches": 15.6,
        "rating": 4.3,
        "review_count": 1200,
        "discount_percentage": 15.0,
        "is_prime": 1
    }

    pred = predictor.predict_one(sample)
    print(f"Sample Item:     {sample['title']}")
    print(f"Predicted Tier:  {pred['predicted_tier']} (Confidence: {pred['confidence_percentage']})")
    print(f"Estimated Range: {pred['estimated_price_range_inr']}")

    print("\n" + "=" * 60)
    print("  Pipeline completed successfully.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run E-Commerce Pipeline")
    parser.add_argument("--live", action="store_true", help="Try live Amazon scraping")
    parser.add_argument("--count", type=int, default=1200, help="Number of products (default: 1200)")
    args = parser.parse_args()

    run_full_pipeline(live=args.live, count=args.count)
