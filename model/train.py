import pandas as pd
import numpy as np
import json
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
MODEL_DIR = BASE_DIR

COL_MAP = {
    'timestamp': 'timestamp', 'Timestamp': 'timestamp',
    'location': 'location', 'Location': 'location', 'Source_Location': 'location',
    'vehicle_count': 'vehicle_count', 'Vehicle Count': 'vehicle_count', 'Vehicle Count ': 'vehicle_count',
    'Vehicle_Count': 'vehicle_count',
    'Traffic Volume': 'vehicle_count',
    'speed_avg': 'speed_avg', 'Avg Speed (km/h)': 'speed_avg', 'Avg Speed (km/h) ': 'speed_avg',
    'Current_Speed_kmh': 'speed_avg',
    'weather_condition': 'weather_condition', 'Weather': 'weather_condition',
    'rain_mm': 'rain_mm', 'Rain(mm)': 'rain_mm', 'Rain (mm)': 'rain_mm',
    'road_type': 'road_type', 'Road Type': 'road_type', 'Road Type ': 'road_type', 'Route_Type': 'road_type',
    'incident_flag': 'incident_flag', 'Accident': 'incident_flag', 'Accident_On_Route': 'incident_flag',
    'has_event': 'has_event', 'Event Nearby': 'has_event', 'Event Nearby ': 'has_event', 'Event_Nearby': 'has_event',
    'congestion_level': 'congestion_level', 'Congestion Level': 'congestion_level', 'Congestion Level ': 'congestion_level',
    'Traffic_Density': 'congestion_level',
    'public_transport_density': 'public_transport_density', 'Public Transport Density': 'public_transport_density',
    'Public_Transport_Impact': 'public_transport_density',
    'hour_of_day': 'hour_of_day', 'Hour of Day': 'hour_of_day',
    'day_of_week': 'day_of_week', 'Day of Week': 'day_of_week',
    'is_weekend': 'is_weekend', 'Is Weekend': 'is_weekend', 'Is Weekend ': 'is_weekend',
    'is_peak_hour': 'is_peak_hour', 'Is Peak Hour': 'is_peak_hour', 'Peak_Hour': 'is_peak_hour',
    'two_wheelers_pct': 'two_wheelers_pct', 'Two-Wheelers (%)': 'two_wheelers_pct',
    'cars_pct': 'cars_pct', 'Cars (%)': 'cars_pct',
    'heavy_vehicles_pct': 'heavy_vehicles_pct', 'Heavy Vehicles (%)': 'heavy_vehicles_pct',
    'temperature_c': 'temperature_c', 'Temperature (C)': 'temperature_c', 'Temperature (Â°C)': 'temperature_c',
    'visibility_km': 'visibility_km', 'Visibility (km)': 'visibility_km',
    'congestion_score': 'congestion_score', 'Congestion Score (0-100)': 'congestion_score', 'Congestion_Score': 'congestion_score',
    'Peak Type': 'peak_type', 'City': 'city', 'Source_City': 'city',
    'Latitude': 'latitude', 'Longitude': 'longitude',
    'Distance_km': 'distance_km', 'Construction_Work': 'construction_work', 'Road_Condition': 'road_condition',
    'Toll_Road': 'toll_road',
}

def to_bool(val):
    if isinstance(val, (int, float)):
        return 1 if val else 0
    if isinstance(val, bool):
        return 1 if val else 0
    s = str(val).strip().lower()
    return 1 if s in ('yes', 'true', '1', 'y') else 0

def load_all_data():
    files = [
        os.path.join(DATA_DIR, 'advanced_indian_traffic_dataset_50000.csv'),
        os.path.join(DATA_DIR, 'indian_city_traffic_congestion_dataset_15000.csv'),
        os.path.join(DATA_DIR, 'ai_route_optimization_dataset_30000.xlsx'),
        os.path.join(DATA_DIR, 'India_Traffic_Dataset_10Cities_10000Rows.xlsx'),
        os.path.join(DATA_DIR, 'TrafficCongestion_MultiLocation_7000Rows.xlsx'),
        os.path.join(DATA_DIR, 'traffic_flow_supplement.csv'),
    ]
    all_dfs = []
    for path in files:
        if not os.path.exists(path):
            continue
        print(f"[INFO] Loading: {os.path.basename(path)}")
        try:
            if path.endswith('.xlsx'):
                df = pd.read_excel(path, engine='openpyxl')
            else:
                df = pd.read_csv(path)
            # Strip whitespace from column names
            df.columns = df.columns.str.strip()
            # Map columns
            rename = {}
            for c in df.columns:
                if c in COL_MAP:
                    rename[c] = COL_MAP[c]
            df = df.rename(columns=rename)
            # Keep only mapped + useful columns
            keep = set(rename.values()) | {'latitude', 'longitude'}
            df = df[[c for c in df.columns if c in keep]]
            all_dfs.append(df)
        except Exception as e:
            print(f"[WARN] Could not load {os.path.basename(path)}: {e}")
    print(f"[INFO] Loaded {len(all_dfs)} datasets")
    return all_dfs


