import React, { useState } from 'react';
import axios from 'axios';
import { useShip } from '../App';

const ShipActionsSidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [loading, setLoading] = useState(false);
  const { selectedShip, updateSelectedShip } = useShip();

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleEmergencyAction = async (action, payload = {}) => {
    if (!selectedShip) {
      alert('No ship selected');
      return;
    }

    // Add confirmation for destructive actions
    const destructiveActions = ['self-destruct', 'abandon-ship', 'eject-crew'];
    if (destructiveActions.includes(action)) {
      const confirmed = window.confirm(
        `Are you sure you want to ${action.replace('-', ' ')} ${selectedShip.symbol}? This action cannot be undone.`
      );
      if (!confirmed) return;
      payload.confirm = true;
    }

    try {
      setLoading(true);
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/${action}`, payload);
      
      if (response.data?.data?.message) {
        alert(response.data.data.message);
      }

      // Update ship data
      if (action === 'self-destruct') {
        // Ship was destroyed, clear selection
        updateSelectedShip(null);
      } else {
        // Fetch updated ship data
        const shipResponse = await axios.get('/api/ships');
        const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
        if (updatedShip) {
          updateSelectedShip(updatedShip);
        }
      }

    } catch (err) {
      alert(err.response?.data?.detail || `Failed to execute ${action}`);
    } finally {
      setLoading(false);
    }
  };

  const handleEmergencyRepair = async () => {
    const system = prompt('Which system to repair? (hull, engine, reactor, life_support, navigation)', 'hull');
    if (system) {
      await handleEmergencyAction('emergency-repair', { system });
    }
  };

  const handleDistressBeacon = async () => {
    const message = prompt('Distress message:', 'Emergency assistance required');
    if (message) {
      await handleEmergencyAction('distress-beacon', { message });
    }
  };

  return (
    <div className={`ship-actions-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <h3>🚀 Ship Actions</h3>
        <button 
          className="collapse-btn" 
          onClick={toggleSidebar}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? '►' : '◄'}
        </button>
      </div>
      
      {!isCollapsed && (
        <div className="sidebar-content">
          {selectedShip && (
            <div className="selected-ship-info">
              <h4>Selected Ship</h4>
              <p><strong>{selectedShip.symbol}</strong></p>
              <p>Status: {selectedShip.nav?.status}</p>
              <p>Location: {selectedShip.nav?.waypointSymbol}</p>
              <p>Crew: {selectedShip.crew?.current}/{selectedShip.crew?.capacity}</p>
            </div>
          )}

          <div className="action-section">
            <h4>Navigation</h4>
            <div className="action-buttons-placeholder">
              <div className="placeholder-text">
                Navigation actions will appear here
              </div>
            </div>
          </div>

          <div className="action-section">
            <h4>Trading</h4>
            <div className="action-buttons-placeholder">
              <div className="placeholder-text">
                Trading actions will appear here
              </div>
            </div>
          </div>

          <div className="action-section">
            <h4>Mining</h4>
            <div className="action-buttons-placeholder">
              <div className="placeholder-text">
                Mining actions will appear here
              </div>
            </div>
          </div>

          <div className="action-section">
            <h4>Refuel & Repair</h4>
            <div className="action-buttons-placeholder">
              <div className="placeholder-text">
                Maintenance actions will appear here
              </div>
            </div>
          </div>

          {/* Emergency Actions Section */}
          <div className="action-section emergency-section">
            <h4>🚨 Emergency Actions</h4>
            <div className="emergency-actions">
              <button 
                className="emergency-btn eject-crew"
                onClick={() => handleEmergencyAction('eject-crew')}
                disabled={loading || !selectedShip}
                title="Emergency escape pods"
              >
                🚀 Eject Crew
              </button>

              <button 
                className="emergency-btn distress-beacon"
                onClick={handleDistressBeacon}
                disabled={loading || !selectedShip}
                title="Call for help"
              >
                📡 Distress Beacon
              </button>

              <button 
                className="emergency-btn emergency-repair"
                onClick={handleEmergencyRepair}
                disabled={loading || !selectedShip}
                title="Quick fix critical systems"
              >
                🔧 Emergency Repair
              </button>

              <button 
                className="emergency-btn salvage-mode"
                onClick={() => handleEmergencyAction('salvage-mode')}
                disabled={loading || !selectedShip}
                title="Recover from severe damage"
              >
                🛠️ Salvage Mode
              </button>

              <button 
                className="emergency-btn abandon-ship"
                onClick={() => handleEmergencyAction('abandon-ship')}
                disabled={loading || !selectedShip}
                title="Leave ship in escape pods"
              >
                🆘 Abandon Ship
              </button>

              <button 
                className="emergency-btn self-destruct"
                onClick={() => handleEmergencyAction('self-destruct')}
                disabled={loading || !selectedShip}
                title="Scuttle ship"
              >
                💥 Self-Destruct
              </button>
            </div>
          </div>

          {!selectedShip && (
            <div className="no-ship-selected">
              <p>Select a ship from the Fleet page to access ship actions.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ShipActionsSidebar;