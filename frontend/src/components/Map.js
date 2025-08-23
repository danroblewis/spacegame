import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import './Map.css';

const Map = ({ selectedShip, onShipUpdate }) => {
  const [waypoints, setWaypoints] = useState([]);
  const [currentSystem, setCurrentSystem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [navigating, setNavigating] = useState(false);
  
  // Zoom and pan state
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  const svgRef = useRef(null);
  const containerRef = useRef(null);

  const fetchSystemData = useCallback(async () => {
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
  }, [selectedShip?.nav?.systemSymbol]);

  useEffect(() => {
    if (selectedShip) {
      fetchSystemData();
    }
  }, [selectedShip, fetchSystemData]);

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
      await axios.post(`/api/ships/${selectedShip.symbol}/navigate`, {
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

  const handleJump = async (waypointSymbol) => {
    if (!selectedShip || navigating || !waypointSymbol) return;

    try {
      setNavigating(true);
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/jump`, {
        waypointSymbol: waypointSymbol
      });

      alert(`Jump successful! ${response.data.data.transaction ? 
        `Antimatter cost: ${response.data.data.transaction.price} credits` : ''}`);
      
      if (onShipUpdate) {
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        onShipUpdate(updatedShip);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Jump failed');
    } finally {
      setNavigating(false);
    }
  };

  const handleWarp = async (waypointSymbol) => {
    if (!selectedShip || navigating || !waypointSymbol) return;

    try {
      setNavigating(true);
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/warp`, {
        waypointSymbol: waypointSymbol
      });

      alert(`Warp successful! Fuel consumed: ${response.data.data.fuel?.consumed?.amount || 'Unknown'}`);
      
      if (onShipUpdate) {
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        onShipUpdate(updatedShip);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Warp failed');
    } finally {
      setNavigating(false);
    }
  };

  const hasWarpDrive = () => {
    return selectedShip?.modules?.some(module => 
      module.symbol?.includes('WARP_DRIVE') || module.name?.includes('Warp Drive')
    );
  };

  // Zoom and pan handlers
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newZoom = Math.max(0.1, Math.min(5, zoom * delta));
    
    // Zoom towards mouse position
    const rect = svgRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    const scaleChange = newZoom / zoom;
    const newPanX = mouseX - (mouseX - pan.x) * scaleChange;
    const newPanY = mouseY - (mouseY - pan.y) * scaleChange;
    
    setZoom(newZoom);
    setPan({ x: newPanX, y: newPanY });
  }, [zoom, pan]);

  const handleMouseDown = useCallback((e) => {
    if (e.button === 0) { // Left mouse button only
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  }, [pan]);

  const handleMouseMove = useCallback((e) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDoubleClick = useCallback(() => {
    // Reset zoom and pan
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  const zoomIn = useCallback(() => {
    setZoom(prev => Math.min(5, prev * 1.2));
  }, []);

  const zoomOut = useCallback(() => {
    setZoom(prev => Math.max(0.1, prev / 1.2));
  }, []);

  const resetView = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

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
              <>
                <button 
                  onClick={handleDock}
                  disabled={navigating}
                  className="dock-btn"
                >
                  {navigating ? 'Processing...' : 'Dock'}
                </button>
                <button 
                  onClick={() => {
                    const waypoint = prompt('Enter waypoint symbol for jump:');
                    if (waypoint) handleJump(waypoint);
                  }}
                  disabled={navigating}
                  className="jump-btn quick-nav"
                  title="Quick Jump"
                >
                  🚀 Jump
                </button>
                <button 
                  onClick={() => {
                    const waypoint = prompt('Enter waypoint symbol for warp:');
                    if (waypoint) handleWarp(waypoint);
                  }}
                  disabled={navigating || !hasWarpDrive()}
                  className="warp-btn quick-nav"
                  title="Quick Warp"
                >
                  ⚡ Warp
                </button>
              </>
            )}
          </div>
        </div>
        <div className="map-controls">
          <button onClick={zoomOut} className="zoom-btn" title="Zoom Out">−</button>
          <span className="zoom-level">{Math.round(zoom * 100)}%</span>
          <button onClick={zoomIn} className="zoom-btn" title="Zoom In">+</button>
          <button onClick={resetView} className="reset-btn" title="Reset View">⌂</button>
        </div>
      </div>

      <div className="map-view" 
           ref={containerRef}
           onWheel={handleWheel}
           onMouseDown={handleMouseDown}
           onMouseMove={handleMouseMove}
           onMouseUp={handleMouseUp}
           onMouseLeave={handleMouseUp}
           onDoubleClick={handleDoubleClick}
           style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        <svg 
          ref={svgRef}
          className="system-map" 
          viewBox={`${minX} ${minY} ${mapWidth} ${mapHeight}`}
          preserveAspectRatio="xMidYMid meet"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: '0 0'
          }}
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
        <div className="legend-controls">
          <strong>Map Controls:</strong> Mouse wheel to zoom, drag to pan, double-click to reset view
        </div>
      </div>
    </div>
  );
};

export default Map;