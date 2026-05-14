# TrafficAI - Smart Congestion Predictor

[![GitHub](https://img.shields.io/badge/GitHub-Manav5234/hackzilla-00ff88?style=flat&logo=github)](https://github.com/Manav5234/hackzilla)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-98.9%25_accuracy-EC1C24?style=flat&logo=xgboost)](https://xgboost.readthedocs.io)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

Real-time traffic congestion prediction for Indian cities using XGBoost (98.9% accuracy), live weather, route comparison, and a Groq AI chatbot.

**Live Preview:** `http://localhost:5173` (after running both servers)

---

## Quick Start

```bash
# Terminal 1 - Backend (port 8000)
cd backend
python main.py

# Terminal 2 - Frontend (port 5173)
cd frontend
npx vite --host 0.0.0.0 --port 5173

# Open in browser
http://localhost:5173
```

---

## Features

| Feature | What it does |
|---------|-------------|
| **Traffic Prediction** | XGBoost model with 264 features predicts congestion score (0-100), risk level (Low/Medium/High), and top affected zones. Vehicle count and speed auto-adjust based on time of day |
| **Live Heatmap** | 170+ color-coded markers across 10 Indian cities (Delhi, Mumbai, Bangalore, Chennai, Hyderabad, Pune, Kolkata, Ahmedabad, Jaipur, Surat) with live traffic data |
| **Route Comparator** | 3 route alternatives via OSRM - Fastest, Toll Free, and AI Recommended. **Click any route to draw it on the map** with colored polyline and start/end markers |
| **Weather Integration** | Real-time weather from Open-Meteo API - temperature, humidity, precipitation, wind speed, visibility |
| **AI Chatbot** | Groq-powered (Llama 3.3 70B) with Indian traffic knowledge. Ask about NH48, Delhi-Noida routes, Bangalore traffic, and more |
| **Event Mode** | Toggle simulation of congestion spikes from IPL matches, concerts, or other events (+25% boost) |

---

## Tech Stack

**Backend**
- FastAPI + Uvicorn
- XGBoost classifier (800 estimators, depth 12)
- pandas, numpy, joblib
- Open-Meteo (weather), OSRM (routing), Groq SDK (AI chat)

**Frontend**
- React 19 + Vite 8
- Leaflet + leaflet.heat
- Custom dark theme CSS

---

## Model

Trained on **111,313 rows** across **6 combined datasets** covering 10 Indian cities and 170+ locations.

- **264 features:** hour-of-day, day-of-week, peak hour flags, weather conditions, road type, vehicle composition (2-wheeler/car/heavy %), public transport density, visibility, temperature, cyclic time encoding, vehicle-peak interaction
- **Accuracy:** 98.90% on test data (22,263 samples)
- **Confusion Matrix:** Low 99.6% recall, Medium 98.5%, High 98.8%

**Datasets used:**
| Dataset | Rows |
|---------|------|
| advanced_indian_traffic_dataset | 50,000 |
| ai_route_optimization_dataset | 30,000 |
| indian_city_traffic_congestion_dataset | 15,000 |
| India_Traffic_Dataset_10Cities | 10,000 |
| TrafficCongestion_MultiLocation | 7,000 |
| traffic_flow_supplement | 350 |

---

## API Endpoints

| Method | Path | Parameters | Response |
|--------|------|-----------|----------|
| `GET` | `/health` | - | `{status, model_loaded, features_count}` |
| `POST` | `/predict` | `{location, timestamp, weather, road_type, ...}` | `{congestion_score, risk_label, color_code, probability, top_congested_zones}` |
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
    .env              - API keys (GROQ_API_KEY)
    requirements.txt  - Python dependencies
  frontend/
    src/
      components/     - MapView, PredictPanel, RouteComparator, ChatBot, StatsBar, EventSpike
      services/       - API client (api.js)
      App.jsx         - Root component
      App.css         - Dark theme styles
    index.html
    vite.config.js
    package.json
  model/
    xgb_traffic_model.pkl   - Trained XGBoost model (17 MB)
    feature_columns.json     - 264 feature names
    feature_importance.png   - Feature importance chart
    train.py                 - Training pipeline (handles all 6 datasets)
  data/                       - 6 datasets (111k total rows)
```

---

## Configuration

```env
# backend/.env
GROQ_API_KEY=your_groq_api_key_here
```

Set `GROQ_API_KEY` to enable the full AI chatbot (free at console.groq.com). Leave as-is for fallback mode with built-in route responses.

---

## Recent Updates

- **Route Drawing** — Click any route card in the Route Comparator to draw the path on the interactive map with colored polyline and start/end markers. Map auto-fits to show the full route
- **Smart Time Estimation** — Vehicle count and speed auto-calculate based on time of day (1 AM = 15 vehicles / 65 km/h, 9 AM peak = 350 vehicles / 30 km/h)
- **111k Row Model** — Combined 6 datasets, 264 features, 170+ locations, 98.9% accuracy
- **Haze & Arterial** — Weather options include Haze, road types include Arterial
- **Active Route Highlight** — Selected route card glows green, others dim for clear comparison
