from pathlib import Path
import os
import pandas as pd

"""
Starter ingestion stub.

Purpose:
- fetch restaurant candidates from an external provider later
- save them into demo_restaurants.csv or a database
- keep the Streamlit app serving from cached data for speed and cost control

Next steps:
1. Create an API key in Google Places or Foursquare
2. Store it in environment variables
3. Replace the placeholder function below with real API calls
4. Normalize returned fields into this schema:

restaurant_id,name,country,city,area,lat,lon,cuisines,dietary_tags,price_band,
rating,review_count,delivery_available,dine_in_available,open_now
"""

OUTPUT_FILE = Path("demo_restaurants.csv")


def normalize_places_to_schema(records: list[dict]) -> pd.DataFrame:
    rows = []
    for i, record in enumerate(records, start=1):
        rows.append({
            "restaurant_id": record.get("restaurant_id", i),
            "name": record.get("name", ""),
            "country": record.get("country", ""),
            "city": record.get("city", ""),
            "area": record.get("area", ""),
            "lat": record.get("lat"),
            "lon": record.get("lon"),
            "cuisines": record.get("cuisines", ""),
            "dietary_tags": record.get("dietary_tags", ""),
            "price_band": record.get("price_band", "medium"),
            "rating": record.get("rating"),
            "review_count": record.get("review_count", 0),
            "delivery_available": record.get("delivery_available", False),
            "dine_in_available": record.get("dine_in_available", True),
            "open_now": record.get("open_now", False),
        })
    return pd.DataFrame(rows)


def fetch_places_for_city(country: str, city: str) -> list[dict]:
    api_key = os.getenv("PLACES_API_KEY", "")
    if not api_key:
        raise RuntimeError("PLACES_API_KEY is not set. Add it as an environment variable or Streamlit secret.")

    # Replace this placeholder with real provider integration.
    # For now, return an empty list so the script is safe to run.
    return []


def main():
    cities = [
        ("Pakistan", "Lahore"),
        ("Pakistan", "Karachi"),
        ("Pakistan", "Islamabad"),
        ("UK", "London"),
        ("UK", "Manchester"),
        ("UK", "Birmingham"),
    ]

    all_records = []
    for country, city in cities:
        try:
            records = fetch_places_for_city(country, city)
            all_records.extend(records)
            print(f"Fetched {len(records)} records for {city}, {country}")
        except Exception as e:
            print(f"Skipping {city}, {country}: {e}")

    df = normalize_places_to_schema(all_records)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
