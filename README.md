# E-Commerce Product Intelligence & Price Prediction

An end-to-end data and machine learning project that collects e-commerce product listings from Amazon, processes and stores them in a normalized SQLite database, runs SQL analysis queries (using CTEs and Window Functions), and trains a machine learning classifier to predict product price tiers.

Includes an interactive Streamlit dashboard for querying the database and making real-time price predictions.

---

## Overview

The project covers 4 main stages:

1. **Data Collection & Parsing**: Scrapes product data from Amazon search pages using BeautifulSoup, extracting price, rating, reviews, discount, and hardware specs (RAM, storage, processor, screen size) using regular expressions.
2. **Relational Database (SQL)**: Stores data in a 3NF SQLite database (`categories`, `brands`, `products`). Includes 8 SQL queries using Common Table Expressions (CTEs) and Window Functions (`DENSE_RANK()`, partitioned averages) to analyze brand pricing, discount elasticity, and category benchmarks.
3. **Exploratory Data Analysis (EDA)**: Analyzes distributions and correlations using Pandas, Matplotlib, and Seaborn, generating visualization charts saved to `reports/figures/`.
4. **Machine Learning**: Preprocesses tabular and text features with Scikit-learn's `ColumnTransformer` (scaling, one-hot encoding, and TF-IDF on product titles). Compares Logistic Regression, Random Forest, and Gradient Boosting to classify products into `Budget`, `Mid-Range`, or `Premium` tiers.
5. **Streamlit App**: A simple web UI to run queries, view charts, and test custom product predictions interactively.

---

## Project Structure

```
amazon_product_intelligence/
├── data/
│   ├── raw/                  # Scraped CSV and JSON data
│   └── processed/            # SQLite database and saved model artifact (.joblib)
├── database/
│   ├── schema.sql            # SQLite schema (tables, foreign keys, indexes, views)
│   ├── analytics_queries.sql # SQL analysis queries (CTEs, Window Functions)
│   └── db_manager.py         # Database connection and helper methods
├── scraper/
│   ├── amazon_scraper.py     # Scraper with rotating headers and regex parser
│   └── data_generator.py     # Local sample generator for offline testing
├── eda/
│   └── eda_analyzer.py       # EDA charts and summary statistics
├── ml/
│   ├── feature_engineering.py# Preprocessing pipeline (ColumnTransformer, TF-IDF)
│   ├── train_model.py        # Model training, cross-validation, and evaluation
│   └── predict.py            # Inference script to predict tier on new products
├── reports/
│   ├── figures/              # Generated plots and confusion matrix
│   └── sql_insights.md       # Output markdown report from SQL queries
├── app.py                    # Streamlit web app
├── run_pipeline.py           # Master script to run everything end-to-end
├── test_pipeline.py          # Pytest test suite
├── requirements.txt
└── README.md
```

---

## Machine Learning Results

Models evaluated on a held-out test split (80/20 train/test):

| Model | Test Accuracy | Balanced Accuracy | Weighted F1 | Macro F1 |
|---|:---:|:---:|:---:|:---:|
| **Random Forest** | **92.50%** | **92.69%** | **0.9249** | **0.9254** |
| **Gradient Boosting** | 92.08% | 92.21% | 0.9209 | 0.9213 |
| **Logistic Regression** | 90.42% | 90.57% | 0.9045 | 0.9048 |

The Random Forest model was selected as the best performer and serialized to `data/processed/best_price_tier_model.joblib`. Key predictive features include RAM, storage, brand, and title keywords.

---

## SQL Queries Implemented

The queries in `database/analytics_queries.sql` analyze:
- **Category Benchmarks**: Average, min, max price, ratings, and review count by category.
- **Top 3 Products per Category**: Ranked using `DENSE_RANK() OVER (PARTITION BY category_id ORDER BY rating DESC, review_count DESC)`.
- **Brand Price Premium**: CTE comparing each brand's average selling price to the overall category average.
- **Price Deviation**: Difference between individual product price and category average using window averages.
- **Discount vs Rating**: Average rating across 5 discount brackets.
- **Value Gems vs Underperformers**: High-rated budget products vs low-rated premium products.
- **Hardware Spec Pricing**: Price progression across RAM and storage combinations for laptops.
- **Prime Impact**: Pricing and review differences between Prime and non-Prime listings.

---

## Getting Started

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/<your-username>/amazon-product-intelligence.git
cd amazon-product-intelligence
pip install -r requirements.txt
```

### 2. Run the Full Pipeline
Runs scraping/generation, database setup, SQL queries, EDA charts, and model training:
```bash
python run_pipeline.py
```

### 3. Launch the Streamlit App
```bash
streamlit run app.py
```

### 4. Run Tests
```bash
python -m pytest test_pipeline.py -v
```

---

## Tech Stack
- **Python 3.10+**
- **Database:** SQLite3, SQL
- **Libraries:** Pandas, NumPy, Scikit-learn, BeautifulSoup4, Requests, Matplotlib, Seaborn, Streamlit
