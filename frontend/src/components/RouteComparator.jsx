import { useState } from 'react';
import { getRoutes } from '../services/api';

const CITIES = [
  { name: 'Connaught Place', lat: 28.6329, lon: 77.2197 },
  { name: 'India Gate', lat: 28.6129, lon: 77.2295 },
  { name: 'Karol Bagh', lat: 28.6520, lon: 77.1903 },
  { name: 'IGI Airport T3', lat: 28.5562, lon: 77.1000 },
  { name: 'Dwarka Sector 21', lat: 28.5925, lon: 77.0448 },
  { name: 'MG Road Gurgaon', lat: 28.4795, lon: 77.1001 },
  { name: 'Cyber Hub Gurgaon', lat: 28.4960, lon: 77.0896 },
  { name: 'Sector 18 Noida', lat: 28.5700, lon: 77.3200 },
  { name: 'Sector 62 Noida', lat: 28.6270, lon: 77.3670 },
  { name: 'Vaishali Ghaziabad', lat: 28.6460, lon: 77.3415 },
  { name: 'Andheri Mumbai', lat: 19.1216, lon: 72.8510 },
  { name: 'Bandra Mumbai', lat: 19.0596, lon: 72.8295 },
  { name: 'Koramangala Bangalore', lat: 12.9352, lon: 77.6245 },
  { name: 'T Nagar Chennai', lat: 13.0418, lon: 80.2341 },
  { name: 'Park Street Kolkata', lat: 22.5595, lon: 88.3532 },
];

export default function RouteComparator() {
  const [origin, setOrigin] = useState(CITIES[0]);
  const [dest, setDest] = useState(CITIES[3]);
  const [routes, setRoutes] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    setLoading(true);
    const res = await getRoutes(origin.lat, origin.lon, dest.lat, dest.lon);
    setRoutes(res);
    setLoading(false);
  };

  return (
    <div className="panel route-panel">
      <h3 className="panel-title">
        <span className="neon-dot" />
        Route Comparator
      </h3>

      <div className="form-group">
        <label>Origin</label>
        <select value={origin.name} onChange={e => {
          const c = CITIES.find(x => x.name === e.target.value);
          if (c) setOrigin(c);
        }}>
          {CITIES.map(c => <option key={c.name}>{c.name}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label>Destination</label>
        <select value={dest.name} onChange={e => {
          const c = CITIES.find(x => x.name === e.target.value);
          if (c) setDest(c);
        }}>
          {CITIES.map(c => <option key={c.name}>{c.name}</option>)}
        </select>
      </div>

      <button className="btn-primary" onClick={handleCompare} disabled={loading}>
        {loading ? 'Finding Routes...' : 'Compare Routes'}
      </button>

      {routes && (
        <div className="routes-container">
          {routes.map((route, i) => (
            <div key={i} className="route-card" style={{ borderLeftColor: route.color_code }}>
              <div className="route-header">
                <span className="route-label">{route.label}</span>
                {route.label.includes('AI') && <span className="ai-badge">AI</span>}
              </div>
              <div className="route-stats">
                <div className="stat">
                  <span className="stat-icon">⏱</span>
                  <span className="stat-value">{route.duration_min} min</span>
                </div>
                <div className="stat">
                  <span className="stat-icon">📏</span>
                  <span className="stat-value">{route.distance_km} km</span>
                </div>
                <div className="stat">
                  <span className="stat-icon" style={{ color: route.color_code }}>●</span>
                  <span className="stat-value">{route.congestion_level}</span>
                </div>
              </div>
              <div className="route-warning">{route.congestion_warning}</div>
              {route.ai_note && <div className="ai-note">🧠 {route.ai_note}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
