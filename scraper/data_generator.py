"""
Sample data generator for Amazon electronics.
Generates realistic product listings for laptops, phones, headphones,
smartwatches, and tablets for local development and testing.
"""

import random
from typing import List, Dict, Any

CATEGORIES = {
    "Laptops": {
        "brands": {
            "Apple": {"base_price": 85000, "price_std": 25000, "rating_mean": 4.6, "rating_std": 0.3},
            "Dell": {"base_price": 55000, "price_std": 18000, "rating_mean": 4.2, "rating_std": 0.4},
            "HP": {"base_price": 48000, "price_std": 15000, "rating_mean": 4.1, "rating_std": 0.4},
            "Lenovo": {"base_price": 45000, "price_std": 16000, "rating_mean": 4.2, "rating_std": 0.4},
            "ASUS": {"base_price": 52000, "price_std": 22000, "rating_mean": 4.3, "rating_std": 0.4},
            "Acer": {"base_price": 38000, "price_std": 12000, "rating_mean": 4.0, "rating_std": 0.5},
            "MSI": {"base_price": 68000, "price_std": 24000, "rating_mean": 4.3, "rating_std": 0.4},
        },
        "rams": [8, 16, 24, 32, 64],
        "storages": [256, 512, 1024, 2048],
        "processors": ["Intel Core i3", "Intel Core i5", "Intel Core i7", "Intel Core i9", "AMD Ryzen 5", "AMD Ryzen 7", "Apple M2", "Apple M3"],
        "screens": [13.3, 14.0, 15.6, 16.0, 17.3],
        "keywords": ["Gaming", "Thin & Light", "OLED", "Backlit Keyboard", "FHD Display", "Touchscreen", "Creator Edition", "Military Grade"]
    },
    "Smartphones": {
        "brands": {
            "Apple": {"base_price": 79000, "price_std": 28000, "rating_mean": 4.6, "rating_std": 0.3},
            "Samsung": {"base_price": 42000, "price_std": 25000, "rating_mean": 4.3, "rating_std": 0.4},
            "OnePlus": {"base_price": 38000, "price_std": 14000, "rating_mean": 4.3, "rating_std": 0.3},
            "Xiaomi": {"base_price": 18000, "price_std": 8000, "rating_mean": 4.1, "rating_std": 0.4},
            "Realme": {"base_price": 16000, "price_std": 6000, "rating_mean": 4.0, "rating_std": 0.4},
            "Google": {"base_price": 59000, "price_std": 18000, "rating_mean": 4.4, "rating_std": 0.3},
            "Motorola": {"base_price": 22000, "price_std": 9000, "rating_mean": 4.1, "rating_std": 0.4},
        },
        "rams": [4, 6, 8, 12, 16],
        "storages": [64, 128, 256, 512, 1024],
        "processors": ["Snapdragon 8 Gen 3", "Snapdragon 7s Gen 2", "Dimensity 9200", "A17 Pro", "A16 Bionic", "Tensor G3", "Snapdragon 695"],
        "screens": [6.1, 6.4, 6.67, 6.7, 6.8],
        "keywords": ["5G", "120Hz AMOLED", "OIS Camera", "100W Fast Charging", "Curved Display", "IP68 Water Resistant", "Dual SIM"]
    },
    "Headphones": {
        "brands": {
            "Sony": {"base_price": 18000, "price_std": 10000, "rating_mean": 4.5, "rating_std": 0.3},
            "Bose": {"base_price": 26000, "price_std": 8000, "rating_mean": 4.5, "rating_std": 0.3},
            "Sennheiser": {"base_price": 16000, "price_std": 9000, "rating_mean": 4.4, "rating_std": 0.4},
            "JBL": {"base_price": 6000, "price_std": 4000, "rating_mean": 4.2, "rating_std": 0.4},
            "boAt": {"base_price": 2000, "price_std": 1200, "rating_mean": 3.9, "rating_std": 0.5},
            "OnePlus": {"base_price": 3500, "price_std": 1500, "rating_mean": 4.2, "rating_std": 0.3},
            "Noise": {"base_price": 1800, "price_std": 900, "rating_mean": 3.8, "rating_std": 0.5},
        },
        "rams": [0],
        "storages": [0],
        "processors": ["Standard Audio Chip", "Active Noise Cancellation ANC", "Spatial Audio DSP", "Lossless DAC"],
        "screens": [0.0],
        "keywords": ["Active Noise Cancellation", "40H Playtime", "Wireless Bluetooth 5.3", "Deep Bass", "Multipoint Connection", "Fast Pair"]
    },
    "Smartwatches": {
        "brands": {
            "Apple": {"base_price": 42000, "price_std": 15000, "rating_mean": 4.6, "rating_std": 0.3},
            "Samsung": {"base_price": 24000, "price_std": 8000, "rating_mean": 4.3, "rating_std": 0.4},
            "Garmin": {"base_price": 38000, "price_std": 14000, "rating_mean": 4.5, "rating_std": 0.3},
            "Fossil": {"base_price": 14000, "price_std": 5000, "rating_mean": 3.9, "rating_std": 0.5},
            "Amazfit": {"base_price": 8500, "price_std": 4000, "rating_mean": 4.1, "rating_std": 0.4},
            "Fire-Boltt": {"base_price": 2200, "price_std": 1000, "rating_mean": 3.9, "rating_std": 0.5},
            "Noise": {"base_price": 2400, "price_std": 1100, "rating_mean": 4.0, "rating_std": 0.4},
        },
        "rams": [0],
        "storages": [4, 8, 16, 32, 64],
        "processors": ["Dual Core S9", "Exynos W930", "Nordic Low Power", "Apollo4 Plus"],
        "screens": [1.3, 1.4, 1.78, 1.96, 2.0],
        "keywords": ["AMOLED Display", "Bluetooth Calling", "SpO2 Heart Rate", "GPS Tracking", "Stainless Steel", "100+ Sports Modes"]
    },
    "Tablets": {
        "brands": {
            "Apple": {"base_price": 55000, "price_std": 25000, "rating_mean": 4.7, "rating_std": 0.2},
            "Samsung": {"base_price": 35000, "price_std": 20000, "rating_mean": 4.3, "rating_std": 0.4},
            "Lenovo": {"base_price": 18000, "price_std": 7000, "rating_mean": 4.0, "rating_std": 0.4},
            "Xiaomi": {"base_price": 24000, "price_std": 6000, "rating_mean": 4.3, "rating_std": 0.3},
            "OnePlus": {"base_price": 32000, "price_std": 8000, "rating_mean": 4.4, "rating_std": 0.3},
        },
        "rams": [4, 6, 8, 12, 16],
        "storages": [64, 128, 256, 512, 1024],
        "processors": ["Apple M2", "Apple M4", "Snapdragon 870", "MediaTek Dimensity 9000", "Snapdragon 8 Gen 2"],
        "screens": [10.2, 10.9, 11.0, 12.4, 12.9, 14.6],
        "keywords": ["Stylus Pen Support", "Liquid Retina", "WiFi + 5G Cellular", "Quad Speakers Dolby Atmos", "120Hz Ultra Smooth"]
    }
}