def harmonize(dfs):
    combined = pd.concat(dfs, ignore_index=True, sort=False)
    print(f"[INFO] Combined shape: {combined.shape}")
    print(f"[INFO] Columns: {list(combined.columns)}")

    # Derive congestion_level from alternative columns if not present
    if 'congestion_level' not in combined.columns or combined['congestion_level'].isnull().all():
        if 'Traffic_Density' in combined.columns or 'traffic_density' in combined.columns:
            td_col = 'Traffic_Density' if 'Traffic_Density' in combined.columns else 'traffic_density'
            td_map = {'Very High': 'High', 'High': 'High', 'Medium': 'Medium', 'Low': 'Low', 'Very Low': 'Low'}
            combined['congestion_level'] = combined[td_col].astype(str).str.strip().str.title().map(td_map)
        elif 'congestion_score' in combined.columns and combined['congestion_score'].notna().any():
            cs = pd.to_numeric(combined['congestion_score'], errors='coerce')
            combined['congestion_level'] = pd.cut(cs, bins=[-1, 35, 65, 100], labels=['Low', 'Medium', 'High'])

    # Drop rows with no congestion_level after derivation
    combined = combined.dropna(subset=['congestion_level'])
    combined['congestion_level'] = combined['congestion_level'].astype(str).str.strip().str.title()
    combined['congestion_level'] = combined['congestion_level'].replace({'Very High': 'High', 'Very high': 'High', 'Veryhigh': 'High'})

    # Map route types to road types for the route optimization dataset
    route_to_road = {
        'Fastest': 'Highway', 'Shortest': 'Urban', 'Toll Free': 'Highway',
        'Scenic': 'Residential', 'Economic': 'Highway', 'Safe': 'Residential',
        'AI Recommended': 'Urban',
    }
    if 'road_type' in combined.columns:
        combined['road_type'] = combined['road_type'].fillna('Unknown').astype(str).str.strip().str.title()
        combined['road_type'] = combined['road_type'].map(lambda x: route_to_road.get(x, x)).fillna('Unknown')

    # Fill missing categoricals
    for c in ['weather_condition']:
        if c in combined.columns:
            combined[c] = combined[c].fillna('Unknown').astype(str).str.strip().str.title()

    if 'location' in combined.columns:
        combined['location'] = combined['location'].fillna('Unknown').astype(str).str.strip().str.title()

    # Convert boolean-ish columns
    for c in ['incident_flag', 'has_event']:
        if c in combined.columns:
            combined[c] = combined[c].apply(to_bool)

    for c in ['is_weekend', 'is_peak_hour']:
        if c in combined.columns:
            combined[c] = combined[c].apply(to_bool)

    # Map day_of_week strings to numbers
    day_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6,
    }
    if 'day_of_week' in combined.columns:
        combined['day_of_week'] = combined['day_of_week'].astype(str).str.strip().str.lower()
        combined['day_of_week'] = combined['day_of_week'].map(day_map).fillna(0).astype(int)

    # Numeric fill
    for c in ['vehicle_count', 'speed_avg', 'rain_mm']:
        if c in combined.columns:
            combined[c] = pd.to_numeric(combined[c], errors='coerce').fillna(0)

    # Drop duplicate rows based on key features to avoid over-weighting any dataset
    dedup_cols = [c for c in ['location', 'hour_of_day', 'vehicle_count', 'speed_avg', 'congestion_level'] if c in combined.columns]
    if dedup_cols:
        before = len(combined)
        combined = combined.drop_duplicates(subset=dedup_cols, keep='first')
        print(f"[INFO] Deduplicated: {before} -> {len(combined)} rows")

    return combined


