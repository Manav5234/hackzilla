import { useState, useEffect } from 'react';
import { getHeatmapData, getWeather } from '../services/api';

export default function StatsBar({ selectedCity, onCityChange }) {
  const [stats, setStats] = useState({ total: 0, high: 0, avgScore: 0 });
  const [weather, setWeather] = useState(null);

  useEffect(() => {
    getHeatmapData().then(data => {
      if (data.length) {
        const high = data.filter(d => d.intensity > 70).length;
        const avg = data.reduce((s, d) => s + d.intensity, 0) / data.length;
        setStats({ total: data.length, high, avgScore: Math.round(avg) });
        if (data[0]) {
          getWeather(data[0].lat, data[0].lon).then(setWeather);
        }
      }
    });
  }, []);

  useEffect(() => {
    if (selectedCity) {
      getWeather(28.6329, 77.2197).then(setWeather);
    }
  }, [selectedCity]);

  return (
    <div className="stats-bar">
      <div className="stat-block">
        <span className="stat-label">Monitored Zones</span>
        <span className="stat-number">{stats.total}</span>
      </div>
      <div className="stat-block">
        <span className="stat-label">High Risk</span>
        <span className="stat-number" style={{ color: '#ef4444' }}>{stats.high}</span>
      </div>
      <div className="stat-block">
        <span className="stat-label">Avg Congestion</span>
        <span className="stat-number" style={{ color: stats.avgScore > 50 ? '#f59e0b' : '#22c55e' }}>
          {stats.avgScore}/100
        </span>
      </div>
      <div className="stat-block">
        <span className="stat-label">Weather</span>
        <span className="stat-number" style={{ fontSize: '0.9rem' }}>
          {weather ? `${weather.temperature_c}°C ${weather.condition}` : '—'}
        </span>
      </div>
    </div>
  );
}
