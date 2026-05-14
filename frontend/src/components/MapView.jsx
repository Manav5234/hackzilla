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

export default function MapView({ heatmapData, selectedCity, onCityClick, routeCoords }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const heatLayer = useRef(null);
  const routeLayer = useRef(null);
  const routeMarkers = useRef(null);

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

  useEffect(() => {
    const map = mapInstance.current;
    if (!map) return;

    if (routeLayer.current) { map.removeLayer(routeLayer.current); routeLayer.current = null; }
    if (routeMarkers.current) { routeMarkers.current.forEach(m => map.removeLayer(m)); routeMarkers.current = null; }

    if (!routeCoords || !routeCoords.coordinates || routeCoords.coordinates.length < 2) return;

    const coords = routeCoords.coordinates;
    const color = routeCoords.color || '#3388ff';

    routeLayer.current = L.polyline(coords, {
      color, weight: 5, opacity: 0.8, dashArray: null,
    }).addTo(map);

    const startIcon = L.divIcon({ html: '<div style="background:#22c55e;width:12px;height:12px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 6px rgba(0,0,0,0.5)"></div>', className: '', iconSize: [12, 12], iconAnchor: [6, 6] });
    const endIcon = L.divIcon({ html: '<div style="background:#ef4444;width:12px;height:12px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 6px rgba(0,0,0,0.5)"></div>', className: '', iconSize: [12, 12], iconAnchor: [6, 6] });

    const startMarker = L.marker(coords[0], { icon: startIcon }).addTo(map).bindPopup(`<b>Start</b><br/>${routeCoords.label || 'Route'}`);
    const endMarker = L.marker(coords[coords.length - 1], { icon: endIcon }).addTo(map).bindPopup('<b>Destination</b>');
    routeMarkers.current = [startMarker, endMarker];

    map.fitBounds(routeLayer.current.getBounds().pad(0.1));
  }, [routeCoords]);

  return <div ref={mapRef} style={{ width: '100%', height: '100%' }} />;
}
