PRAGMA foreign_keys = ON;

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Brands table
CREATE TABLE IF NOT EXISTS brands (
    brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL UNIQUE,
    origin_tier TEXT DEFAULT 'Standard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    asin TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    brand_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    current_price REAL NOT NULL CHECK(current_price >= 0),
    original_price REAL NOT NULL CHECK(original_price >= 0),
    discount_percentage REAL DEFAULT 0 CHECK(discount_percentage >= 0 AND discount_percentage <= 100),
    rating REAL NOT NULL CHECK(rating >= 1.0 AND rating <= 5.0),
    review_count INTEGER DEFAULT 0 CHECK(review_count >= 0),
    ram_gb INTEGER DEFAULT 0,
    storage_gb INTEGER DEFAULT 0,
    processor TEXT DEFAULT 'Standard',
    screen_size_inches REAL DEFAULT 0.0,
    is_prime INTEGER DEFAULT 0 CHECK(is_prime IN (0, 1)),
    in_stock INTEGER DEFAULT 1 CHECK(in_stock IN (0, 1)),
    price_tier TEXT NOT NULL CHECK(price_tier IN ('Budget', 'Mid-Range', 'Premium')),
    product_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- Indexes for common filters
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(current_price);
CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating);
CREATE INDEX IF NOT EXISTS idx_products_tier ON products(price_tier);
CREATE INDEX IF NOT EXISTS idx_products_discount ON products(discount_percentage);

-- Flattened view joining products with brand and category names
CREATE VIEW IF NOT EXISTS v_product_catalog_flat AS
SELECT 
    p.asin,
    p.title,
    b.brand_name,
    c.category_name,
    p.current_price,
    p.original_price,
    ROUND(p.original_price - p.current_price, 2) AS absolute_discount_amount,
    p.discount_percentage,
    p.rating,
    p.review_count,
    p.ram_gb,
    p.storage_gb,
    p.processor,
    p.screen_size_inches,
    p.is_prime,
    p.price_tier,
    p.product_url,
    p.scraped_at
FROM products p
JOIN brands b ON p.brand_id = b.brand_id
JOIN categories c ON p.category_id = c.category_id;
