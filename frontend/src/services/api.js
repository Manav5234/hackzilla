const API_BASE = 'http://localhost:8000';

export async function predict(data) {
  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('Predict API error:', e);
    return {
      congestion_score: 45,
      risk_label: 'Medium',
      color_code: '#f59e0b',
      probability: [0.2, 0.6, 0.2],
      top_congested_zones: [
        { name: 'Connaught Place', lat: 28.6329, lon: 77.2197, intensity: 72 },
        { name: 'Karol Bagh', lat: 28.6520, lon: 77.1903, intensity: 65 },
        { name: 'India Gate', lat: 28.6129, lon: 77.2295, intensity: 58 },
      ],
      event_boost_applied: false,
    };
  }
}

export async function getHeatmapData() {
  try {
    const res = await fetch(`${API_BASE}/heatmap-data`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.data || [];
  } catch (e) {
    console.error('Heatmap API error:', e);
    return FALLBACK_HEATMAP;
  }
}

export async function getRoutes(originLat, originLon, destLat, destLon) {
  try {
    const res = await fetch(
      `${API_BASE}/routes?origin_lat=${originLat}&origin_lon=${originLon}&dest_lat=${destLat}&dest_lon=${destLon}`
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.routes || [];
  } catch (e) {
    console.error('Routes API error:', e);
    return [];
  }
}

export async function getWeather(lat, lon) {
  try {
    const res = await fetch(`${API_BASE}/weather?lat=${lat}&lon=${lon}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('Weather API error:', e);
    return {
      temperature_c: 28, humidity: 65, precipitation_mm: 0, rain_mm: 0,
      wind_speed_kmh: 12, visibility_m: 8000, condition: 'Clear', source: 'fallback',
    };
  }
}

export async function sendChatMessage(message) {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_message: message }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.reply || 'No response';
  } catch (e) {
    console.error('Chat API error:', e);
    return "I'm having trouble connecting to the traffic AI. Please try again.";
  }
}

const FALLBACK_HEATMAP = [
  { lat: 28.6329, lon: 77.2197, intensity: 72, name: 'Connaught Place' },
  { lat: 28.6129, lon: 77.2295, intensity: 45, name: 'India Gate' },
  { lat: 28.6520, lon: 77.1903, intensity: 65, name: 'Karol Bagh' },
  { lat: 28.5562, lon: 77.1000, intensity: 38, name: 'IGI Airport T3' },
  { lat: 28.5925, lon: 77.0448, intensity: 42, name: 'Dwarka Sector 21' },
  { lat: 28.4795, lon: 77.1001, intensity: 71, name: 'MG Road Gurgaon' },
  { lat: 28.4960, lon: 77.0896, intensity: 68, name: 'Cyber Hub Gurgaon' },
  { lat: 28.5700, lon: 77.3200, intensity: 55, name: 'Sector 18 Noida' },
  { lat: 28.6270, lon: 77.3670, intensity: 60, name: 'Sector 62 Noida' },
  { lat: 28.6460, lon: 77.3415, intensity: 48, name: 'Vaishali Ghaziabad' },
  { lat: 19.1216, lon: 72.8510, intensity: 78, name: 'Andheri Mumbai' },
  { lat: 19.0596, lon: 72.8295, intensity: 52, name: 'Bandra Mumbai' },
  { lat: 12.9352, lon: 77.6245, intensity: 82, name: 'Koramangala Bangalore' },
  { lat: 13.0418, lon: 80.2341, intensity: 44, name: 'T Nagar Chennai' },
  { lat: 22.5595, lon: 88.3532, intensity: 39, name: 'Park Street Kolkata' },
  { lat: 28.5850, lon: 77.4000, intensity: 47, name: 'Greater Noida West' },
];
