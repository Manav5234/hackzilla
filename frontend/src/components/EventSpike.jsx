export default function EventSpike({ eventActive, onToggle }) {
  return (
    <div className="panel event-panel">
      <h3 className="panel-title">
        <span className="neon-dot" />
        Event Mode
      </h3>
      <div className="event-toggle">
        <label className="toggle-label">
          <input type="checkbox" checked={eventActive} onChange={onToggle} />
          <span className="toggle-track">
            <span className="toggle-thumb" />
          </span>
          <span className="toggle-text">
            {eventActive ? 'Active Event (IPL Match / Concert)' : 'No Active Event'}
          </span>
        </label>
      </div>
      {eventActive && (
        <div className="event-banner">
          ⚠ Event mode active: Congestion predictions increased by 25-35%
        </div>
      )}
    </div>
  );
}
