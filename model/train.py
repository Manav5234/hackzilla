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


def load_data():
    main_path = os.path.join(DATA_DIR, 'TrafficCongestion_MultiLocation_7000Rows.xlsx')
    sample_path = os.path.join(DATA_DIR, 'TrafficCongestion_Sample_Dataset.xlsx')
    supp_path = os.path.join(DATA_DIR, 'traffic_flow_supplement.csv')

    df_main = None
    if os.path.exists(main_path):
        print(f"[INFO] Loading main dataset: {main_path}")
        df_main = pd.read_excel(main_path, engine='openpyxl')
    elif os.path.exists(sample_path):
        print(f"[INFO] Main not found. Loading sample: {sample_path}")
        df_main = pd.read_excel(sample_path, engine='openpyxl')
    else:
        print("[WARN] No Excel dataset found.")

    df_supp = None
    if os.path.exists(supp_path):
        print(f"[INFO] Loading supplementary dataset: {supp_path}")
        df_supp = pd.read_csv(supp_path)
    else:
        print("[WARN] Supplementary CSV not found.")

    return df_main, df_supp


def harmonize_main(df_main):
    keep_cols = ['Timestamp', 'Location', 'Traffic Volume', 'Avg Speed (km/h)',
                 'Weather', 'Rain(mm)', 'Accident', 'Congestion Level',
                 'Latitude', 'Longitude']
    df_main = df_main[[c for c in keep_cols if c in df_main.columns]].copy()
    col_map = {
        'Timestamp': 'timestamp',
        'Location': 'location',
        'Traffic Volume': 'vehicle_count',
        'Avg Speed (km/h)': 'speed_avg',
        'Weather': 'weather_condition',
        'Rain(mm)': 'rain_mm',
        'Accident': 'incident_flag',
        'Congestion Level': 'congestion_level'
    }
    df = df_main.rename(columns=col_map).copy()
    df['congestion_level'] = df['congestion_level'].replace({'Very High': 'High'})
    df['road_type'] = 'Unknown'
    df['has_event'] = 0
    df['public_transport_density'] = 0
    return df


def harmonize_supp(df_supp):
    keep_cols = ['timestamp', 'location', 'vehicle_count', 'congestion_level',
                 'road_type', 'speed_avg']
    df_supp = df_supp[[c for c in keep_cols if c in df_supp.columns]].copy()
    df = df_supp.copy()
    df['weather_condition'] = 'Clear'
    df['rain_mm'] = 0
    df['incident_flag'] = 0
    df['has_event'] = 0
    df['public_transport_density'] = (df['vehicle_count'] * 0.3).astype(int)
    return df


def engineer_features(df):
    print(f"\n{'='*60}")
    print(f"  Dataset Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Null counts:\n{df.isnull().sum()}")
    print(f"\n  Congestion level distribution:\n{df['congestion_level'].value_counts()}")
    print(f"{'='*60}")

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['hour_of_day'] = df['timestamp'].dt.hour.fillna(0).astype(int)
    df['day_of_week'] = df['timestamp'].dt.dayofweek.fillna(0).astype(int)
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_rush_hour'] = (
        ((df['hour_of_day'] >= 8) & (df['hour_of_day'] <= 10)) |
        ((df['hour_of_day'] >= 17) & (df['hour_of_day'] <= 19))
    ).astype(int)

    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)

    cat_cols = []
    for c in ['weather_condition', 'road_type', 'location']:
        if c in df.columns:
            cat_cols.append(c)

    for c in cat_cols:
        df[c] = df[c].fillna('Unknown')

    df = pd.get_dummies(df, columns=cat_cols, drop_first=False, dtype=int)

    if 'vehicle_count' in df.columns:
        df['vehicle_count'] = df['vehicle_count'].fillna(df['vehicle_count'].median())
    if 'speed_avg' in df.columns:
        df['speed_avg'] = df['speed_avg'].fillna(df['speed_avg'].median())

    if 'vehicle_count' in df.columns and 'is_rush_hour' in df.columns:
        df['vehicle_count_x_rush'] = df['vehicle_count'] * df['is_rush_hour']

    num_cols = ['rain_mm', 'public_transport_density', 'vehicle_count', 'speed_avg',
                'vehicle_count_x_rush']
    for c in num_cols:
        if c in df.columns:
            df[c] = df[c].fillna(df[c].median() if df[c].nunique() > 1 else 0)

    if 'incident_flag' in df.columns:
        df['incident_flag'] = df['incident_flag'].map({'Yes': 1, 'No': 0, True: 1, False: 0}).fillna(0).astype(int)

    return df


def train_model(df):
    label_map = {'Low': 0, 'Medium': 1, 'High': 2}
    df['congestion_label'] = df['congestion_level'].map(label_map)
    df = df.dropna(subset=['congestion_label'])
    df['congestion_label'] = df['congestion_label'].astype(int)

    exclude = ['timestamp', 'congestion_level', 'congestion_label',
               'Latitude', 'Longitude', 'latitude', 'longitude']
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
        n_estimators=300,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss',
        use_label_encoder=False
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
    top_n = min(15, len(idx_sorted))
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
    print("[INFO] Model saved to model/xgb_traffic_model.pkl")

    with open(os.path.join(MODEL_DIR, 'feature_columns.json'), 'w') as f:
        json.dump(feature_cols, f)
    print("[INFO] Feature columns saved to model/feature_columns.json")

    return model, feature_cols


if __name__ == '__main__':
    print("=" * 60)
    print("  TRAFFIC CONGESTION PREDICTOR - ML PIPELINE")
    print("=" * 60)

    df_main, df_supp = load_data()

    dfs = []
    if df_main is not None:
        dfs.append(harmonize_main(df_main))
    if df_supp is not None:
        dfs.append(harmonize_supp(df_supp))

    if not dfs:
        raise RuntimeError("No data available to train.")

    df = pd.concat(dfs, ignore_index=True)
    df = engineer_features(df)
    model, feature_cols = train_model(df)

    print("\n[SUCCESS] ML Pipeline complete. Model ready for backend.")
