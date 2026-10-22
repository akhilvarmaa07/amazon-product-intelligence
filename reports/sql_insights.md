# SQL Analytics Report
Summary of queries run on the scraped product catalog.

## category_macro_benchmark
| category_name   |   total_products |   avg_price |   min_price |   max_price |   avg_rating |   total_reviews |   avg_discount_pct |
|:----------------|-----------------:|------------:|------------:|------------:|-------------:|----------------:|-------------------:|
| Laptops         |              240 |    119130   |    42540.6  |    287934   |         4.19 |          117130 |               27.1 |
| Smartphones     |              240 |     54118.9 |    13670.9  |    158123   |         4.22 |          142820 |               29.8 |
| Tablets         |              240 |     49229.4 |    18635.8  |    108246   |         4.33 |          111523 |               28.7 |
| Smartwatches    |              240 |     17915.7 |     1456.34 |     51562.4 |         4.19 |          105631 |               29.1 |
| Headphones      |              240 |     10325.7 |      999    |     30143.5 |         4.2  |          115752 |               27.4 |

```sql
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
```
---

## top_products_per_category
| category_name   |   rank_in_category | brand_name   | title_preview                                           |   current_price |   rating |   review_count |
|:----------------|-------------------:|:-------------|:--------------------------------------------------------|----------------:|---------:|---------------:|
| Headphones      |                  1 | boAt         | boAt Headphones with Multipoint Connection, Fast Pair   |         2133.29 |        5 |           1688 |
| Headphones      |                  2 | Sony         | Sony Headphones with Wireless Bluetooth 5.3, Deep Bass, |        18834.6  |        5 |            647 |
| Headphones      |                  3 | Sony         | Sony Headphones with Wireless Bluetooth 5.3             |        15227.5  |        5 |            544 |
| Laptops         |                  1 | Acer         | Acer Laptop Apple M3 (8GB RAM / 2048GB SSD / 14.0" FHD  |       103485    |        5 |           2755 |
| Laptops         |                  2 | Apple        | Apple Laptop Intel Core i7 (8GB RAM / 256GB SSD / 16.0" |       118687    |        5 |           2569 |
| Laptops         |                  3 | ASUS         | ASUS Laptop Intel Core i7 (64GB RAM / 2048GB SSD / 13.3 |       170945    |        5 |            838 |
| Smartphones     |                  1 | OnePlus      | OnePlus Smartphone (64GB Storage, 4GB RAM) - OIS Camera |        61706.1  |        5 |           1654 |
| Smartphones     |                  2 | Xiaomi       | Xiaomi Smartphone (256GB Storage, 16GB RAM) - IP68 Wate |        29002.3  |        5 |            849 |
| Smartphones     |                  3 | Samsung      | Samsung Smartphone (128GB Storage, 8GB RAM) - 120Hz AMO |        54550.6  |        5 |            563 |
| Smartwatches    |                  1 | Apple        | Apple Smartwatch (1.4" Display, GPS Tracking)           |        47117.3  |        5 |            670 |
| Smartwatches    |                  2 | Garmin       | Garmin Smartwatch (1.96" Display, Bluetooth Calling, 10 |        40787.1  |        5 |            476 |
| Smartwatches    |                  3 | Apple        | Apple Smartwatch (2.0" Display, 100+ Sports Modes, Stai |        32020.9  |        5 |            387 |
| Tablets         |                  1 | Samsung      | Samsung Tablet (14.6" Display, 1024GB ROM, 6GB RAM, Liq |        78262.9  |        5 |           2153 |
| Tablets         |                  2 | Apple        | Apple Tablet (10.9" Display, 512GB ROM, 16GB RAM, Quad  |        87621.5  |        5 |           1442 |
| Tablets         |                  3 | OnePlus      | OnePlus Tablet (10.2" Display, 256GB ROM, 16GB RAM, 120 |        46479.8  |        5 |            785 |

```sql
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
```
---

## brand_dominance_and_premium
| category_name   | brand_name   |   product_count |   brand_avg_price |   brand_avg_rating |   price_premium_pct |
|:----------------|:-------------|----------------:|------------------:|-------------------:|--------------------:|
| Headphones      | Bose         |              30 |          25915.4  |               4.46 |               151   |
| Headphones      | Sony         |              45 |          17687.8  |               4.54 |                71.3 |
| Headphones      | Sennheiser   |              29 |          17242.8  |               4.36 |                67   |
| Headphones      | JBL          |              24 |           5754.89 |               4.25 |               -44.3 |
| Headphones      | OnePlus      |              35 |           3403.7  |               4.16 |               -67   |
| Headphones      | boAt         |              34 |           2043.88 |               3.84 |               -80.2 |
| Headphones      | Noise        |              43 |           1813.13 |               3.85 |               -82.4 |
| Laptops         | Apple        |              34 |         177370    |               4.57 |                48.9 |
| Laptops         | MSI          |              29 |         149993    |               4.31 |                25.9 |
| Laptops         | Dell         |              39 |         118599    |               4.09 |                -0.4 |
| Laptops         | ASUS         |              39 |         107560    |               4.22 |                -9.7 |
| Laptops         | HP           |              31 |         105135    |               4.03 |               -11.7 |
| Laptops         | Lenovo       |              33 |          99255.6  |               4.15 |               -16.7 |
| Laptops         | Acer         |              35 |          81596.8  |               3.95 |               -31.5 |
| Smartphones     | Apple        |              27 |         114281    |               4.54 |               111.2 |
| Smartphones     | Google       |              36 |          83987.4  |               4.37 |                55.2 |
| Smartphones     | Samsung      |              32 |          61392.3  |               4.29 |                13.4 |
| Smartphones     | OnePlus      |              41 |          51943.5  |               4.28 |                -4   |
| Smartphones     | Motorola     |              37 |          31816.4  |               4.09 |               -41.2 |
| Smartphones     | Xiaomi       |              40 |          25125.3  |               4.12 |               -53.6 |
| Smartphones     | Realme       |              27 |          22331.2  |               3.91 |               -58.7 |
| Smartwatches    | Apple        |              32 |          41804.5  |               4.62 |               133.3 |
| Smartwatches    | Garmin       |              30 |          37610.3  |               4.45 |               109.9 |
| Smartwatches    | Samsung      |              39 |          24061.8  |               4.38 |                34.3 |
| Smartwatches    | Fossil       |              31 |          13513    |               3.93 |               -24.6 |
| Smartwatches    | Amazfit      |              36 |           8566.18 |               4.05 |               -52.2 |
| Smartwatches    | Noise        |              34 |           2413.32 |               4.01 |               -86.5 |
| Smartwatches    | Fire-Boltt   |              38 |           2261.99 |               3.91 |               -87.4 |
| Tablets         | Apple        |              44 |          83304.8  |               4.73 |                69.2 |
| Tablets         | Samsung      |              54 |          54378.7  |               4.25 |                10.5 |
| Tablets         | OnePlus      |              42 |          48632    |               4.41 |                -1.2 |
| Tablets         | Xiaomi       |              54 |          36180.8  |               4.29 |               -26.5 |
| Tablets         | Lenovo       |              46 |          26454.3  |               4    |               -46.3 |

```sql
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
```
---

## relative_price_deviation
| asin       | category_name   | brand_name   | title_preview                                 |   current_price |   category_avg_price |   price_delta_from_mean | price_tier   |
|:-----------|:----------------|:-------------|:----------------------------------------------|----------------:|---------------------:|------------------------:|:-------------|
| B0X9FCXGMH | Laptops         | Apple        | Apple Laptop Intel Core i3 (64GB RAM / 2048GB |          287934 |             119130   |                168805   | Premium      |
| B0N4NP6LJK | Laptops         | Apple        | Apple Laptop Intel Core i3 (64GB RAM / 2048GB |          269047 |             119130   |                149918   | Premium      |
| B0K6V6DLVW | Laptops         | Apple        | Apple Laptop Intel Core i3 (64GB RAM / 1024GB |          235110 |             119130   |                115981   | Premium      |
| B02BUXSHBR | Laptops         | Apple        | Apple Laptop Apple M2 (64GB RAM / 256GB SSD / |          229105 |             119130   |                109976   | Premium      |
| B0MXOW4B9M | Smartphones     | Apple        | Apple Smartphone (512GB Storage, 16GB RAM) -  |          158123 |              54118.9 |                104004   | Premium      |
| B0B2INKR76 | Laptops         | MSI          | MSI Laptop Intel Core i7 (64GB RAM / 2048GB S |          222794 |             119130   |                103664   | Premium      |
| B0XL4O50QH | Laptops         | Apple        | Apple Laptop Apple M2 (16GB RAM / 2048GB SSD  |          222675 |             119130   |                103546   | Premium      |
| B0LJ0DC7UF | Laptops         | Apple        | Apple Laptop Intel Core i3 (64GB RAM / 512GB  |          222438 |             119130   |                103308   | Premium      |
| B0SOCH9N3U | Smartphones     | Apple        | Apple Smartphone (1024GB Storage, 8GB RAM) -  |          152765 |              54118.9 |                 98646.3 | Premium      |
| B0LXX6RFUM | Laptops         | Apple        | Apple Laptop Intel Core i3 (32GB RAM / 2048GB |          217291 |             119130   |                 98161.4 | Premium      |
| B058K7FJ7B | Laptops         | Apple        | Apple Laptop AMD Ryzen 7 (24GB RAM / 2048GB S |          214390 |             119130   |                 95260.2 | Premium      |
| B09S2WCDK2 | Smartphones     | Apple        | Apple Smartphone (512GB Storage, 12GB RAM) -  |          147296 |              54118.9 |                 93177.3 | Premium      |
| B0RH20L8GA | Laptops         | Apple        | Apple Laptop AMD Ryzen 5 (64GB RAM / 512GB SS |          211817 |             119130   |                 92687.6 | Premium      |
| B0NFVRQ36H | Smartphones     | Apple        | Apple Smartphone (256GB Storage, 12GB RAM) -  |          145009 |              54118.9 |                 90890.5 | Premium      |
| B0RXYJMUYE | Laptops         | Apple        | Apple Laptop Apple M3 (24GB RAM / 1024GB SSD  |          209582 |             119130   |                 90452   | Premium      |

```sql
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
```
---

## discount_depth_analysis
| discount_bracket       |   product_count |   avg_selling_price |   avg_rating |   avg_reviews_per_product |
|:-----------------------|----------------:|--------------------:|-------------:|--------------------------:|
| 1% - 15% (Light)       |             280 |             50994.7 |         4.27 |                       447 |
| 46%+ (Deep Clearance)  |             216 |             50140.8 |         4.22 |                       527 |
| 31% - 45% (Aggressive) |             306 |             50206.6 |         4.22 |                       527 |
| 0% (No Discount)       |              85 |             46959.7 |         4.22 |                       444 |
| 16% - 30% (Moderate)   |             313 |             50188.1 |         4.2  |                       496 |

```sql
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
```
---

## anomalies_gems_and_underperformers
| anomaly_type     | category_name   | brand_name   | title_preview                                      |   current_price |   rating |   review_count |
|:-----------------|:----------------|:-------------|:---------------------------------------------------|----------------:|---------:|---------------:|
| Budget Value Gem | Headphones      | Sony         | Sony Headphones with Wireless Bluetooth 5.3, Deep  |        18834.6  |      5   |            647 |
| Budget Value Gem | Headphones      | boAt         | boAt Headphones with Multipoint Connection, Fast P |         2133.29 |      5   |           1688 |
| Budget Value Gem | Headphones      | Sony         | Sony Headphones with Wireless Bluetooth 5.3        |        15227.5  |      5   |            544 |
| Budget Value Gem | Headphones      | Sony         | Sony Headphones with 40H Playtime                  |        18879.4  |      4.9 |            955 |
| Budget Value Gem | Smartwatches    | Samsung      | Samsung Smartwatch (2.0" Display, 100+ Sports Mode |        21746    |      4.9 |            741 |
| Budget Value Gem | Smartwatches    | Samsung      | Samsung Smartwatch (1.96" Display, Stainless Steel |        23410.7  |      4.9 |           1176 |
| Budget Value Gem | Headphones      | Sennheiser   | Sennheiser Headphones with Wireless Bluetooth 5.3, |        20962.4  |      4.8 |            519 |
| Budget Value Gem | Headphones      | Sony         | Sony Headphones with Active Noise Cancellation, De |        16825.2  |      4.7 |           1099 |
| Budget Value Gem | Smartwatches    | Amazfit      | Amazfit Smartwatch (1.78" Display, 100+ Sports Mod |         6294.77 |      4.7 |            567 |
| Budget Value Gem | Smartwatches    | Samsung      | Samsung Smartwatch (1.4" Display, Stainless Steel) |        21981    |      4.7 |            657 |
| Budget Value Gem | Headphones      | Sony         | Sony Headphones with Deep Bass                     |        17922    |      4.7 |            768 |
| Budget Value Gem | Smartwatches    | Samsung      | Samsung Smartwatch (1.78" Display, Bluetooth Calli |        23083.9  |      4.7 |            544 |
| Budget Value Gem | Smartwatches    | Fire-Boltt   | Fire-Boltt Smartwatch (2.0" Display, Bluetooth Cal |         1537.91 |      4.7 |           3413 |
| Budget Value Gem | Headphones      | Sennheiser   | Sennheiser Headphones with Multipoint Connection,  |        18348.3  |      4.6 |            780 |
| Budget Value Gem | Headphones      | OnePlus      | OnePlus Headphones with Deep Bass                  |         3688.81 |      4.6 |            630 |
| Budget Value Gem | Headphones      | Sony         | Sony Headphones with Fast Pair                     |        18414.4  |      4.6 |            625 |
| Budget Value Gem | Headphones      | JBL          | JBL Headphones with 40H Playtime, Multipoint Conne |         4880.74 |      4.6 |            539 |
| Budget Value Gem | Smartwatches    | Samsung      | Samsung Smartwatch (1.96" Display, AMOLED Display, |        24751.8  |      4.5 |            555 |
| Budget Value Gem | Headphones      | Sennheiser   | Sennheiser Headphones with Wireless Bluetooth 5.3, |        16138.3  |      4.5 |           1150 |
| Budget Value Gem | Headphones      | Sennheiser   | Sennheiser Headphones with Wireless Bluetooth 5.3  |        15571.6  |      4.5 |            906 |

```sql
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
```
---

## hardware_specs_roi
|   ram_gb |   storage_gb |   laptop_count |   avg_price |   min_price |   max_price |   avg_rating |
|---------:|-------------:|---------------:|------------:|------------:|------------:|-------------:|
|        8 |          256 |             10 |     72674.8 |     42540.6 |      118687 |         4.07 |
|        8 |          512 |              9 |     86088.1 |     69060   |      137715 |         4.16 |
|        8 |         1024 |             16 |     90426.1 |     58644.6 |      143480 |         4.24 |
|        8 |         2048 |              6 |    128889   |     95283.9 |      177295 |         4.2  |
|       16 |          256 |              9 |     99495.9 |     65250   |      153163 |         4.34 |
|       16 |          512 |              7 |     94424.9 |     66286.8 |      110048 |         4.2  |
|       16 |         1024 |             17 |     96048.2 |     61581.6 |      157860 |         4.21 |
|       16 |         2048 |             14 |    139540   |     84612.1 |      222675 |         4.13 |
|       24 |          256 |             14 |    107854   |     55818.1 |      172755 |         4.17 |
|       24 |          512 |             14 |    102070   |     70672.4 |      159385 |         4.19 |
|       24 |         1024 |             13 |    116304   |     68030.6 |      209582 |         4.2  |
|       24 |         2048 |             13 |    156996   |    114327   |      214390 |         4.32 |
|       32 |          256 |             13 |    107330   |     71203.7 |      186988 |         4.32 |
|       32 |          512 |             11 |    107333   |     70512.6 |      166963 |         4.25 |
|       32 |         1024 |             11 |    114269   |     75897.9 |      201270 |         4.24 |
|       32 |         2048 |             15 |    144643   |    112092   |      217291 |         4.01 |
|       64 |          256 |             13 |    131584   |     83562.7 |      229105 |         4.05 |
|       64 |          512 |             15 |    142725   |     96315   |      222438 |         4.13 |
|       64 |         1024 |             11 |    155801   |    115236   |      235110 |         4.12 |
|       64 |         2048 |              9 |    185214   |    123003   |      287934 |         4.28 |

```sql
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
```
---

## prime_badge_impact
| prime_status   |   total_listings |   avg_price |   avg_rating |   avg_reviews |   avg_discount_pct |
|:---------------|-----------------:|------------:|-------------:|--------------:|-------------------:|
| Non-Prime      |              173 |     49407.9 |         4.23 |           505 |               28.7 |
| Prime Eligible |             1027 |     50267.8 |         4.22 |           492 |               28.4 |

```sql
SELECT 
    CASE WHEN is_prime = 1 THEN 'Prime Eligible' ELSE 'Non-Prime' END AS prime_status,
    COUNT(asin) AS total_listings,
    ROUND(AVG(current_price), 2) AS avg_price,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(review_count), 0) AS avg_reviews,
    ROUND(AVG(discount_percentage), 1) AS avg_discount_pct
FROM products
GROUP BY is_prime;
```
---