def engineer_features(df):
    print(f"\n{'='*60}")
    print(f"  Dataset Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Null counts:\n{df.isnull().sum()}")
    print(f"\n  Congestion level distribution:\n{df['congestion_level'].value_counts()}")
    print(f"{'='*60}")

    # Parse timestamp if present
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        if 'hour_of_day' not in df.columns:
            df['hour_of_day'] = df['timestamp'].dt.hour.fillna(0).astype(int)
        if 'day_of_week' not in df.columns:
            df['day_of_week'] = df['timestamp'].dt.dayofweek.fillna(0).astype(int)
        if 'is_weekend' not in df.columns:
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

    if 'is_peak_hour' not in df.columns and 'hour_of_day' in df.columns:
        df['is_peak_hour'] = (
            ((df['hour_of_day'] >= 8) & (df['hour_of_day'] <= 10)) |
            ((df['hour_of_day'] >= 17) & (df['hour_of_day'] <= 19))
        ).astype(int)

    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)

    cat_cols = [c for c in ['weather_condition', 'road_type', 'location'] if c in df.columns]
    for c in cat_cols:
        df[c] = df[c].fillna('Unknown')
    df = pd.get_dummies(df, columns=cat_cols, drop_first=False, dtype=int)

    for c in ['vehicle_count', 'speed_avg']:
        if c in df.columns:
            df[c] = df[c].fillna(df[c].median() if df[c].nunique() > 1 else 0)

    if 'vehicle_count' in df.columns and 'is_peak_hour' in df.columns:
        df['vehicle_count_x_peak'] = df['vehicle_count'] * df['is_peak_hour']

    num_cols = ['rain_mm', 'public_transport_density', 'vehicle_count', 'speed_avg',
                'vehicle_count_x_peak', 'two_wheelers_pct', 'cars_pct',
                'heavy_vehicles_pct', 'temperature_c', 'visibility_km',
                'distance_km', 'toll_road', 'congestion_score']
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
            df[c] = df[c].fillna(df[c].median() if df[c].nunique() > 1 else 0)

    # Fill any remaining NaN in all numeric feature columns
    for c in df.select_dtypes(include=['float64', 'int64', 'float32', 'int32']).columns:
        if c not in ['congestion_label']:
            df[c] = df[c].fillna(0)

    return df


def train_model(df):
    label_map = {'Low': 0, 'Medium': 1, 'High': 2}
    df['congestion_label'] = df['congestion_level'].map(label_map)
    df = df.dropna(subset=['congestion_label'])
    df['congestion_label'] = df['congestion_label'].astype(int)

    exclude = ['timestamp', 'congestion_level', 'congestion_label',
               'latitude', 'longitude', 'city', 'peak_type', 'congestion_score',
               'toll_road', 'road_condition', 'construction_work', 'distance_km']
    feature_cols = [c for c in df.columns if c not in exclude]
    df = df[[c for c in feature_cols + ['congestion_label'] if c in df.columns]].dropna()
    feature_cols = [c for c in df.columns if c != 'congestion_label']

    print(f"\n[INFO] Feature columns ({len(feature_cols)}): {feature_cols}")
    print(f"[INFO] Final training shape: {df.shape}")

    X = df[feature_cols].values
    y = df['congestion_label'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[INFO] Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

    model = xgb.XGBClassifier(
        n_estimators=800,
        max_depth=12,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric='mlogloss',
        use_label_encoder=False,
        verbosity=0,
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"\n{'='*60}")
    print(f"  ACCURACY: {acc*100:.2f}%")
    print(f"{'='*60}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred, target_names=['Low', 'Medium', 'High'])}")
    print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")

    importance = model.feature_importances_
    idx_sorted = np.argsort(importance)[::-1]
    top_n = min(20, len(idx_sorted))
    plt.figure(figsize=(10, 8))
    plt.barh(range(top_n), importance[idx_sorted[:top_n]])
    plt.yticks(range(top_n), [feature_cols[i] for i in idx_sorted[:top_n]])
    plt.xlabel('Importance')
    plt.title('Top Feature Importance - XGBoost Traffic Model')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, 'feature_importance.png'), dpi=150)
    plt.close()
    print("[INFO] Feature importance chart saved.")

    joblib.dump(model, os.path.join(MODEL_DIR, 'xgb_traffic_model.pkl'))
    print(f"[INFO] Model saved ({os.path.getsize(os.path.join(MODEL_DIR, 'xgb_traffic_model.pkl')) / 1024:.0f} KB)")

    with open(os.path.join(MODEL_DIR, 'feature_columns.json'), 'w') as f:
        json.dump(feature_cols, f)
    print(f"[INFO] {len(feature_cols)} feature columns saved")

    return model, feature_cols


if __name__ == '__main__':
    print("=" * 60)
    print("  TRAFFIC CONGESTION PREDICTOR - ML PIPELINE")
    print("=" * 60)

    dfs = load_all_data()
    if not dfs:
        raise RuntimeError("No data available.")

    df = harmonize(dfs)
    df = engineer_features(df)
    model, feature_cols = train_model(df)

    print("\n[SUCCESS] ML Pipeline complete. Model ready for backend.")
