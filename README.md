# Context-Aware Restaurant Recommender

## Overview

This project implements a context-aware restaurant recommender system for Pakistan and the UK. It combines user preferences, restaurant features, and location-based filtering to generate personalized recommendations.

The system follows a hybrid recommendation approach using content-based signals (cuisine, dietary tags) and contextual factors such as distance, rating, popularity, and availability.

---

## Live Demo

Access the deployed application here:  
https://context-aware-restaurant-recommender.streamlit.app/

---

## Technology Stack

- Python  
- Streamlit  
- Pandas  
- NumPy  

---

## Features

- Location-based filtering (country, city, distance)
- Preference-based recommendations (cuisines, dietary tags)
- Budget and dining mode selection (delivery, dine-in)
- Real-time ranking with adjustable weights
- Explainable recommendations with reasoning
- Interactive map visualization
- Export recommendations as CSV
- Persona-based presets (e.g., Budget Student, Family Dining)

---

## Recommendation Logic

The system ranks restaurants using a weighted scoring model:

- Content match (cuisine and dietary alignment)
- Rating and popularity
- Distance from user
- Budget compatibility
- Availability (open now)
- User favourites

This design allows flexible tuning of recommendation behavior and supports both experimentation and practical applications.

---

## Dataset

The application uses a structured dataset with restaurants across:

- Pakistan: Lahore, Karachi, Islamabad  
- UK: London, Manchester, Birmingham  

Each record includes:

- Location (latitude, longitude, city, area)
- Cuisine and dietary tags
- Ratings and review counts
- Availability (delivery, dine-in, open now)
- Price band

---

## Limitations

- Uses a static dataset without live API integration
- No collaborative filtering implemented
- No persistent user profiles
- Recommendation quality depends on dataset size and quality

---

## Future Improvements

- Integration with Google Places or Foursquare APIs
- Automated data ingestion pipeline
- Collaborative filtering and personalization
- Learning-to-rank models
- User authentication and saved preferences
- Evaluation metrics and A/B testing

---

## Purpose

This project demonstrates:

- End-to-end design of a recommendation system
- Context-aware ranking and feature engineering
- Deployment of interactive data applications using Streamlit
- Practical application of machine learning concepts

It is suitable for both industry portfolios and academic exploration in recommender systems.
