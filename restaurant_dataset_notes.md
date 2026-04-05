# Restaurant dataset upgrade notes

This package contains:

- `demo_restaurants.csv` with 184 starter rows across:
  - Pakistan: Lahore, Karachi, Islamabad
  - UK: London, Manchester, Birmingham
- `restaurant_api_ingestion_stub.py` as a starter ingestion structure for future live API integration

## Why this improves recommendations

The recommender performs better when it has:
- more restaurants per city
- more cuisine variety
- richer area coverage
- more realistic rating and popularity spread

## Important note

This expanded CSV is a **starter development dataset** for testing ranking, filtering, and deployment.
It is not a verified live catalog.

## Recommended next step

Use this dataset now for a stronger deployed MVP, then later replace or refresh it using an ingestion script that caches data from an official provider.
