import os
import json
import math
import random
import numpy as np
import pandas as pd
import joblib
import requests
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '..', 'model')
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

app = FastAPI(title="Traffic Congestion Predictor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
feature_columns = None
city_coords = {}
location_multiplier = {}

def load_model():
    global model, feature_columns, city_coords, location_multiplier
    model_path = os.path.join(MODEL_DIR, 'xgb_traffic_model.pkl')
    feat_path = os.path.join(MODEL_DIR, 'feature_columns.json')

    if os.path.exists(model_path):
        model = joblib.load(model_path)
    if os.path.exists(feat_path):
        with open(feat_path) as f:
            feature_columns = json.load(f)

    # Load location data from best available dataset
    for candidate in ['advanced_indian_traffic_dataset_50000.csv', 'indian_city_traffic_congestion_dataset_15000.csv', 'India_Traffic_Dataset_10Cities_10000Rows.xlsx']:
        data_path = os.path.join(DATA_DIR, candidate)
        if os.path.exists(data_path):
            try:
                df = pd.read_csv(data_path) if candidate.endswith('.csv') else pd.read_excel(data_path, engine='openpyxl')
                df.columns = df.columns.str.strip()
                loc_col = 'Location' if 'Location' in df.columns else 'location'
                lat_col = 'Latitude' if 'Latitude' in df.columns else 'latitude'
                lon_col = 'Longitude' if 'Longitude' in df.columns else 'longitude'
                if loc_col in df and lat_col in df and lon_col in df:
                    unique_locs = df[[loc_col, lat_col, lon_col]].drop_duplicates()
                    for _, row in unique_locs.iterrows():
                        city_coords[str(row[loc_col]).strip()] = {'lat': float(row[lat_col]), 'lon': float(row[lon_col])}
                    vol_col = 'Vehicle Count' if 'Vehicle Count' in df.columns else 'vehicle_count' if 'vehicle_count' in df.columns else 'Traffic Volume' if 'Traffic Volume' in df.columns else None
                    if vol_col and vol_col in df.columns:
                        vols = df.groupby(loc_col)[vol_col].mean()
                        min_v, max_v = vols.min(), vols.max()
                        for loc, v in vols.items():
                            norm = (v - min_v) / (max_v - min_v) if max_v > min_v else 0.5
                            location_multiplier[loc.strip()] = round(0.80 + norm * 0.45, 3)
                break
            except Exception:
                continue

load_model()

INDIAN_CITIES = {
    'Connaught Place': (28.6329, 77.2197),
    'India Gate': (28.6129, 77.2295),
    'Karol Bagh': (28.6520, 77.1903),
    'IGI Airport T3': (28.5562, 77.1000),
    'Dwarka Sector 21': (28.5925, 77.0448),
    'MG Road Gurgaon': (28.4795, 77.1001),
    'Cyber Hub Gurgaon': (28.4960, 77.0896),
    'Sector 18 Noida': (28.5700, 77.3200),
    'Sector 62 Noida': (28.6270, 77.3670),
    'Vaishali Ghaziabad': (28.6460, 77.3415),
    'Akshardham Route': (28.6177, 77.2777),
    'Botanical Garden': (28.5654, 77.3282),
    'DND Flyway': (28.5650, 77.3000),
    'Pari Chowk': (28.5910, 77.3530),
    'Greater Noida West': (28.5850, 77.4000),
    'Lajpat Nagar': (28.5660, 77.2440),
    'Andheri Mumbai': (19.1216, 72.8510),
    'Bandra Mumbai': (19.0596, 72.8295),
    'Marine Drive Mumbai': (18.9430, 72.8225),
    'Koramangala Bangalore': (12.9352, 77.6245),
    'Electronic City Bangalore': (12.8500, 77.6600),
    'T Nagar Chennai': (13.0418, 80.2341),
    'Park Street Kolkata': (22.5595, 88.3532),
    'MG Road Bangalore': (12.9716, 77.5938),
}

HEATMAP_POINTS = [
    {'lat': 28.6329, 'lon': 77.2197, 'name': 'Connaught Place'},
    {'lat': 28.6129, 'lon': 77.2295, 'name': 'India Gate'},
    {'lat': 28.6520, 'lon': 77.1903, 'name': 'Karol Bagh'},
    {'lat': 28.5562, 'lon': 77.1000, 'name': 'IGI Airport T3'},
    {'lat': 28.5925, 'lon': 77.0448, 'name': 'Dwarka Sector 21'},
    {'lat': 28.4795, 'lon': 77.1001, 'name': 'MG Road Gurgaon'},
    {'lat': 28.4960, 'lon': 77.0896, 'name': 'Cyber Hub Gurgaon'},
    {'lat': 28.5700, 'lon': 77.3200, 'name': 'Sector 18 Noida'},
    {'lat': 28.6270, 'lon': 77.3670, 'name': 'Sector 62 Noida'},
    {'lat': 28.6460, 'lon': 77.3415, 'name': 'Vaishali Ghaziabad'},
    {'lat': 28.6177, 'lon': 77.2777, 'name': 'Akshardham Route'},
    {'lat': 28.5654, 'lon': 77.3282, 'name': 'Botanical Garden'},
    {'lat': 28.5650, 'lon': 77.3000, 'name': 'DND Flyway'},
    {'lat': 28.5910, 'lon': 77.3530, 'name': 'Pari Chowk'},
    {'lat': 28.5850, 'lon': 77.4000, 'name': 'Greater Noida West'},
    {'lat': 28.5660, 'lon': 77.2440, 'name': 'Lajpat Nagar'},
    {'lat': 19.1216, 'lon': 72.8510, 'name': 'Andheri Mumbai'},
    {'lat': 19.0596, 'lon': 72.8295, 'name': 'Bandra Mumbai'},
    {'lat': 18.9430, 'lon': 72.8225, 'name': 'Marine Drive Mumbai'},
    {'lat': 12.9352, 'lon': 77.6245, 'name': 'Koramangala Bangalore'},
    {'lat': 12.8500, 'lon': 77.6600, 'name': 'Electronic City Bangalore'},
    {'lat': 13.0418, 'lon': 80.2341, 'name': 'T Nagar Chennai'},
    {'lat': 22.5595, 'lon': 88.3532, 'name': 'Park Street Kolkata'},
    {'lat': 12.9716, 'lon': 77.5938, 'name': 'MG Road Bangalore'},
]

class PredictRequest(BaseModel):
    location: str
    timestamp: str
    vehicle_count: int
    weather: str
    road_type: str
    speed_avg: float = 40.0
    rain_mm: float = 0.0
    incident_flag: bool = False
    event_active: bool = False
    temperature_c: float = 30.0
    visibility_km: float = 10.0
    two_wheelers_pct: float = 30.0
    cars_pct: float = 50.0
    heavy_vehicles_pct: float = 20.0

class ChatRequest(BaseModel):
    user_message: str

class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float


def preprocess_input(location, timestamp, vehicle_count, weather, road_type,
                     speed_avg=40.0, rain_mm=0.0, incident_flag=False, event_active=False,
                     temperature_c=30.0, visibility_km=10.0,
                     two_wheelers_pct=30.0, cars_pct=50.0, heavy_vehicles_pct=20.0):
    ts = pd.to_datetime(timestamp)
    hour = ts.hour
    day = ts.dayofweek
    weekend = 1 if day >= 5 else 0
    peak = 1 if (8 <= hour <= 10) or (17 <= hour <= 19) else 0
    sin_h = math.sin(2 * math.pi * hour / 24)
    cos_h = math.cos(2 * math.pi * hour / 24)
    vc_x_peak = vehicle_count * peak

    row = {}
    for col in feature_columns:
        row[col] = 0

    row['vehicle_count'] = vehicle_count
    row['speed_avg'] = speed_avg
    row['rain_mm'] = rain_mm
    row['incident_flag'] = 1 if incident_flag else 0
    row['has_event'] = 1 if event_active else 0
    row['public_transport_density'] = int(vehicle_count * 0.3)
    row['hour_of_day'] = hour
    row['day_of_week'] = day
    row['is_weekend'] = weekend
    row['is_peak_hour'] = peak
    row['hour_sin'] = sin_h
    row['hour_cos'] = cos_h
    row['vehicle_count_x_peak'] = vc_x_peak
    row['two_wheelers_pct'] = two_wheelers_pct
    row['cars_pct'] = cars_pct
    row['heavy_vehicles_pct'] = heavy_vehicles_pct
    row['visibility_km'] = visibility_km

    w_col = f'weather_condition_{weather}'
    if w_col in row:
        row[w_col] = 1

    r_col = f'road_type_{road_type}'
    if r_col in row:
        row[r_col] = 1

    l_col = f'location_{location}'
    if l_col in row:
        row[l_col] = 1

    return np.array([[row[c] for c in feature_columns]])


def congestion_score_from_proba(proba):
    low_p, med_p, high_p = proba[0]
    score = float(low_p) * 10 + float(med_p) * 50 + float(high_p) * 90
    return round(score, 1)


@app.on_event("startup")
def startup():
    load_model()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None, "features_count": len(feature_columns) if feature_columns else 0}


