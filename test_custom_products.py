"""
Quick test script to check predictions on sample product specs.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ml.predict import PriceTierPredictor

test_cases = [
    {
        "name": "Budget Smartphone",
        "specs": {
            "title": "Realme Narzo 50i 4GB RAM 64GB Storage",
            "category_name": "Smartphones",
            "brand_name": "Realme",
            "processor": "MediaTek Dimensity",
            "ram_gb": 4,
            "storage_gb": 64,
            "screen_size_inches": 6.5,
            "rating": 4.0,
            "review_count": 14200,
            "discount_percentage": 25.0,
            "is_prime": 1
        }
    },
    {
        "name": "Mid-Range Laptop",
        "specs": {
            "title": "Lenovo IdeaPad Slim 3 15.6 inch FHD Laptop Intel Core i3 8GB RAM 512GB SSD",
            "category_name": "Laptops",
            "brand_name": "Lenovo",
            "processor": "Intel Core",
            "ram_gb": 8,
            "storage_gb": 512,
            "screen_size_inches": 15.6,
            "rating": 4.2,
            "review_count": 890,
            "discount_percentage": 15.0,
            "is_prime": 1
        }
    },
    {
        "name": "Gaming Laptop",
        "specs": {
            "title": "ASUS ROG Strix G16 Gaming Laptop Intel Core i7 32GB RAM 1TB SSD",
            "category_name": "Laptops",
            "brand_name": "ASUS",
            "processor": "Intel Core",
            "ram_gb": 32,
            "storage_gb": 1024,
            "screen_size_inches": 16.0,
            "rating": 4.6,
            "review_count": 1250,
            "discount_percentage": 10.0,
            "is_prime": 1
        }
    },
    {
        "name": "Budget Wireless Earbuds",
        "specs": {
            "title": "boAt Airdopes 141 Bluetooth Wireless Earbuds",
            "category_name": "Headphones",
            "brand_name": "boAt",
            "processor": "Standard",
            "ram_gb": 0,
            "storage_gb": 0,
            "screen_size_inches": 0.0,
            "rating": 3.9,
            "review_count": 45000,
            "discount_percentage": 65.0,
            "is_prime": 1
        }
    }
]

predictor = PriceTierPredictor()

print("\nTesting sample predictions:")
for tc in test_cases:
    pred = predictor.predict_one(tc["specs"])
    print(f"\n- {tc['name']}")
    print(f"  Title:      {tc['specs']['title']}")
    print(f"  Predicted:  {pred['predicted_tier']} ({pred['confidence_percentage']})")
    print(f"  Price Band: {pred['estimated_price_range_inr']}")
