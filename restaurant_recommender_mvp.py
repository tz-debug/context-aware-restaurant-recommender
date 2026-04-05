import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Restaurant Recommender MVP", layout="wide")
st.title("Context-Aware Restaurant Recommender")
st.write(
    "A starter MVP for Pakistan and UK restaurant discovery using hybrid-style ranking "
    "with user preferences, restaurant features, and location-aware scoring."
)


@st.cache_data
def load_csv_flexible(path: str) -> pd.DataFrame:
    encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
    last_error = None
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_error = e
    raise last_error


@st.cache_data
def load_dataset() -> pd.DataFrame:
    candidates = [
        "demo_restaurants.csv",
        "./demo_restaurants.csv",
        str(Path.cwd() / "demo_restaurants.csv"),
        str(Path.cwd() / "data" / "demo_restaurants.csv"),
    ]
    for path in candidates:
        if Path(path).exists():
            return load_csv_flexible(path)
    return pd.DataFrame()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    expected = [
        "restaurant_id", "name", "country", "city", "area", "lat", "lon",
        "cuisines", "dietary_tags", "price_band", "rating", "review_count",
        "delivery_available", "dine_in_available", "open_now"
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    bool_cols = ["delivery_available", "dine_in_available", "open_now"]
    for col in bool_cols:
        df[col] = df[col].astype(str).str.lower().map(
            {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
        ).fillna(df[col])

    num_cols = ["lat", "lon", "rating", "review_count"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["cuisines"] = df["cuisines"].fillna("")
    df["dietary_tags"] = df["dietary_tags"].fillna("")
    df["price_band"] = df["price_band"].fillna("medium").str.lower()

    return df


def split_tags(text: str) -> set:
    if pd.isna(text):
        return set()
    return {t.strip().lower() for t in str(text).split("|") if t.strip()}


def haversine_km(lat1, lon1, lat2, lon2):
    if any(pd.isna(v) for v in [lat1, lon1, lat2, lon2]):
        return np.nan
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def scale_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    if len(s) == 0:
        return s
    if s.max() == s.min():
        return pd.Series(np.ones(len(s)), index=s.index)
    return (s - s.min()) / (s.max() - s.min())


def build_user_profile(selected_cuisines, selected_dietary, favorites):
    return {
        "selected_cuisines": {x.lower() for x in selected_cuisines},
        "selected_dietary": {x.lower() for x in selected_dietary},
        "favorites": set(favorites),
    }


def score_restaurants(df: pd.DataFrame, user_profile: dict, user_lat: float, user_lon: float,
                      budget: str, mode: str, country: str, city: str, max_distance_km: float) -> pd.DataFrame:
    out = df.copy()

    out = out[(out["country"] == country) & (out["city"] == city)].copy()
    if out.empty:
        return out

    out["distance_km"] = out.apply(lambda r: haversine_km(user_lat, user_lon, r["lat"], r["lon"]), axis=1)
    out = out[(out["distance_km"].isna()) | (out["distance_km"] <= max_distance_km)].copy()

    if mode == "delivery":
        out = out[out["delivery_available"] == True].copy()
    elif mode == "dine-in":
        out = out[out["dine_in_available"] == True].copy()

    if out.empty:
        return out

    cuisine_scores = []
    dietary_scores = []
    favorite_scores = []

    for _, row in out.iterrows():
        cuisines = split_tags(row["cuisines"])
        dietary = split_tags(row["dietary_tags"])

        cuisine_match = 0.0
        if user_profile["selected_cuisines"]:
            cuisine_match = len(cuisines & user_profile["selected_cuisines"]) / max(len(user_profile["selected_cuisines"]), 1)

        dietary_match = 1.0
        if user_profile["selected_dietary"]:
            dietary_match = len(dietary & user_profile["selected_dietary"]) / max(len(user_profile["selected_dietary"]), 1)

        favorite_boost = 1.0 if row["name"] in user_profile["favorites"] else 0.0

        cuisine_scores.append(cuisine_match)
        dietary_scores.append(dietary_match)
        favorite_scores.append(favorite_boost)

    out["content_score"] = 0.7 * pd.Series(cuisine_scores, index=out.index) + 0.3 * pd.Series(dietary_scores, index=out.index)
    out["favorite_score"] = pd.Series(favorite_scores, index=out.index)

    out["rating_score"] = scale_series(out["rating"].fillna(out["rating"].median()))
    out["popularity_score"] = scale_series(np.log1p(out["review_count"].fillna(0)))
    out["distance_score"] = 1 - scale_series(out["distance_km"].fillna(out["distance_km"].max()))
    out["open_score"] = out["open_now"].astype(int)

    price_map = {"low": 1, "medium": 2, "high": 3}
    target_budget = price_map.get(budget, 2)
    out["budget_score"] = out["price_band"].map(price_map).fillna(2).apply(lambda x: 1 - abs(x - target_budget) / 2)

    out["final_score"] = (
        0.35 * out["content_score"] +
        0.15 * out["rating_score"] +
        0.10 * out["popularity_score"] +
        0.15 * out["distance_score"] +
        0.10 * out["budget_score"] +
        0.05 * out["open_score"] +
        0.10 * out["favorite_score"]
    )

    return out.sort_values("final_score", ascending=False).reset_index(drop=True)


uploaded = st.sidebar.file_uploader("Upload restaurant CSV (optional)", type=["csv"])
if uploaded is not None:
    raw_df = pd.read_csv(uploaded)
else:
    raw_df = load_dataset()

if raw_df.empty:
    st.error("No dataset found. Put demo_restaurants.csv next to the app or upload your own CSV.")
    st.stop()

try:
    df = normalize_columns(raw_df)
except Exception as e:
    st.error(str(e))
    st.stop()

countries = sorted(df["country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Country", countries)

cities = sorted(df[df["country"] == selected_country]["city"].dropna().unique().tolist())
selected_city = st.sidebar.selectbox("City", cities)

city_df = df[(df["country"] == selected_country) & (df["city"] == selected_city)].copy()

all_cuisines = sorted({tag for val in city_df["cuisines"] for tag in split_tags(val)})
all_dietary = sorted({tag for val in city_df["dietary_tags"] for tag in split_tags(val)})

selected_cuisines = st.sidebar.multiselect("Preferred cuisines", all_cuisines, default=all_cuisines[:2] if all_cuisines else [])
selected_dietary = st.sidebar.multiselect("Dietary preferences", all_dietary)
budget = st.sidebar.selectbox("Budget", ["low", "medium", "high"], index=1)
mode = st.sidebar.selectbox("Dining mode", ["any", "delivery", "dine-in"])
max_distance_km = st.sidebar.slider("Max distance (km)", 1, 20, 8)

st.sidebar.subheader("Your location")
default_lat = float(city_df["lat"].median())
default_lon = float(city_df["lon"].median())
user_lat = st.sidebar.number_input("Latitude", value=default_lat, format="%.6f")
user_lon = st.sidebar.number_input("Longitude", value=default_lon, format="%.6f")

favorites = st.sidebar.multiselect("Favorite restaurants", sorted(city_df["name"].unique().tolist()))

profile = build_user_profile(selected_cuisines, selected_dietary, favorites)
ranked = score_restaurants(
    df=df,
    user_profile=profile,
    user_lat=user_lat,
    user_lon=user_lon,
    budget=budget,
    mode=mode,
    country=selected_country,
    city=selected_city,
    max_distance_km=max_distance_km,
)

tab1, tab2, tab3 = st.tabs(["Recommendations", "Data", "Export"])

with tab1:
    st.subheader("Top Recommendations")
    if ranked.empty:
        st.warning("No restaurants matched the current filters.")
    else:
        show_cols = [
            "name", "country", "city", "area", "cuisines", "dietary_tags", "price_band",
            "rating", "review_count", "distance_km", "open_now", "delivery_available",
            "dine_in_available", "final_score"
        ]

        max_results = min(20, len(ranked))
        top_n = st.slider("Number of results", 1, max_results, min(10, max_results))

        st.dataframe(ranked[show_cols].head(top_n), use_container_width=True)

        st.subheader("Why these were recommended")
        explain_cols = [
            "name", "content_score", "rating_score", "popularity_score",
            "distance_score", "budget_score", "open_score", "favorite_score", "final_score"
        ]
        st.dataframe(ranked[explain_cols].head(top_n), use_container_width=True)

with tab2:
    st.subheader("Dataset preview")
    st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
    st.dataframe(df.head(20), use_container_width=True)

with tab3:
    st.subheader("Download ranked results")
    if not ranked.empty:
        csv_data = ranked.to_csv(index=False)
        st.download_button(
            "Download recommendations CSV",
            data=csv_data,
            file_name="recommendations.csv",
            mime="text/csv",
        )
