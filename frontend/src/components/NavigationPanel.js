import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './NavigationPanel.css';

const NavigationPanel = ({ selectedShip, onShipUpdate, availableSystems = [] }) => {
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(null);
  const [routePlan, setRoutePlan] = useState(null);
  const [autopilot, setAutopilot] = useState({ active: false, currentStep: 0 });
  const [targetWaypoint, setTargetWaypoint] = useState('');
  const [routeWaypoints, setRouteWaypoints] = useState(['']);
  const [optimizeFuel, setOptimizeFuel] = useState(true);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (selectedShip) {
      checkCooldown();
      // Check cooldown every 5 seconds
      intervalRef.current = setInterval(checkCooldown, 5000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [selectedShip]);

  const checkCooldown = async () => {
    if (!selectedShip) return;
    
    try {
      const response = await axios.get(`/api/ships/${selectedShip.symbol}/cooldown`);
      setCooldown(response.data.data);
    } catch (err) {
      console.error('Failed to check cooldown:', err);
    }
  };

  const handleJump = async () => {
    if (!selectedShip || !targetWaypoint || loading) return;

    try {
      setLoading(true);
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/jump`, {
        waypointSymbol: targetWaypoint
      });

      alert(`Jump successful! ${response.data.data.transaction ? 
        `Antimatter cost: ${response.data.data.transaction.price} credits` : ''}`);
      
      if (onShipUpdate) {
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        onShipUpdate(updatedShip);
      }

      checkCooldown();
      setTargetWaypoint('');
    } catch (err) {
      alert(err.response?.data?.detail || 'Jump failed');
    } finally {
      setLoading(false);
    }
  };

  const handleWarp = async () => {
    if (!selectedShip || !targetWaypoint || loading) return;

    try {
      setLoading(true);
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/warp`, {
        waypointSymbol: targetWaypoint
      });

      alert(`Warp successful! Fuel consumed: ${response.data.data.fuel?.consumed?.amount || 'Unknown'}`);
      
      if (onShipUpdate) {
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        onShipUpdate(updatedShip);
      }

      setTargetWaypoint('');
    } catch (err) {
      alert(err.response?.data?.detail || 'Warp failed');
    } finally {
      setLoading(false);
    }
  };

  const handleEmergencyStop = async () => {
    if (!selectedShip || loading) return;

    if (!confirm('Execute emergency stop? This may consume additional fuel.')) return;

    try {
      setLoading(true);
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/emergency-stop`);

      alert(response.data.data.message || 'Emergency stop executed');
      
      if (onShipUpdate) {
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        onShipUpdate(updatedShip);
      }

      // Stop autopilot if active
      setAutopilot({ active: false, currentStep: 0 });
    } catch (err) {
      alert(err.response?.data?.detail || 'Emergency stop failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePlanRoute = async () => {
    if (!selectedShip || routeWaypoints.filter(w => w.trim()).length === 0) return;

    try {
      setLoading(true);
      const validWaypoints = routeWaypoints.filter(w => w.trim());
      
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/route`, {
        waypoints: validWaypoints,
        optimize_fuel: optimizeFuel
      });

      setRoutePlan(response.data.data);
    } catch (err) {
      alert(err.response?.data?.detail || 'Route planning failed');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAutopilot = async () => {
    if (!routePlan || autopilot.active) return;

    setAutopilot({ active: true, currentStep: 0 });
    
    // Execute autopilot steps
    for (let i = 0; i < routePlan.waypoints.length; i++) {
      if (!autopilot.active) break; // Stop if autopilot was deactivated
      
      setAutopilot(prev => ({ ...prev, currentStep: i }));
      
      try {
        // Navigate to waypoint
        await axios.post(`/api/ships/${selectedShip.symbol}/navigate`, {
          waypointSymbol: routePlan.waypoints[i]
        });

        // Wait for arrival (simplified - in real implementation would check ship status)
        await new Promise(resolve => setTimeout(resolve, 2000));

        if (onShipUpdate) {
          const shipResponse = await axios.get('/api/ships');
          const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
          onShipUpdate(updatedShip);
        }
      } catch (err) {
        alert(`Autopilot failed at waypoint ${routePlan.waypoints[i]}: ${err.response?.data?.detail || 'Unknown error'}`);
        break;
      }
    }

    setAutopilot({ active: false, currentStep: 0 });
  };

  const handleStopAutopilot = () => {
    setAutopilot({ active: false, currentStep: 0 });
  };

  const addRouteWaypoint = () => {
    setRouteWaypoints([...routeWaypoints, '']);
  };

  const updateRouteWaypoint = (index, value) => {
    const newWaypoints = [...routeWaypoints];
    newWaypoints[index] = value;
    setRouteWaypoints(newWaypoints);
  };

  const removeRouteWaypoint = (index) => {
    const newWaypoints = routeWaypoints.filter((_, i) => i !== index);
    setRouteWaypoints(newWaypoints);
  };

  const canPerformAction = () => {
    return selectedShip && 
           selectedShip.nav?.status === 'IN_ORBIT' && 
           !loading && 
           (!cooldown || cooldown.remainingSeconds === 0);
  };

  const hasWarpDrive = () => {
    return selectedShip?.modules?.some(module => 
      module.symbol?.includes('WARP_DRIVE') || module.name?.includes('Warp Drive')
    );
  };

  if (!selectedShip) {
    return (
      <div className="navigation-panel">
        <h3>Advanced Navigation</h3>
        <p>Select a ship to access navigation features</p>
      </div>
    );
  }

  return (
    <div className="navigation-panel">
      <h3>Advanced Navigation - {selectedShip.symbol}</h3>
      
      {/* Status Display */}
      <div className="nav-status">
        <div className="status-item">
          <span className="label">Status:</span>
          <span className={`value ${selectedShip.nav?.status?.toLowerCase()}`}>
            {selectedShip.nav?.status}
          </span>
        </div>
        <div className="status-item">
          <span className="label">Location:</span>
          <span className="value">{selectedShip.nav?.waypointSymbol}</span>
        </div>
        {cooldown && cooldown.remainingSeconds > 0 && (
          <div className="status-item cooldown">
            <span className="label">Cooldown:</span>
            <span className="value">{cooldown.remainingSeconds}s</span>
          </div>
        )}
      </div>

      {/* Quick Navigation */}
      <div className="nav-section">
        <h4>Quick Navigation</h4>
        <div className="nav-controls">
          <input
            type="text"
            placeholder="Enter waypoint symbol"
            value={targetWaypoint}
            onChange={(e) => setTargetWaypoint(e.target.value)}
            disabled={loading || !canPerformAction()}
          />
          <div className="nav-buttons">
            <button
              onClick={handleJump}
              disabled={!canPerformAction() || !targetWaypoint}
              className="jump-btn"
              title="Jump via jump gate to connected systems"
            >
              {loading ? 'Jumping...' : 'Jump'}
            </button>
            <button
              onClick={handleWarp}
              disabled={!canPerformAction() || !targetWaypoint || !hasWarpDrive()}
              className="warp-btn"
              title="Warp to distant systems (requires warp drive)"
            >
              {loading ? 'Warping...' : 'Warp'}
            </button>
          </div>
        </div>
        {!hasWarpDrive() && (
          <p className="warning">⚠️ Ship requires a Warp Drive module for warp travel</p>
        )}
      </div>

      {/* Emergency Controls */}
      <div className="nav-section">
        <h4>Emergency Controls</h4>
        <button
          onClick={handleEmergencyStop}
          disabled={loading || selectedShip.nav?.status !== 'IN_TRANSIT'}
          className="emergency-btn"
        >
          🛑 Emergency Stop
        </button>
        <p className="help-text">
          Abort current navigation (only available during transit)
        </p>
      </div>

      {/* Route Planning */}
      <div className="nav-section">
        <h4>Route Planning</h4>
        <div className="route-controls">
          <div className="route-waypoints">
            {routeWaypoints.map((waypoint, index) => (
              <div key={index} className="waypoint-input">
                <input
                  type="text"
                  placeholder={`Waypoint ${index + 1}`}
                  value={waypoint}
                  onChange={(e) => updateRouteWaypoint(index, e.target.value)}
                />
                {routeWaypoints.length > 1 && (
                  <button
                    onClick={() => removeRouteWaypoint(index)}
                    className="remove-btn"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
          <div className="route-actions">
            <button onClick={addRouteWaypoint} className="add-waypoint-btn">
              + Add Waypoint
            </button>
            <label className="fuel-optimize">
              <input
                type="checkbox"
                checked={optimizeFuel}
                onChange={(e) => setOptimizeFuel(e.target.checked)}
              />
              Optimize for fuel efficiency
            </label>
            <button
              onClick={handlePlanRoute}
              disabled={loading || routeWaypoints.filter(w => w.trim()).length === 0}
              className="plan-btn"
            >
              Plan Route
            </button>
          </div>
        </div>

        {/* Route Plan Display */}
        {routePlan && (
          <div className="route-plan">
            <h5>Route Plan</h5>
            <div className="route-summary">
              <div className="summary-item">
                <span>Total Fuel:</span>
                <span>{routePlan.total_fuel_estimate}</span>
              </div>
              <div className="summary-item">
                <span>Total Time:</span>
                <span>{Math.round(routePlan.total_time_estimate / 60)} minutes</span>
              </div>
            </div>
            <div className="route-steps">
              {routePlan.route_legs?.map((leg, index) => (
                <div key={index} className="route-step">
                  <span className="step-number">{index + 1}</span>
                  <span className="step-waypoint">{leg.waypoint}</span>
                  <span className="step-fuel">{leg.estimated_fuel} fuel</span>
                  <span className="step-time">{Math.round(leg.estimated_time / 60)}m</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Autopilot */}
      <div className="nav-section">
        <h4>Autopilot</h4>
        {!autopilot.active ? (
          <button
            onClick={handleStartAutopilot}
            disabled={!routePlan || !canPerformAction()}
            className="autopilot-btn"
          >
            🤖 Start Autopilot
          </button>
        ) : (
          <div className="autopilot-active">
            <button onClick={handleStopAutopilot} className="stop-autopilot-btn">
              ⏹️ Stop Autopilot
            </button>
            <div className="autopilot-progress">
              Step {autopilot.currentStep + 1} of {routePlan?.waypoints?.length || 0}
            </div>
          </div>
        )}
        <p className="help-text">
          {!routePlan ? 'Plan a route first to enable autopilot' : 
           'Autopilot will automatically navigate through all waypoints'}
        </p>
      </div>

      {/* Help Section */}
      <div className="nav-section help-section">
        <details className="help-details">
          <summary className="help-summary">
            <h4>📚 Navigation Help</h4>
          </summary>
          <div className="help-content">
            <div className="help-item">
              <strong>🚢 Navigate:</strong> Move between waypoints in the same system. Ship must be in orbit.
            </div>
            <div className="help-item">
              <strong>🚀 Jump:</strong> Instant travel via jump gates to connected systems. Consumes antimatter.
            </div>
            <div className="help-item">
              <strong>⚡ Warp:</strong> Travel to distant systems. Requires warp drive module and consumes fuel.
            </div>
            <div className="help-item">
              <strong>🛑 Emergency Stop:</strong> Abort current navigation. Only available during transit.
            </div>
            <div className="help-item">
              <strong>🗺️ Route Planning:</strong> Plan multi-waypoint journeys with fuel optimization.
            </div>
            <div className="help-item">
              <strong>🤖 Autopilot:</strong> Automated navigation through planned routes.
            </div>
            <div className="help-item">
              <strong>⏱️ Cooldown:</strong> Some actions trigger reactor cooldown. Wait before next action.
            </div>
          </div>
        </details>
      </div>
    </div>
  );
};

export default NavigationPanel;