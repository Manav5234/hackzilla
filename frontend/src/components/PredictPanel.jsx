import { useState, useMemo } from 'react';
import { predict } from '../services/api';

const LOCATIONS = [
  'Connaught Place', 'India Gate', 'Karol Bagh', 'IGI Airport T3',
  'Dwarka Sector 21', 'MG Road Gurgaon', 'Cyber Hub Gurgaon',
  'Sector 18 Noida', 'Sector 62 Noida', 'Vaishali Ghaziabad',
  'Akshardham Route', 'Botanical Garden', 'DND Flyway', 'Pari Chowk',
  'Greater Noida West', 'Lajpat Nagar', 'Andheri Mumbai', 'Bandra Mumbai',
  'Marine Drive Mumbai', 'Koramangala Bangalore', 'Electronic City Bangalore',
  'T Nagar Chennai', 'Park Street Kolkata', 'MG Road Bangalore',
];
const WEATHERS = ['Clear', 'Cloudy', 'Rain', 'Fog', 'Haze'];
const ROAD_TYPES = ['Urban', 'Highway', 'Residential', 'Arterial'];

function estimateVehiclesFromTime(timeStr) {
  const h = +timeStr.split(':')[0];
  if (h >= 0 && h <= 5) return 15;
  if (h >= 6 && h <= 7) return 80;
  if (h >= 8 && h <= 10) return 350;
  if (h >= 11 && h <= 16) return 200;
  if (h >= 17 && h <= 19) return 400;
  if (h >= 20 && h <= 22) return 150;
  return 50;
}

function estimateSpeedFromTime(timeStr, count) {
  const h = +timeStr.split(':')[0];
  if (h >= 0 && h <= 5) return 65;
  if (count > 350) return 20;
  if (count > 200) return 35;
  if ((h >= 8 && h <= 10) || (h >= 17 && h <= 19)) return 30;
  return 50;
}

function estimateRain(weather) {
  return weather === 'Rain' || weather === 'Storm' ? 15 : weather === 'Fog' ? 5 : 0;
}

export default function PredictPanel({ eventActive }) {
  const [location, setLocation] = useState('Connaught Place');
  const [weather, setWeather] = useState('Clear');
  const [roadType, setRoadType] = useState('Urban');
  const [time, setTime] = useState(new Date().toTimeString().slice(0, 5));
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const autoVehicleCount = useMemo(() => estimateVehiclesFromTime(time), [time]);
  const autoSpeedAvg = useMemo(() => estimateSpeedFromTime(time, autoVehicleCount), [time, autoVehicleCount]);
  const autoRain = useMemo(() => estimateRain(weather), [weather]);

  const handleSubmit = async () => {
    setLoading(true);
    const now = new Date();
    const [h, m] = time.split(':');
    now.setHours(+h, +m, 0, 0);
    const data = {
      location,
      timestamp: now.toISOString().slice(0, 19).replace('T', ' '),
      vehicle_count: autoVehicleCount,
      weather,
      road_type: roadType,
      speed_avg: autoSpeedAvg,
      rain_mm: autoRain,
      incident_flag: false,
      event_active: eventActive,
    };
    const res = await predict(data);
    setResult(res);
    setLoading(false);
  };

  return (
    <div className="panel predict-panel">
      <h3 className="panel-title">
        <span className="neon-dot" />
        Traffic Prediction
      </h3>

      <div className="form-group">
        <label>Location</label>
        <select value={location} onChange={e => setLocation(e.target.value)}>
          {LOCATIONS.map(l => <option key={l}>{l}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label>Weather</label>
        <select value={weather} onChange={e => setWeather(e.target.value)}>
          {WEATHERS.map(w => <option key={w}>{w}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label>Road Type</label>
        <select value={roadType} onChange={e => setRoadType(e.target.value)}>
          {ROAD_TYPES.map(r => <option key={r}>{r}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label>Est. Vehicles: <strong>{autoVehicleCount}</strong></label>
        <div className="range-labels"><span>Auto-calculated from time</span></div>
      </div>

      <div className="form-group">
        <label>Time</label>
        <input type="time" value={time} onChange={e => setTime(e.target.value)} />
      </div>

      <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
        {loading ? 'Analyzing...' : 'Predict Congestion'}
      </button>

      {result && (
        <div className="result-card" style={{ borderColor: result.color_code }}>
          <div className="result-header">
            <span className="risk-badge" style={{ background: result.color_code }}>
              {result.risk_label}
            </span>
            <span className="score-value" style={{ color: result.color_code }}>
              {result.congestion_score}/100
            </span>
          </div>
          <div className="score-gauge">
            <div className="gauge-fill" style={{ width: `${result.congestion_score}%`, background: result.color_code }} />
          </div>
          <div className="result-detail">
            Low: {(result.probability[0] * 100).toFixed(0)}% &middot;
            Med: {(result.probability[1] * 100).toFixed(0)}% &middot;
            High: {(result.probability[2] * 100).toFixed(0)}%
          </div>
          {result.event_boost_applied && (
            <div className="event-warning">⚠ Event boost applied (+25%)</div>
          )}
          <div className="zones-list">
            <strong>Top Congested Zones:</strong>
            {result.top_congested_zones.map((z, i) => (
              <div key={i} className="zone-item">
                {i + 1}. {z.name} — <span style={{ color: z.intensity > 70 ? '#ef4444' : z.intensity > 40 ? '#f59e0b' : '#22c55e' }}>{z.intensity}/100</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
