import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ShipActionsSidebar = ({ selectedShip, onShipUpdate, onMessage }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [securityStatus, setSecurityStatus] = useState(null);
  const [loading, setLoading] = useState({});

  return (
    <div className={`ship-actions-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <h3>🚀 Ship Actions</h3>
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="collapse-btn"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? '▶' : '◀'}
        </button>
      </div>

      {!isCollapsed && (
        <div className="sidebar-content">
          {!selectedShip && (
            <div className="no-ship-selected">
              <p>Select a ship to view available actions</p>
            </div>
          )}

          {selectedShip && (
            <>
              <div className="selected-ship-info">
                <h4>📍 {selectedShip.symbol}</h4>
                <p>Status: {selectedShip.nav?.status}</p>
                <p>Location: {selectedShip.nav?.waypointSymbol}</p>
              </div>

              <div className="action-section">
                <h4>🧭 Navigation</h4>
                <div className="action-buttons">
                  <button className="action-btn">Navigate</button>
                  <button className="action-btn">Orbit</button>
                  <button className="action-btn">Dock</button>
                </div>
              </div>

              <div className="action-section">
                <h4>⚔️ Combat</h4>
                <div className="action-buttons">
                  <button className="action-btn">Scan</button>
                  <button className="action-btn">Attack</button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ShipActionsSidebar;