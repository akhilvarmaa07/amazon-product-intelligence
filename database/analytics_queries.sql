-- ------------------------------------------------------------------------------
-- QUERY 1: Category Price and Volume Overview
-- ------------------------------------------------------------------------------
-- name: category_macro_benchmark
SELECT 
    c.category_name,
    COUNT(p.asin) AS total_products,
    ROUND(AVG(p.current_price), 2) AS avg_price,
    ROUND(MIN(p.current_price), 2) AS min_price,
    ROUND(MAX(p.current_price), 2) AS max_price,
    ROUND(AVG(p.rating), 2) AS avg_rating,
    SUM(p.review_count) AS total_reviews,
    ROUND(AVG(p.discount_percentage), 1) AS avg_discount_pct
FROM products p
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_id, c.category_name
ORDER BY avg_price DESC;

-- ------------------------------------------------------------------------------
-- QUERY 2: Top 3 Rated Products per Category (Using DENSE_RANK Window Function)
-- ------------------------------------------------------------------------------
-- name: top_products_per_category
WITH RankedProducts AS (
    SELECT 
        c.category_name,
        b.brand_name,
        p.title,
        p.current_price,
        p.rating,
        p.review_count,
        DENSE_RANK() OVER (
            PARTITION BY p.category_id 
            ORDER BY p.rating DESC, p.review_count DESC
        ) AS rank_in_category
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    JOIN brands b ON p.brand_id = b.brand_id
)
SELECT 
    category_name,
    rank_in_category,
    brand_name,
    SUBSTR(title, 1, 55) AS title_preview,
    current_price,
    rating,
    review_count
FROM RankedProducts
WHERE rank_in_category <= 3
ORDER BY category_name, rank_in_category;

-- ------------------------------------------------------------------------------
-- QUERY 3: Brand Price Premium vs Category Average (Using CTE)
-- ------------------------------------------------------------------------------
-- name: brand_dominance_and_premium
WITH CategoryAverages AS (
    SELECT 
        category_id,
        AVG(current_price) AS cat_avg_price
    FROM products
    GROUP BY category_id
),
BrandAggs AS (
    SELECT 
        c.category_name,
        b.brand_name,
        COUNT(p.asin) AS product_count,
        ROUND(AVG(p.current_price), 2) AS brand_avg_price,
        ROUND(AVG(p.rating), 2) AS brand_avg_rating,
        ca.cat_avg_price
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    JOIN brands b ON p.brand_id = b.brand_id
    JOIN CategoryAverages ca ON p.category_id = ca.category_id
    GROUP BY c.category_id, b.brand_id
)
SELECT 
    category_name,
    brand_name,
    product_count,
    brand_avg_price,
    brand_avg_rating,
    ROUND(((brand_avg_price - cat_avg_price) / cat_avg_price) * 100, 1) AS price_premium_pct
FROM BrandAggs
WHERE product_count >= 10
ORDER BY category_name, price_premium_pct DESC;

-- ------------------------------------------------------------------------------
-- QUERY 4: Price Difference from Category Average (Partitioned AVG)
-- ------------------------------------------------------------------------------
-- name: relative_price_deviation
SELECT 
    p.asin,
    c.category_name,
    b.brand_name,
    SUBSTR(p.title, 1, 45) AS title_preview,
    p.current_price,
    ROUND(AVG(p.current_price) OVER(PARTITION BY p.category_id), 2) AS category_avg_price,
    ROUND(p.current_price - AVG(p.current_price) OVER(PARTITION BY p.category_id), 2) AS price_delta_from_mean,
    p.price_tier
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN brands b ON p.brand_id = b.brand_id
ORDER BY ABS(p.current_price - AVG(p.current_price) OVER(PARTITION BY p.category_id)) DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- QUERY 5: Discount Range vs Average Rating
-- ------------------------------------------------------------------------------
-- name: discount_depth_analysis
SELECT 
    CASE 
        WHEN discount_percentage = 0 THEN '0% (No Discount)'
        WHEN discount_percentage <= 15 THEN '1% - 15% (Light)'
        WHEN discount_percentage <= 30 THEN '16% - 30% (Moderate)'
        WHEN discount_percentage <= 45 THEN '31% - 45% (Aggressive)'
        ELSE '46%+ (Deep Clearance)'
    END AS discount_bracket,
    COUNT(asin) AS product_count,
    ROUND(AVG(current_price), 2) AS avg_selling_price,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(review_count), 0) AS avg_reviews_per_product
FROM products
GROUP BY discount_bracket
ORDER BY avg_rating DESC;

-- ------------------------------------------------------------------------------
-- QUERY 6: Highly Rated Budget Items vs Low Rated Premium Items
-- ------------------------------------------------------------------------------
-- name: anomalies_gems_and_underperformers
SELECT 
    'Budget Value Gem' AS anomaly_type,
    c.category_name,
    b.brand_name,
    SUBSTR(p.title, 1, 50) AS title_preview,
    p.current_price,
    p.rating,
    p.review_count
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN brands b ON p.brand_id = b.brand_id
WHERE p.price_tier = 'Budget' AND p.rating >= 4.4 AND p.review_count >= 500

UNION ALL

SELECT 
    'Overpriced Underperformer' AS anomaly_type,
    c.category_name,
    b.brand_name,
    SUBSTR(p.title, 1, 50) AS title_preview,
    p.current_price,
    p.rating,
    p.review_count
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN brands b ON p.brand_id = b.brand_id
WHERE p.price_tier = 'Premium' AND p.rating < 4.0
ORDER BY anomaly_type, rating DESC
LIMIT 20;

-- ------------------------------------------------------------------------------
-- QUERY 7: Laptop RAM and Storage Price Analysis
-- ------------------------------------------------------------------------------
-- name: hardware_specs_roi
SELECT 
    p.ram_gb,
    p.storage_gb,
    COUNT(p.asin) AS laptop_count,
    ROUND(AVG(p.current_price), 2) AS avg_price,
    ROUND(MIN(p.current_price), 2) AS min_price,
    ROUND(MAX(p.current_price), 2) AS max_price,
    ROUND(AVG(p.rating), 2) AS avg_rating
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE c.category_name = 'Laptops' AND p.ram_gb > 0
GROUP BY p.ram_gb, p.storage_gb
ORDER BY p.ram_gb ASC, p.storage_gb ASC;

-- ------------------------------------------------------------------------------
-- QUERY 8: Prime Eligible vs Non-Prime Comparison
-- ------------------------------------------------------------------------------
-- name: prime_badge_impact
SELECT 
    CASE WHEN is_prime = 1 THEN 'Prime Eligible' ELSE 'Non-Prime' END AS prime_status,
    COUNT(asin) AS total_listings,
    ROUND(AVG(current_price), 2) AS avg_price,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(review_count), 0) AS avg_reviews,
    ROUND(AVG(discount_percentage), 1) AS avg_discount_pct
FROM products
GROUP BY is_prime;
