import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

export default function MapView({ heatmapData, selectedCity, onCityClick }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const heatLayer = useRef(null);

  useEffect(() => {
    if (mapInstance.current) return;
    mapInstance.current = L.map(mapRef.current, {
      center: [20.5937, 78.9629],
      zoom: 5,
      zoomControl: false,
    });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
      maxZoom: 19,
    }).addTo(mapInstance.current);
    L.control.zoom({ position: 'bottomright' }).addTo(mapInstance.current);
  }, []);

  useEffect(() => {
    if (!mapInstance.current || !heatmapData || heatmapData.length === 0) return;
    if (heatLayer.current) {
      mapInstance.current.removeLayer(heatLayer.current);
    }
    const points = heatmapData.map(d => [d.lat, d.lon, d.intensity / 100]);
    heatLayer.current = L.heatLayer(points, {
      radius: 30,
      blur: 20,
      maxZoom: 10,
      max: 1.0,
      gradient: { 0.0: '#22c55e', 0.4: '#f59e0b', 0.7: '#ef4444' },
    }).addTo(mapInstance.current);
  }, [heatmapData]);

  useEffect(() => {
    if (!mapInstance.current || !heatmapData) return;
    const existing = [];
    mapInstance.current.eachLayer(l => { if (l instanceof L.Marker) existing.push(l); });
    existing.forEach(m => mapInstance.current.removeLayer(m));
    heatmapData.forEach(d => {
      const color = d.intensity > 70 ? '#ef4444' : d.intensity > 40 ? '#f59e0b' : '#22c55e';
      const marker = L.circleMarker([d.lat, d.lon], {
        radius: 8, fillColor: color, color: '#fff', weight: 2, opacity: 1, fillOpacity: 0.8,
      });
      marker.bindPopup(`
        <div style="font-family:sans-serif;min-width:140px">
          <strong>${d.name}</strong><br/>
          Traffic: ${d.traffic_volume || 'N/A'} veh<br/>
          Speed: ${d.speed_avg ? d.speed_avg.toFixed(1) : 'N/A'} km/h<br/>
          Congestion: <span style="color:${color};font-weight:bold">${d.intensity.toFixed(0)}/100</span>
        </div>
      `);
      marker.on('click', () => onCityClick && onCityClick(d.name));
      marker.addTo(mapInstance.current);
    });
  }, [heatmapData, onCityClick]);

  useEffect(() => {
    if (!mapInstance.current || !selectedCity) return;
    const found = heatmapData?.find(d => d.name === selectedCity);
    if (found) {
      mapInstance.current.setView([found.lat, found.lon], 13);
    }
  }, [selectedCity, heatmapData]);

  return <div ref={mapRef} style={{ width: '100%', height: '100%' }} />;
}
