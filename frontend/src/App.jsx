import { useState, useEffect, useCallback } from 'react';
import MapView from './components/MapView';
import PredictPanel from './components/PredictPanel';
import RouteComparator from './components/RouteComparator';
import ChatBot from './components/ChatBot';
import StatsBar from './components/StatsBar';
import EventSpike from './components/EventSpike';
import { getHeatmapData } from './services/api';
import './App.css';

function App() {
  const [heatmapData, setHeatmapData] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [eventActive, setEventActive] = useState(false);
  const [routeCoords, setRouteCoords] = useState(null);

  useEffect(() => {
    getHeatmapData().then(setHeatmapData);
  }, []);

  const handleCityClick = useCallback((name) => {
    setSelectedCity(name);
  }, []);

  return (
    <div className="app">
      <div className="top-bar">
        <div className="logo">
          <span className="logo-icon">🚦</span>
          <span className="logo-text">TrafficAI<span className="logo-sub">Smart Congestion Predictor</span></span>
        </div>
        <StatsBar selectedCity={selectedCity} />
      </div>

      <div className="main-layout">
        <div className="left-panel">
          <PredictPanel eventActive={eventActive} />
          <RouteComparator onRouteSelect={setRouteCoords} />
          <EventSpike eventActive={eventActive} onToggle={() => setEventActive(!eventActive)} />
        </div>

        <div className="right-panel">
          <MapView
            heatmapData={heatmapData}
            selectedCity={selectedCity}
            onCityClick={handleCityClick}
            routeCoords={routeCoords}
          />
        </div>
      </div>

      <ChatBot />
    </div>
  );
}

export default App;
