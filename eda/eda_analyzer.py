"""
Data analysis and plotting script for product data.
Generates charts for price distribution, ratings, top brands, and feature correlations.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

FIGURES_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"


class EDAAnalyzer:
    def __init__(self, df: pd.DataFrame, output_dir: Optional[Path] = None):
        self.df = df.copy()
        self.output_dir = output_dir or FIGURES_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid", palette="muted")
        plt.rcParams.update({
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10
        })

    def get_summary_statistics(self) -> Dict[str, Any]:
        num_cols = ["current_price", "discount_percentage", "rating", "review_count", "ram_gb", "storage_gb"]
        stats_df = self.df[num_cols].describe().T
        stats_df["median"] = self.df[num_cols].median()
        stats_df["skew"] = self.df[num_cols].skew()
        return stats_df.to_dict(orient="index")

    def plot_price_distribution_by_category(self) -> Path:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(
            data=self.df,
            x="category_name",
            y="current_price",
            hue="category_name",
            palette="Set2",
            ax=ax,
            legend=False
        )
        ax.set_title("Price Distribution by Category (INR)")
        ax.set_xlabel("Category")
        ax.set_ylabel("Price (INR)")
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

        plt.tight_layout()
        out_path = self.output_dir / "01_price_distribution_by_category.png"
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
        return out_path

    def plot_rating_vs_reviews_by_tier(self) -> Path:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            data=self.df,
            x="rating",
            y="review_count",
            hue="price_tier",
            size="current_price",
            sizes=(20, 200),
            palette={"Budget": "#2ecc71", "Mid-Range": "#3498db", "Premium": "#e74c3c"},
            alpha=0.75,
            ax=ax
        )
        ax.set_title("Rating vs Review Count by Price Tier")
        ax.set_xlabel("Average Rating")
        ax.set_ylabel("Review Count (Log Scale)")
        ax.set_yscale("log")
        ax.legend(title="Price Tier", bbox_to_anchor=(1.02, 1), loc="upper left")

        plt.tight_layout()
        out_path = self.output_dir / "02_rating_vs_reviews_by_tier.png"
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
        return out_path

    def plot_top_brands_price_ranking(self, top_n: int = 10) -> Path:
        top_brands = self.df["brand_name"].value_counts().head(top_n).index
        brand_df = self.df[self.df["brand_name"].isin(top_brands)]
        avg_prices = brand_df.groupby("brand_name")["current_price"].mean().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            x=avg_prices.values,
            y=avg_prices.index,
            hue=avg_prices.index,
            palette="crest",
            ax=ax,
            legend=False
        )
        ax.set_title(f"Average Selling Price - Top {top_n} Brands")
        ax.set_xlabel("Average Price (INR)")
        ax.set_ylabel("Brand")

        for i, val in enumerate(avg_prices.values):
            ax.text(val + 500, i, f"Rs {val:,.0f}", va="center", fontsize=9)

        plt.tight_layout()
        out_path = self.output_dir / "03_top_brands_avg_price.png"
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
        return out_path

    def plot_discount_vs_rating_correlation(self) -> Path:
        bins = [-1, 0, 15, 30, 45, 100]
        labels = ["0%", "1-15%", "16-30%", "31-45%", "46%+"]
        temp_df = self.df.copy()
        temp_df["discount_bracket"] = pd.cut(temp_df["discount_percentage"], bins=bins, labels=labels)
        bracket_stats = temp_df.groupby("discount_bracket", observed=False)["rating"].agg(["mean", "count"]).reset_index()

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.barplot(
            data=bracket_stats,
            x="discount_bracket",
            y="mean",
            hue="discount_bracket",
            palette="viridis",
            ax=ax,
            legend=False
        )
        ax.set_ylim(3.0, 5.0)
        ax.set_title("Average Rating by Discount Range")
        ax.set_xlabel("Discount Range")
        ax.set_ylabel("Mean Rating")

        for i, row in bracket_stats.iterrows():
            ax.text(i, row["mean"] + 0.05, f"{row['mean']:.2f} (n={row['count']})", ha="center", fontsize=9)

        plt.tight_layout()
        out_path = self.output_dir / "04_discount_vs_rating_stability.png"
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
        return out_path

    def plot_correlation_heatmap(self) -> Path:
        num_cols = ["current_price", "original_price", "discount_percentage", "rating", "review_count", "ram_gb", "storage_gb", "screen_size_inches"]
        valid_cols = [c for c in num_cols if c in self.df.columns]
        corr_matrix = self.df[valid_cols].corr()

        fig, ax = plt.subplots(figsize=(9, 7))
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            linewidths=0.5,
            ax=ax
        )
        ax.set_title("Numerical Features Correlation")

        plt.tight_layout()
        out_path = self.output_dir / "05_feature_correlation_matrix.png"
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
        return out_path

    def run_full_eda(self) -> Dict[str, Any]:
        p1 = self.plot_price_distribution_by_category()
        p2 = self.plot_rating_vs_reviews_by_tier()
        p3 = self.plot_top_brands_price_ranking()
        p4 = self.plot_discount_vs_rating_correlation()
        p5 = self.plot_correlation_heatmap()

        return {
            "figures": [str(p1), str(p2), str(p3), str(p4), str(p5)],
            "summary_stats": self.get_summary_statistics()
        }


if __name__ == "__main__":
    from ..database.db_manager import DatabaseManager
    db = DatabaseManager()
    df = db.get_all_products_df()
    analyzer = EDAAnalyzer(df)
    res = analyzer.run_full_eda()
    print(f"Generated {len(res['figures'])} charts.")
