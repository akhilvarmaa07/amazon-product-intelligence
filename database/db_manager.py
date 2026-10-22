"""
Database helper module using SQLite3 and Pandas.
Handles table creation, bulk inserts, and running analysis queries.
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = DB_DIR.parent / "data" / "processed" / "amazon_products.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
QUERIES_PATH = DB_DIR / "analytics_queries.sql"


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self) -> None:
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()

        with self.get_connection() as conn:
            conn.executescript(ddl)
            conn.commit()
        logger.info(f"Initialized database at {self.db_path}")

    def insert_products(self, products: List[Dict[str, Any]]) -> int:
        """Insert categories, brands, and product rows into SQLite."""
        if not products:
            logger.warning("No product records to insert.")
            return 0

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Insert unique categories
            categories = list({p["category"] for p in products})
            for cat in categories:
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (category_name) VALUES (?)",
                    (cat,)
                )

            # Insert unique brands
            brands = list({p["brand"] for p in products})
            for brand in brands:
                cursor.execute(
                    "INSERT OR IGNORE INTO brands (brand_name) VALUES (?)",
                    (brand,)
                )

            # Map names to IDs
            cursor.execute("SELECT category_id, category_name FROM categories")
            cat_map = {row["category_name"]: row["category_id"] for row in cursor.fetchall()}

            cursor.execute("SELECT brand_id, brand_name FROM brands")
            brand_map = {row["brand_name"]: row["brand_id"] for row in cursor.fetchall()}

            # Batch insert
            rows = []
            for p in products:
                cat_id = cat_map.get(p["category"])
                brand_id = brand_map.get(p["brand"])
                if not cat_id or not brand_id:
                    continue

                rows.append((
                    p["asin"],
                    p["title"],
                    brand_id,
                    cat_id,
                    float(p["current_price"]),
                    float(p["original_price"]),
                    float(p.get("discount_percentage", 0.0)),
                    float(p["rating"]),
                    int(p.get("review_count", 0)),
                    int(p.get("ram_gb", 0)),
                    int(p.get("storage_gb", 0)),
                    p.get("processor", "Standard"),
                    float(p.get("screen_size_inches", 0.0)),
                    int(p.get("is_prime", 0)),
                    int(p.get("in_stock", 1)),
                    p["price_tier"],
                    p.get("product_url", "")
                ))

            insert_sql = """
            INSERT OR REPLACE INTO products (
                asin, title, brand_id, category_id, current_price, original_price,
                discount_percentage, rating, review_count, ram_gb, storage_gb,
                processor, screen_size_inches, is_prime, in_stock, price_tier, product_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.executemany(insert_sql, rows)
            conn.commit()

            logger.info(f"Saved {len(rows)} products to database.")
            return len(rows)

    def get_all_products_df(self) -> pd.DataFrame:
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM v_product_catalog_flat;", conn)

    def parse_queries_file(self) -> Dict[str, Dict[str, str]]:
        if not QUERIES_PATH.exists():
            raise FileNotFoundError(f"Queries file not found: {QUERIES_PATH}")

        with open(QUERIES_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        queries = {}
        blocks = content.split("-- ------------------------------------------------------------------------------")
        for b in blocks:
            b_strip = b.strip()
            if not b_strip:
                continue

            name = None
            title = None
            sql_lines = []
            desc_lines = []

            for line in b_strip.split("\n"):
                if line.startswith("-- name:"):
                    name = line.replace("-- name:", "").strip()
                elif line.startswith("-- QUERY"):
                    title = line.replace("--", "").strip()
                elif line.startswith("--"):
                    desc_lines.append(line.replace("--", "").strip())
                else:
                    if line.strip():
                        sql_lines.append(line)

            if name and sql_lines:
                queries[name] = {
                    "name": name,
                    "title": title or name,
                    "description": " ".join(desc_lines),
                    "sql": "\n".join(sql_lines)
                }

        return queries

    def execute_query(self, query_sql: str) -> pd.DataFrame:
        with self.get_connection() as conn:
            return pd.read_sql_query(query_sql, conn)

    def generate_analytics_report(self, output_markdown_path: Optional[str] = None) -> str:
        queries_dict = self.parse_queries_file()
        report_sections = [
            "# SQL Analytics Report",
            "Summary of queries run on the scraped product catalog.\n"
        ]

        for name, q_info in queries_dict.items():
            try:
                df = self.execute_query(q_info["sql"])
                report_sections.append(f"## {q_info['title']}")
                if q_info["description"]:
                    report_sections.append(f"*{q_info['description']}*\n")
                
                report_sections.append(df.to_markdown(index=False))
                report_sections.append("\n```sql")
                report_sections.append(q_info["sql"].strip())
                report_sections.append("```\n---\n")
            except Exception as e:
                logger.error(f"Error executing {name}: {e}")

        full_report = "\n".join(report_sections)

        if output_markdown_path:
            out_p = Path(output_markdown_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                f.write(full_report)

        return full_report


if __name__ == "__main__":
    db = DatabaseManager()
    df = db.get_all_products_df()
    print(f"Total products in DB: {len(df)}")
