import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Systems = () => {
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSystem, setSelectedSystem] = useState(null);

  useEffect(() => {
    fetchSystems();
  }, []);

  const fetchSystems = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/systems');
      setSystems(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch systems');
    } finally {
      setLoading(false);
    }
  };

  const getSystemTypeColor = (type) => {
    switch (type) {
      case 'NEUTRON_STAR':
        return '#ff6b6b';
      case 'RED_STAR':
        return '#ff4757';
      case 'ORANGE_STAR':
        return '#ffa502';
      case 'BLUE_STAR':
        return '#3742fa';
      case 'YOUNG_STAR':
        return '#2ed573';
      case 'WHITE_DWARF':
        return '#f1f2f6';
      case 'BLACK_HOLE':
        return '#2f3542';
      case 'HYPERGIANT':
        return '#ff3838';
      case 'MAIN_SEQUENCE':
        return '#ffa502';
      case 'HYDROGEN_GAS_GIANT':
        return '#70a1ff';
      case 'AMMONIA_ICE':
        return '#a4b0be';
      case 'WATER_ICE_GIANT':
        return '#74b9ff';
      case 'ICE_GIANT':
        return '#74b9ff';
      case 'GAS_GIANT':
        return '#70a1ff';
      case 'TERRESTRIAL':
        return '#2ed573';
      case 'ROCKY_METAL':
        return '#a4b0be';
      case 'ROCKY_ICE':
        return '#a4b0be';
      default:
        return '#cccccc';
    }
  };

  if (loading) {
    return <div className="loading">Loading systems data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="systems">
      <div className="card">
        <h1>Galaxy Systems</h1>
        <p>Total Systems: {systems.length}</p>
      </div>

      {systems.length === 0 ? (
        <div className="card">
          <p>No systems found.</p>
        </div>
      ) : (
        <div className="grid">
          {systems.map((system) => (
            <div key={system.symbol} className="system-card">
              <div className="system-header">
                <h3 className="system-name">{system.symbol}</h3>
                <span 
                  className="system-type"
                  style={{ backgroundColor: getSystemTypeColor(system.type) }}
                >
                  {system.type.replace(/_/g, ' ')}
                </span>
              </div>

              <div className="system-details">
                <div className="detail-item">
                  <div className="detail-value">{system.sectorSymbol}</div>
                  <div className="detail-label">Sector</div>
                </div>
                <div className="detail-item">
                  <div className="detail-value">({system.x}, {system.y})</div>
                  <div className="detail-label">Coordinates</div>
                </div>
                <div className="detail-item">
                  <div className="detail-value">{system.waypoints?.length || 0}</div>
                  <div className="detail-label">Waypoints</div>
                </div>
                <div className="detail-item">
                  <div className="detail-value">{system.factions?.length || 0}</div>
                  <div className="detail-label">Factions</div>
                </div>
              </div>

              {system.waypoints && system.waypoints.length > 0 && (
                <div className="waypoints-section">
                  <h4>Waypoints:</h4>
                  <div className="waypoints-grid">
                    {system.waypoints.slice(0, 5).map((waypoint, index) => (
                      <div key={index} className="waypoint-item">
                        <span className="waypoint-symbol">{waypoint.symbol}</span>
                        <span className="waypoint-type">{waypoint.type}</span>
                      </div>
                    ))}
                    {system.waypoints.length > 5 && (
                      <div className="waypoint-more">
                        +{system.waypoints.length - 5} more
                      </div>
                    )}
                  </div>
                </div>
              )}

              {system.factions && system.factions.length > 0 && (
                <div className="factions-section">
                  <h4>Factions:</h4>
                  <div className="factions-grid">
                    {system.factions.map((faction, index) => (
                      <div key={index} className="faction-item">
                        {faction.symbol}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Systems;
