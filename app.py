"""
Streamlit dashboard for the E-Commerce Product Intelligence project.
"""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Product Intelligence",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.predict import PriceTierPredictor
from database.db_manager import DatabaseManager, DEFAULT_DB_PATH

@st.cache_resource
def load_predictor():
    return PriceTierPredictor()

@st.cache_resource
def get_db():
    return DatabaseManager(str(DEFAULT_DB_PATH))

st.sidebar.title("E-Commerce Analytics")
st.sidebar.caption("Pipeline: Web Scraping -> SQL -> EDA -> ML")

page = st.sidebar.radio(
    "Go to",
    [
        "Price Tier Predictor",
        "SQL Analysis & Database",
        "EDA Charts",
        "Model Evaluation"
    ]
)

st.sidebar.divider()
st.sidebar.markdown(
    """
    **Stack:**
    - Python, SQLite3
    - Scikit-learn (Random Forest)
    - Pandas, Seaborn, Matplotlib
    - Streamlit
    """
)

# ------------------------------------------------------------------------------
# PAGE 1: PREDICTOR
# ------------------------------------------------------------------------------
if page == "Price Tier Predictor":
    st.title("Product Price Tier Predictor")
    st.write("Input product specifications to predict the price category (Budget, Mid-Range, or Premium).")

    predictor = load_predictor()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Product Details")
        category = st.selectbox(
            "Category",
            ["Laptops", "Smartphones", "Headphones", "Smartwatches", "Tablets"]
        )

        brand_options = {
            "Laptops": ["Apple", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI"],
            "Smartphones": ["Apple", "Samsung", "OnePlus", "Xiaomi", "Realme", "Google", "Motorola"],
            "Headphones": ["Sony", "Bose", "Sennheiser", "JBL", "boAt", "OnePlus", "Noise"],
            "Smartwatches": ["Apple", "Samsung", "Garmin", "Fossil", "Amazfit", "Fire-Boltt", "Noise"],
            "Tablets": ["Apple", "Samsung", "Lenovo", "Xiaomi", "OnePlus"]
        }
        brand = st.selectbox("Brand", brand_options.get(category, ["Apple", "Samsung", "Dell"]))

        title_input = st.text_input(
            "Product Title",
            value=f"{brand} {category} 16GB RAM"
        )

        processor_options = [
            "Intel Core", "AMD Ryzen", "Apple M2", "Apple M3",
            "Qualcomm Snapdragon", "MediaTek Dimensity", "Active Noise Cancellation ANC", "Standard"
        ]
        processor = st.selectbox("Processor / Chipset", processor_options)

    with col2:
        st.subheader("Specs & Ratings")
        c2a, c2b = st.columns(2)
        with c2a:
            ram = st.select_slider("RAM (GB)", options=[0, 4, 6, 8, 12, 16, 24, 32, 64], value=16 if category in ["Laptops", "Smartphones"] else 0)
            storage = st.select_slider("Storage (GB)", options=[0, 32, 64, 128, 256, 512, 1024, 2048], value=512 if category in ["Laptops", "Tablets"] else (128 if category == "Smartphones" else 0))
            screen = st.slider("Screen Size (Inches)", min_value=0.0, max_value=17.3, value=15.6 if category == "Laptops" else (6.7 if category == "Smartphones" else 0.0), step=0.1)

        with c2b:
            rating = st.slider("Rating (1.0 - 5.0)", min_value=1.0, max_value=5.0, value=4.3, step=0.1)
            reviews = st.number_input("Review Count", min_value=5, max_value=100000, value=1200, step=100)
            discount = st.slider("Discount (%)", min_value=0, max_value=70, value=15, step=5)
            is_prime = st.checkbox("Prime Eligible", value=True)

    if st.button("Predict Tier", type="primary", use_container_width=True):
        sample = {
            "title": title_input,
            "category_name": category,
            "brand_name": brand,
            "processor": processor,
            "ram_gb": ram,
            "storage_gb": storage,
            "screen_size_inches": screen,
            "rating": rating,
            "review_count": reviews,
            "discount_percentage": discount,
            "is_prime": 1 if is_prime else 0
        }

        res = predictor.predict_one(sample)
        tier = res["predicted_tier"]

        st.divider()
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Predicted Tier", tier)
        with m2:
            st.metric("Confidence", res["confidence_percentage"])
        with m3:
            st.metric("Estimated Price Range", res["estimated_price_range_inr"])

        st.write("#### Probabilities:")
        probs = res["class_probabilities"]
        for c_name in ["Budget", "Mid-Range", "Premium"]:
            p_val = probs.get(c_name, 0.0)
            st.write(f"**{c_name}:** {p_val * 100:.1f}%")
            st.progress(float(p_val))

# ------------------------------------------------------------------------------
# PAGE 2: SQL QUERIES
# ------------------------------------------------------------------------------
elif page == "SQL Analysis & Database":
    st.title("SQL Analysis & Data Warehouse")
    st.write("Run analytical SQL queries on the SQLite product database.")

    db = get_db()
    queries = db.parse_queries_file()

    selected_q_key = st.selectbox(
        "Select Query:",
        list(queries.keys()),
        format_func=lambda k: queries[k]["title"]
    )

    q_data = queries[selected_q_key]

    try:
        df_result = db.execute_query(q_data["sql"])
        st.dataframe(df_result, use_container_width=True)
        st.caption(f"{len(df_result)} rows returned.")
    except Exception as e:
        st.error(f"Query error: {e}")

    with st.expander("View SQL Query"):
        st.code(q_data["sql"], language="sql")

# ------------------------------------------------------------------------------
# PAGE 3: EDA CHARTS
# ------------------------------------------------------------------------------
elif page == "EDA Charts":
    st.title("Exploratory Data Analysis")
    st.write("Charts generated during data exploration.")

    figures_dir = PROJECT_ROOT / "reports" / "figures"
    charts = [
        ("01_price_distribution_by_category.png", "Price Distribution by Category"),
        ("02_rating_vs_reviews_by_tier.png", "Rating vs Reviews Count"),
        ("03_top_brands_avg_price.png", "Average Price by Brand"),
        ("04_discount_vs_rating_stability.png", "Rating Stability across Discount Brackets"),
        ("05_feature_correlation_matrix.png", "Feature Correlation Heatmap")
    ]

    for fname, title in charts:
        fpath = figures_dir / fname
        if fpath.exists():
            st.subheader(title)
            st.image(str(fpath), use_container_width=True)
            st.divider()

# ------------------------------------------------------------------------------
# PAGE 4: MODEL EVALUATION
# ------------------------------------------------------------------------------
elif page == "Model Evaluation":
    st.title("Model Performance & Comparison")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Best Model", "Random Forest")
    with m2:
        st.metric("Test Accuracy", "92.50%")
    with m3:
        st.metric("Weighted F1", "0.9249")

    st.subheader("Model Comparison")
    df_models = pd.DataFrame([
        {"Model": "Random Forest", "Test Accuracy": "92.50%", "Balanced Acc": "92.69%", "Macro F1": "0.9254", "Weighted F1": "0.9249"},
        {"Model": "Gradient Boosting", "Test Accuracy": "92.08%", "Balanced Acc": "92.21%", "Macro F1": "0.9213", "Weighted F1": "0.9209"},
        {"Model": "Logistic Regression", "Test Accuracy": "90.42%", "Balanced Acc": "90.57%", "Macro F1": "0.9048", "Weighted F1": "0.9045"}
    ])
    st.table(df_models)

    c1, c2 = st.columns(2)
    figures_dir = PROJECT_ROOT / "reports" / "figures"
    cm_path = figures_dir / "06_ml_confusion_matrix.png"
    fi_path = figures_dir / "07_ml_feature_importance.png"

    with c1:
        if cm_path.exists():
            st.subheader("Confusion Matrix")
            st.image(str(cm_path), use_container_width=True)

    with c2:
        if fi_path.exists():
            st.subheader("Top Feature Importances")
            st.image(str(fi_path), use_container_width=True)