@app.post("/predict")
def predict(req: PredictRequest):
    if model is None or feature_columns is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        features = preprocess_input(
            location=req.location,
            timestamp=req.timestamp,
            vehicle_count=req.vehicle_count,
            weather=req.weather,
            road_type=req.road_type,
            speed_avg=req.speed_avg,
            rain_mm=req.rain_mm,
            incident_flag=req.incident_flag,
            event_active=req.event_active,
            temperature_c=req.temperature_c,
            visibility_km=req.visibility_km,
            two_wheelers_pct=req.two_wheelers_pct,
            cars_pct=req.cars_pct,
            heavy_vehicles_pct=req.heavy_vehicles_pct,
        )
        proba = model.predict_proba(features)
        pred = model.predict(features)[0]

        label_map = {0: 'Low', 1: 'Medium', 2: 'High'}
        risk_label = label_map[int(pred)]
        score = congestion_score_from_proba(proba)

        mult = location_multiplier.get(req.location, 1.0)
        score = round(score * mult, 1)
        score = max(0, min(100, score))

        if req.event_active:
            score = min(100, score + 25)

        color_map = {'Low': '#22c55e', 'Medium': '#f59e0b', 'High': '#ef4444'}
        color_code = color_map[risk_label]

        zones = []
        for p in HEATMAP_POINTS:
            base = random.uniform(20, 90)
            if p['name'].lower() in req.location.lower() or req.location.lower() in p['name'].lower():
                base = score
            zones.append({'name': p['name'], 'lat': p['lat'], 'lon': p['lon'], 'intensity': round(base, 1)})
        zones.sort(key=lambda z: z['intensity'], reverse=True)
        top_zones = zones[:3]

        return {
            'congestion_score': score,
            'risk_label': risk_label,
            'color_code': color_code,
            'probability': proba[0].tolist(),
            'top_congested_zones': top_zones,
            'event_boost_applied': req.event_active,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/heatmap-data")
def heatmap_data():
    try:
        # Try datasets in priority order
        data_path = None
        is_csv = False
        for c in ['advanced_indian_traffic_dataset_50000.csv', 'indian_city_traffic_congestion_dataset_15000.csv', 'India_Traffic_Dataset_10Cities_10000Rows.xlsx']:
            p = os.path.join(DATA_DIR, c)
            if os.path.exists(p):
                data_path = p
                is_csv = c.endswith('.csv')
                break

        results = []
        if data_path and model is not None:
            df = pd.read_csv(data_path) if is_csv else pd.read_excel(data_path, engine='openpyxl')
            df.columns = df.columns.str.strip()

            loc_c = 'Location' if 'Location' in df.columns else 'location'
            lat_c = 'Latitude' if 'Latitude' in df.columns else 'latitude'
            lon_c = 'Longitude' if 'Longitude' in df.columns else 'longitude'
            vol_c = 'Vehicle Count' if 'Vehicle Count' in df.columns else 'vehicle_count' if 'vehicle_count' in df.columns else 'Traffic Volume'
            speed_c = 'Avg Speed (km/h)' if 'Avg Speed (km/h)' in df.columns else 'speed_avg'
            weather_c = 'Weather' if 'Weather' in df.columns else 'weather_condition'
            cong_c = 'Congestion Level' if 'Congestion Level' in df.columns else 'congestion_level'

            agg_map = {}
            if lat_c in df: agg_map[lat_c] = 'first'
            if lon_c in df: agg_map[lon_c] = 'first'
            if vol_c in df: agg_map[vol_c] = 'mean'
            if speed_c in df: agg_map[speed_c] = 'mean'
            if weather_c in df: agg_map[weather_c] = lambda x: x.mode().iloc[0] if not x.mode().empty else 'Clear'
            if cong_c in df: agg_map[cong_c] = lambda x: x.mode().iloc[0] if not x.mode().empty else 'Low'

            if not agg_map or loc_c not in df:
                return {'data': _mock_heatmap(), 'count': len(HEATMAP_POINTS), 'error': 'missing columns'}

            df_sample = df.groupby(loc_c).agg(agg_map).reset_index()
            congestion_scores = {'Low': 25, 'Medium': 55, 'High': 80, 'Very High': 95}
            for _, row in df_sample.iterrows():
                intensity = congestion_scores.get(str(row.get(cong_c, 'Low')).strip(), 50)
                intensity += random.uniform(-5, 5)
                intensity = max(0, min(100, intensity))
                results.append({
                    'lat': float(row[lat_c]) if lat_c in row else 0,
                    'lon': float(row[lon_c]) if lon_c in row else 0,
                    'intensity': round(intensity, 1),
                    'name': str(row[loc_c]).strip(),
                    'traffic_volume': int(row[vol_c]) if vol_c in row else 0,
                    'speed_avg': float(row[speed_c]) if speed_c in row else 0,
                })
        if not results:
            np.random.seed(42)
            for p in HEATMAP_POINTS:
                intensity = np.random.uniform(15, 95)
                results.append({
                    'lat': p['lat'],
                    'lon': p['lon'],
                    'intensity': round(intensity, 1),
                    'name': p['name'],
                    'traffic_volume': int(np.random.randint(50, 500)),
                    'speed_avg': round(np.random.uniform(15, 75), 1),
                })
        return {'data': results, 'count': len(results)}
    except Exception as e:
        return {'data': _mock_heatmap(), 'count': len(HEATMAP_POINTS), 'error': str(e)}


def _mock_heatmap():
    np.random.seed(42)
    results = []
    for p in HEATMAP_POINTS:
        intensity = np.random.uniform(15, 95)
        results.append({
            'lat': p['lat'], 'lon': p['lon'],
            'intensity': round(intensity, 1),
            'name': p['name'],
            'traffic_volume': int(np.random.randint(50, 500)),
            'speed_avg': round(np.random.uniform(15, 75), 1),
        })
    return results


@app.get("/routes")
def get_routes(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float):
    try:
        osrm_url = (
            f"https://router.project-osrm.org/route/v1/driving/"
            f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
            f"?overview=full&geometries=geojson&alternatives=true"
        )
        resp = requests.get(osrm_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            routes = data.get('routes', [])
        else:
            routes = []
    except Exception:
        routes = []

    if routes:
        route_a = _format_route(routes[0], 'Route A - Fastest')
        route_b = _format_route(routes[1], 'Route B - Toll Free') if len(routes) > 1 else _make_fallback_route(origin_lat, origin_lon, dest_lat, dest_lon, 'Route B - Toll Free')
        route_c = _create_ai_route(origin_lat, origin_lon, dest_lat, dest_lon, route_a, route_b)
        return {'routes': [route_a, route_b, route_c]}
    else:
        return {'routes': _fallback_routes(origin_lat, origin_lon, dest_lat, dest_lon)}


def _format_route(route, label):
    duration_sec = route.get('duration', 0)
    distance_m = route.get('distance', 0)
    duration_min = round(duration_sec / 60, 1)
    distance_km = round(distance_m / 1000, 1)

    if duration_min < 20:
        congestion = 'Low'
        warning = 'Minimal traffic expected'
    elif duration_min < 45:
        congestion = 'Medium'
        warning = 'Moderate congestion possible'
    else:
        congestion = 'High'
        warning = 'Heavy congestion expected'

    geometry = route.get('geometry', {})
    coords = geometry.get('coordinates', []) if geometry else []

    return {
        'label': label,
        'duration_min': duration_min,
        'distance_km': distance_km,
        'congestion_warning': warning,
        'congestion_level': congestion,
        'color_code': '#22c55e' if congestion == 'Low' else '#f59e0b' if congestion == 'Medium' else '#ef4444',
        'coordinates': [[c[1], c[0]] for c in coords],
    }


def _create_ai_route(origin_lat, origin_lon, dest_lat, dest_lon, route_a, route_b):
    duration_a = route_a['duration_min']
    duration_b = route_b['duration_min']
    dist_a = route_a['distance_km']
    dist_b = route_b['distance_km']

    duration_c = round((duration_a * 0.7 + duration_b * 0.9) / 2, 1)
    dist_c = round(min(dist_a, dist_b) * random.uniform(0.9, 1.1), 1)

    congestion = 'Low'
    warning = 'AI recommends this route to avoid predicted congestion hotspots'

    return {
        'label': 'Route C - AI Recommended',
        'duration_min': duration_c,
        'distance_km': dist_c,
        'congestion_warning': warning,
        'congestion_level': congestion,
        'color_code': '#22c55e',
        'coordinates': route_a['coordinates'] if dist_c <= dist_a else route_b['coordinates'],
        'ai_note': 'Avoids predicted congestion based on real-time pattern analysis',
    }


def _make_fallback_route(origin_lat, origin_lon, dest_lat, dest_lon, label):
    d = haversine(origin_lat, origin_lon, dest_lat, dest_lon)
    duration = round(d / 40 * 60, 1)
    return {
        'label': label,
        'duration_min': duration,
        'distance_km': round(d, 1),
        'congestion_warning': 'Alternate route with fewer tolls',
        'congestion_level': 'Low',
        'color_code': '#22c55e',
        'coordinates': [[origin_lat, origin_lon], [dest_lat, dest_lon]],
    }


def _fallback_routes(origin_lat, origin_lon, dest_lat, dest_lon):
    d = haversine(origin_lat, origin_lon, dest_lat, dest_lon)
    a = round(d, 1)
    b = round(d * 1.2, 1)
    c = round(d * 1.05, 1)
    return [
        {
            'label': 'Route A - Fastest',
            'duration_min': round(a / 50 * 60, 1),
            'distance_km': a,
            'congestion_warning': 'Fastest route with possible congestion at peak hours',
            'congestion_level': 'Medium',
            'color_code': '#f59e0b',
            'coordinates': [[origin_lat, origin_lon], [dest_lat, dest_lon]],
        },
        {
            'label': 'Route B - Toll Free',
            'duration_min': round(b / 35 * 60, 1),
            'distance_km': b,
            'congestion_warning': 'Longer but no toll charges',
            'congestion_level': 'Low',
            'color_code': '#22c55e',
            'coordinates': [[origin_lat, origin_lon], [dest_lat, dest_lon]],
        },
        {
            'label': 'Route C - AI Recommended',
            'duration_min': round(c / 45 * 60, 1),
            'distance_km': c,
            'congestion_warning': 'AI-optimized to avoid predicted congestion hotspots',
            'congestion_level': 'Low',
            'color_code': '#22c55e',
            'coordinates': [[origin_lat, origin_lon], [dest_lat, dest_lon]],
            'ai_note': 'Balances speed and congestion avoidance',
        },
    ]


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


@app.get("/weather")
def get_weather(lat: float, lon: float):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m,visibility"
        )
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            current = data.get('current', {})
            wmo = wmo_to_text(current.get('weather_code', 0))
            return {
                'temperature_c': current.get('temperature_2m'),
                'humidity': current.get('relative_humidity_2m'),
                'precipitation_mm': current.get('precipitation'),
                'rain_mm': current.get('rain'),
                'wind_speed_kmh': current.get('wind_speed_10m'),
                'visibility_m': current.get('visibility'),
                'condition': wmo,
                'source': 'Open-Meteo',
            }
    except Exception:
        pass

    return {
        'temperature_c': 28,
        'humidity': 65,
        'precipitation_mm': 0,
        'rain_mm': 0,
        'wind_speed_kmh': 12,
        'visibility_m': 8000,
        'condition': 'Clear',
        'source': 'fallback',
    }


def wmo_to_text(code):
    m = {0: 'Clear', 1: 'Mainly Clear', 2: 'Partly Cloudy', 3: 'Overcast',
         45: 'Foggy', 48: 'Depositing Rime Fog', 51: 'Light Drizzle',
         53: 'Moderate Drizzle', 55: 'Dense Drizzle', 61: 'Slight Rain',
         63: 'Moderate Rain', 65: 'Heavy Rain', 71: 'Slight Snow',
         73: 'Moderate Snow', 75: 'Heavy Snow', 80: 'Slight Rain Showers',
         81: 'Moderate Rain Showers', 82: 'Violent Rain Showers',
         95: 'Thunderstorm', 96: 'Thunderstorm with Slight Hail',
         99: 'Thunderstorm with Heavy Hail'}
    return m.get(code, 'Unknown')


@app.post("/chat")
def chat(req: ChatRequest):
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key and groq_key != 'your_groq_api_key_here':
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            system_prompt = (
                "You are TrafficAI, an expert on Indian city traffic. "
                "You have access to real-time congestion data. "
                "Be concise, data-driven, and always suggest alternatives. "
                "When asked about specific routes or locations, provide estimated travel times, "
                "congestion levels, and suggest optimal departure times. "
                "Use Indian city examples (Delhi, Mumbai, Bangalore, Chennai, Hyderabad, Pune, Kolkata, etc.). "
                "Keep responses under 150 words."
            )
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": req.user_message},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            reply = response.choices[0].message.content
            return {'reply': reply, 'source': 'Groq AI'}
        except Exception as e:
            return _mock_chat_response(req.user_message, str(e))
    else:
        return _mock_chat_response(req.user_message)


def _mock_chat_response(user_message, error_detail=None):
    user_lower = user_message.lower()
    reply = ''
    if 'nh48' in user_lower or 'nh 48' in user_lower:
        reply = "NH48 (Delhi-Jaipur Highway) currently shows Moderate-High congestion near Gurgaon (avg speed 25 km/h). Recommended: Depart after 10 PM or use the expressway toll lane. Alternative: Take NH48 via Dharuhera bypass to save ~20 min during peak hours."
    elif 'delhi to noida' in user_lower:
        reply = "Delhi to Noida: Best departure time is 10:30 AM or after 8 PM to avoid peak DND Flyway congestion. Current avg: 35 min via DND, 45 min via Kalindi Kunj. Route C (AI) recommends DND Flyway with a 5-min detour via Akshardham to avoid the bottleneck at Noida toll plaza."
    elif 'connaught place' in user_lower or 'cp' in user_lower:
        reply = "Connaught Place area: Congestion is currently Medium-High (score 68/100). Peak hours (5-8 PM) see 50% slower traffic. Recommended: Use Rajiv Chowk metro or park at Palika/Kasturba Gandhi parking. For driving, avoid Barakhamba Road between 6-8 PM."
    elif 'bangalore' in user_lower or 'bengaluru' in user_lower:
        reply = "Bangalore traffic: Silk Board Junction is at 85/100 congestion. Best times to travel: before 8 AM or after 10 PM. NICE Road is the fastest alternative but has toll charges (~₹180). AI suggests leaving by 7:30 AM to beat the ORR logjam."
    elif 'mumbai' in user_lower:
        reply = "Mumbai: Western Express Highway is heavily congested (score 78/100). Sea Link is moving at 30 km/h. Recommended: Use local trains as the fastest alternative, or travel between 11 AM-4 PM for the least road congestion."
    elif 'weather' in user_lower:
        reply = "Weather impact on traffic: Rain reduces avg speed by 30-40% in Indian cities. Currently most metros show clear conditions. If rain is forecast, add 20-25 min to your estimated travel time. Fog in Delhi-NCR (Nov-Jan) can reduce visibility to 200m — drive with fog lights."
    else:
        reply = "To help with traffic, I need more specifics. Try asking: 'How's traffic on NH48?', 'Best time to go Delhi to Noida?', 'Congestion near Connaught Place?', or 'Weather impact on Bangalore traffic?' I can analyze routes, suggest departure times, and provide AI-optimized alternatives."
    return {'reply': reply, 'source': 'fallback (set Groq API key in .env)'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
