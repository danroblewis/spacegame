import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Map.css';

const Map = ({ selectedShip, onShipUpdate }) => {
  const [waypoints, setWaypoints] = useState([]);
  const [currentSystem, setCurrentSystem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [navigating, setNavigating] = useState(false);

  useEffect(() => {
    if (selectedShip) {
      fetchSystemData();
    }
  }, [selectedShip]);

  const fetchSystemData = async () => {
    if (!selectedShip?.nav?.systemSymbol) return;

    try {
      setLoading(true);
      const [systemResponse, waypointsResponse] = await Promise.all([
        axios.get(`/api/systems/${selectedShip.nav.systemSymbol}`),
        axios.get(`/api/systems/${selectedShip.nav.systemSymbol}/waypoints`)
      ]);
      
      setCurrentSystem(systemResponse.data);
      setWaypoints(waypointsResponse.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch map data');
    } finally {
      setLoading(false);
    }
  };

  const handleWaypointClick = async (waypoint) => {
    if (!selectedShip || navigating) return;
    
    // Don't navigate if already at this waypoint
    if (selectedShip.nav.waypointSymbol === waypoint.symbol) return;

    // Can only navigate if ship is in orbit
    if (selectedShip.nav.status !== 'IN_ORBIT') {
      alert('Ship must be in orbit to navigate. Please orbit first.');
      return;
    }

    try {
      setNavigating(true);
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/navigate`, {
        waypointSymbol: waypoint.symbol
      });
      
      if (onShipUpdate) {
        // Fetch updated ship data
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        onShipUpdate(updatedShip);
      }
      
    } catch (err) {
      alert(err.response?.data?.detail || 'Navigation failed');
    } finally {
      setNavigating(false);
    }
  };

  const handleDock = async () => {
    if (!selectedShip || navigating) return;

    try {
      setNavigating(true);
      await axios.post(`/api/ships/${selectedShip.symbol}/dock`);
      
      if (onShipUpdate) {
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        onShipUpdate(updatedShip);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Dock failed');
    } finally {
      setNavigating(false);
    }
  };

  const handleOrbit = async () => {
    if (!selectedShip || navigating) return;

    try {
      setNavigating(true);
      await axios.post(`/api/ships/${selectedShip.symbol}/orbit`);
      
      if (onShipUpdate) {
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        onShipUpdate(updatedShip);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Orbit failed');
    } finally {
      setNavigating(false);
    }
  };

  const getWaypointColor = (type) => {
    const colors = {
      'PLANET': '#4CAF50',
      'MOON': '#9E9E9E',
      'ASTEROID_FIELD': '#8D6E63',
      'JUMP_GATE': '#9C27B0',
      'GAS_GIANT': '#FF9800',
      'NEBULA': '#E91E63',
      'DEBRIS_FIELD': '#607D8B',
      'GRAVITY_WELL': '#F44336'
    };
    return colors[type] || '#2196F3';
  };

  const getWaypointSize = (type) => {
    const sizes = {
      'PLANET': 16,
      'MOON': 10,
      'ASTEROID_FIELD': 12,
      'JUMP_GATE': 14,
      'GAS_GIANT': 20,
      'NEBULA': 18,
      'DEBRIS_FIELD': 8,
      'GRAVITY_WELL': 14
    };
    return sizes[type] || 12;
  };

  if (!selectedShip) {
    return (
      <div className="map-container">
        <div className="map-placeholder">
          <h3>Select a ship to view system map</h3>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="map-container">
        <div className="map-loading">Loading system map...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="map-container">
        <div className="map-error">Error: {error}</div>
      </div>
    );
  }

  // Calculate map bounds
  const margin = 50;
  const minX = Math.min(...waypoints.map(w => w.x)) - margin;
  const maxX = Math.max(...waypoints.map(w => w.x)) + margin;
  const minY = Math.min(...waypoints.map(w => w.y)) - margin;
  const maxY = Math.max(...waypoints.map(w => w.y)) + margin;
  const mapWidth = maxX - minX;
  const mapHeight = maxY - minY;

  return (
    <div className="map-container">
      <div className="map-header">
        <h3>System Map: {currentSystem?.symbol}</h3>
        <div className="ship-controls">
          <div className="ship-status">
            <span className={`status-indicator ${selectedShip.nav.status?.toLowerCase()}`}>
              {selectedShip.nav.status}
            </span>
            <span className="ship-location">
              at {selectedShip.nav.waypointSymbol}
            </span>
          </div>
          <div className="control-buttons">
            {selectedShip.nav.status === 'DOCKED' && (
              <button 
                onClick={handleOrbit}
                disabled={navigating}
                className="orbit-btn"
              >
                {navigating ? 'Processing...' : 'Orbit'}
              </button>
            )}
            {selectedShip.nav.status === 'IN_ORBIT' && (
              <button 
                onClick={handleDock}
                disabled={navigating}
                className="dock-btn"
              >
                {navigating ? 'Processing...' : 'Dock'}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="map-view">
        <svg 
          className="system-map" 
          viewBox={`${minX} ${minY} ${mapWidth} ${mapHeight}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Grid lines */}
          <defs>
            <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
              <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#333" strokeWidth="0.5" opacity="0.3"/>
            </pattern>
          </defs>
          <rect x={minX} y={minY} width={mapWidth} height={mapHeight} fill="url(#grid)" />

          {/* Center point (system center) */}
          <circle
            cx={currentSystem?.x || 0}
            cy={currentSystem?.y || 0}
            r="8"
            fill="#FFD700"
            stroke="#FFA000"
            strokeWidth="2"
            opacity="0.8"
          />
          <text
            x={currentSystem?.x || 0}
            y={(currentSystem?.y || 0) - 15}
            textAnchor="middle"
            fill="#FFD700"
            fontSize="12"
            fontWeight="bold"
          >
            {currentSystem?.type}
          </text>

          {/* Waypoints */}
          {waypoints.map((waypoint) => {
            const isShipLocation = selectedShip.nav.waypointSymbol === waypoint.symbol;
            const isDestination = selectedShip.nav.route?.destination?.symbol === waypoint.symbol;
            const size = getWaypointSize(waypoint.type);
            
            return (
              <g key={waypoint.symbol}>
                {/* Waypoint circle */}
                <circle
                  cx={waypoint.x}
                  cy={waypoint.y}
                  r={size}
                  fill={getWaypointColor(waypoint.type)}
                  stroke={isShipLocation ? '#00FF00' : isDestination ? '#FF0000' : '#FFF'}
                  strokeWidth={isShipLocation || isDestination ? "3" : "1"}
                  className={`waypoint ${selectedShip.nav.status === 'IN_ORBIT' ? 'clickable' : ''}`}
                  onClick={() => handleWaypointClick(waypoint)}
                  style={{ cursor: selectedShip.nav.status === 'IN_ORBIT' ? 'pointer' : 'default' }}
                />

                {/* Ship indicator */}
                {isShipLocation && (
                  <g>
                    <polygon
                      points={`${waypoint.x},${waypoint.y - size - 8} ${waypoint.x - 6},${waypoint.y - size - 2} ${waypoint.x + 6},${waypoint.y - size - 2}`}
                      fill="#00FF00"
                      stroke="#FFF"
                      strokeWidth="1"
                    />
                    <text
                      x={waypoint.x}
                      y={waypoint.y - size - 12}
                      textAnchor="middle"
                      fill="#00FF00"
                      fontSize="10"
                      fontWeight="bold"
                    >
                      {selectedShip.symbol}
                    </text>
                  </g>
                )}

                {/* Waypoint label */}
                <text
                  x={waypoint.x}
                  y={waypoint.y + size + 15}
                  textAnchor="middle"
                  fill="#FFF"
                  fontSize="10"
                  className="waypoint-label"
                >
                  {waypoint.symbol.split('-').pop()}
                </text>
                <text
                  x={waypoint.x}
                  y={waypoint.y + size + 27}
                  textAnchor="middle"
                  fill="#AAA"
                  fontSize="8"
                >
                  {waypoint.type.replace('_', ' ')}
                </text>
              </g>
            );
          })}

          {/* Travel route line */}
          {selectedShip.nav.status === 'IN_TRANSIT' && selectedShip.nav.route && (
            <line
              x1={selectedShip.nav.route.origin?.x || 0}
              y1={selectedShip.nav.route.origin?.y || 0}
              x2={selectedShip.nav.route.destination?.x || 0}
              y2={selectedShip.nav.route.destination?.y || 0}
              stroke="#FF0000"
              strokeWidth="2"
              strokeDasharray="5,5"
              opacity="0.8"
            />
          )}
        </svg>
      </div>

      <div className="map-legend">
        <h4>Legend</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#4CAF50'}}></div>
            <span>Planet</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#9E9E9E'}}></div>
            <span>Moon</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#8D6E63'}}></div>
            <span>Asteroid Field</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#9C27B0'}}></div>
            <span>Jump Gate</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#FF9800'}}></div>
            <span>Gas Giant</span>
          </div>
        </div>
        <div className="legend-note">
          Click on waypoints to navigate (ship must be in orbit)
        </div>
      </div>
    </div>
  );
};

export default Map;