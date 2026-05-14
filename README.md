# TrafficAI - Smart Congestion Predictor

[![GitHub](https://img.shields.io/badge/GitHub-Manav5234/hackzilla-00ff88?style=flat&logo=github)](https://github.com/Manav5234/hackzilla)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-99.86%25_accuracy-EC1C24?style=flat&logo=xgboost)](https://xgboost.readthedocs.io)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

Real-time traffic congestion prediction for Indian cities using XGBoost, live weather, route comparison, and an AI chatbot.

---

## Quick Start

```bash
# Terminal 1 - Backend (port 8000)
cd backend && python main.py

# Terminal 2 - Frontend (port 5173)
cd frontend && npx vite --host 0.0.0.0 --port 5173

# Open in browser
open http://localhost:5173
```

---

## Features

| Feature | What it does |
|---------|-------------|
| **Traffic Prediction** | XGBoost model with 43 features predicts congestion score (0-100), risk level (Low/Medium/High), and top affected zones |
| **Live Heatmap** | 16 color-coded markers across Delhi-NCR, Mumbai, Bangalore, Chennai, Kolkata with live traffic data |
| **Route Comparator** | 3 route alternatives via OSRM - Fastest, Toll Free, and AI Recommended with duration, distance, and congestion warnings |
| **Weather Integration** | Real-time weather from Open-Meteo API - temperature, humidity, precipitation, wind speed, visibility |
| **AI Chatbot** | Groq-powered (Llama 3.3 70B) with Indian traffic knowledge; fallback mode with canned responses for common routes |
| **Event Mode** | Toggle simulation of congestion spikes from IPL matches, concerts, or other events (+25% boost) |

---

## Tech Stack

**Backend**
- FastAPI + Uvicorn
- XGBoost classifier
- pandas, numpy, joblib
- Open-Meteo (weather)
- OSRM (routing)
- Groq SDK (AI chat)

**Frontend**
- React 19 + Vite 8
- Leaflet + leaflet.heat
- CSS (dark theme)

**Model**
- XGBoost trained on 7,070 rows across 24 Indian locations
- 43 engineered features: time, weather, traffic volume, road type, location
- Accuracy: 99.86%

---

## API Endpoints

| Method | Path | Parameters | Response |
|--------|------|-----------|----------|
| `GET` | `/health` | - | `{status, model_loaded, features_count}` |
| `POST` | `/predict` | `{location, timestamp, vehicle_count, weather, road_type, speed_avg, rain_mm, incident_flag, event_active}` | `{congestion_score, risk_label, color_code, probability, top_congested_zones}` |
| `GET` | `/heatmap-data` | - | `{data: [{lat, lon, intensity, name, traffic_volume, speed_avg}], count}` |
| `GET` | `/routes` | `origin_lat, origin_lon, dest_lat, dest_lon` | `{routes: [{label, duration_min, distance_km, congestion_level, coordinates}]}` |
| `GET` | `/weather` | `lat, lon` | `{temperature_c, humidity, rain_mm, wind_speed_kmh, visibility_m, condition}` |
| `POST` | `/chat` | `{user_message}` | `{reply, source}` |

---

## Project Structure

```
hackzilla/
  backend/
    main.py           - FastAPI server with all endpoints
    .env              - API keys (GROQ_API_KEY, TOMTOM_API_KEY)
    requirements.txt  - Python dependencies
  frontend/
    src/
      components/     - React components (MapView, PredictPanel, RouteComparator, ChatBot, StatsBar, EventSpike)
      services/       - API client (api.js)
      App.jsx         - Root component
      App.css         - Dark theme styles
    index.html
    vite.config.js
    package.json
  model/
    xgb_traffic_model.pkl   - Trained XGBoost model
    feature_columns.json     - 43 feature names for preprocessing
    feature_importance.png   - Feature importance chart
    train.py                 - Training pipeline
  data/
    TrafficCongestion_MultiLocation_7000Rows.xlsx
    traffic_flow_supplement.csv
```

---

## Configuration

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
TOMTOM_API_KEY=your_tomtom_api_key_here
```

Set `GROQ_API_KEY` to enable the full AI chatbot. Leave as-is for fallback mode with built-in route responses.

---

## Model Details

Trained on **111,313 rows** across **6 combined datasets** covering 10 Indian cities and 170+ locations. Features include hour-of-day, day-of-week, peak hour flags, weather conditions, road type, vehicle composition (two-wheeler/car/heavy vehicle %), public transport density, visibility, temperature, cyclic time encoding, and vehicle-peak interaction. The XGBoost classifier uses 800 estimators with max depth 12, achieving **98.90% accuracy**.

**Datasets used:**
- advanced_indian_traffic_dataset (50,000 rows)
- ai_route_optimization_dataset (30,000 rows)
- indian_city_traffic_congestion_dataset (15,000 rows)
- India_Traffic_Dataset_10Cities (10,000 rows)
- TrafficCongestion_MultiLocation_7000Rows (7,000 rows)
- traffic_flow_supplement (350 rows)

## What's New

- **Route Drawing** — Click any route in the Route Comparator to draw it on the live map with start/end markers
- **Smart Time Estimation** — Vehicle count and speed auto-adjust based on time of day (early morning = few vehicles, peak hours = heavy traffic)
- **Haze & Arterial support** — Weather and road type options expanded to match real Indian conditions
- **Groq AI Chatbot** — Powered by Llama 3.3 70B for natural traffic conversations
- **Event Mode** — Toggle congestion spikes for IPL matches, concerts, and events