def generate_asin() -> str:
    """Generate a random 10-character Amazon ASIN."""
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "B0" + "".join(random.choice(chars) for _ in range(8))


def generate_product_record(category: str, index: int) -> Dict[str, Any]:
    cat_meta = CATEGORIES[category]
    brand_name = random.choice(list(cat_meta["brands"].keys()))
    brand_stat = cat_meta["brands"][brand_name]

    ram = random.choice(cat_meta["rams"])
    storage = random.choice(cat_meta["storages"])
    processor = random.choice(cat_meta["processors"])
    screen = random.choice(cat_meta["screens"])
    keyword_sample = random.sample(cat_meta["keywords"], k=random.randint(1, 3))

    # Calculate price based on specs and brand
    base_p = brand_stat["base_price"]
    spec_multiplier = 1.0
    if ram > 0:
        spec_multiplier += (ram / 16.0) * 0.30
    if storage > 0:
        spec_multiplier += (storage / 512.0) * 0.25
    if "Apple M" in processor or "Gen 3" in processor or "i9" in processor:
        spec_multiplier += 0.35

    noise = random.gauss(0, brand_stat["price_std"] * 0.35)
    calc_price = max(999.0, (base_p * spec_multiplier) + noise)
    
    # Calculate list price and discount
    discount_pct = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    if discount_pct > 0:
        original_price = calc_price / (1.0 - (discount_pct / 100.0))
    else:
        original_price = calc_price
    
    current_price = round(calc_price, 2)
    original_price = round(original_price, 2)

    # Ratings and reviews
    raw_rating = random.gauss(brand_stat["rating_mean"], brand_stat["rating_std"])
    rating = round(min(5.0, max(1.0, raw_rating)), 1)
    
    review_count = int(random.lognormvariate(5.5, 1.2))
    review_count = max(5, min(review_count, 85000))

    # Product titles
    if category == "Laptops":
        title = f"{brand_name} Laptop {processor} ({ram}GB RAM / {storage}GB SSD / {screen}\" FHD / {', '.join(keyword_sample)})"
    elif category == "Smartphones":
        title = f"{brand_name} Smartphone ({storage}GB Storage, {ram}GB RAM) - {', '.join(keyword_sample)}"
    elif category == "Headphones":
        title = f"{brand_name} Headphones with {', '.join(keyword_sample)}"
    elif category == "Smartwatches":
        title = f"{brand_name} Smartwatch ({screen}\" Display, {', '.join(keyword_sample)})"
    else:
        title = f"{brand_name} Tablet ({screen}\" Display, {storage}GB ROM, {ram}GB RAM, {', '.join(keyword_sample)})"

    # Price tiers
    if current_price <= 25000:
        price_tier = "Budget"
    elif current_price <= 65000:
        price_tier = "Mid-Range"
    else:
        price_tier = "Premium"

    is_prime = random.random() < 0.85
    in_stock = random.random() < 0.95

    return {
        "asin": generate_asin(),
        "title": title,
        "brand": brand_name,
        "category": category,
        "current_price": current_price,
        "original_price": original_price,
        "discount_percentage": discount_pct,
        "rating": rating,
        "review_count": review_count,
        "ram_gb": ram,
        "storage_gb": storage,
        "processor": processor,
        "screen_size_inches": screen,
        "is_prime": 1 if is_prime else 0,
        "in_stock": 1 if in_stock else 0,
        "price_tier": price_tier,
        "product_url": f"https://www.amazon.in/dp/{generate_asin()}"
    }


def generate_seed_catalog(total_records: int = 1200) -> List[Dict[str, Any]]:
    """Generates sample catalog data."""
    random.seed(42)
    records = []
    cats = list(CATEGORIES.keys())
    per_cat = total_records // len(cats)

    for cat in cats:
        for i in range(per_cat):
            records.append(generate_product_record(cat, i))

    random.shuffle(records)
    return records


if __name__ == "__main__":
    catalog = generate_seed_catalog(100)
    print(f"Generated {len(catalog)} items.")
