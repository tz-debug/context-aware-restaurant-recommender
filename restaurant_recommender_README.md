# Context-Aware Hybrid Restaurant Recommender for Pakistan and the UK

A starter MVP for a live-style restaurant recommender that supports Pakistan and the UK using location-aware, preference-aware ranking.

## Live Build Strategy

This project is designed to start with a cached restaurant catalog and then evolve into a production-style system with API ingestion and hybrid ranking.

### MVP included here
- Streamlit interface
- country and city filtering
- cuisine and dietary filters
- budget and dining mode controls
- location-aware ranking using distance
- weighted hybrid-style scoring using:
  - content match
  - rating
  - popularity
  - distance
  - budget fit
  - open-now signal
  - favorite restaurant boost

### Next production steps
- ingest restaurants from Google Places or Foursquare
- cache data in PostgreSQL or CSV snapshots
- add user accounts and interaction logging
- add collaborative filtering from ratings, clicks, and saves
- evaluate with ranking metrics such as Precision@K and NDCG@K

## Files

- `restaurant_recommender_mvp.py`
- `demo_restaurants.csv`
- `restaurant_recommender_README.md`
- `restaurant_recommender_requirements.txt`

## Run locally

```bash
pip install -r restaurant_recommender_requirements.txt
streamlit run restaurant_recommender_mvp.py
```

## CSV schema

Your restaurant dataset should include these columns:

- `restaurant_id`
- `name`
- `country`
- `city`
- `area`
- `lat`
- `lon`
- `cuisines`
- `dietary_tags`
- `price_band`
- `rating`
- `review_count`
- `delivery_available`
- `dine_in_available`
- `open_now`

## Notes on live APIs

A practical production version should fetch restaurant candidates from an official provider, then cache results locally so recommendation requests do not repeatedly hit external APIs. This reduces cost and makes the app faster and more stable.
