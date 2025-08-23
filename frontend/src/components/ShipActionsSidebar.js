import React, { useState, useEffect } from 'react';

const ShipActionsSidebar = ({ selectedShip: propSelectedShip, onScanComplete }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanType, setScanType] = useState(null);
  const [selectedShip, setSelectedShip] = useState(propSelectedShip);

  // Listen for ship selection events from other components
  useEffect(() => {
    const handleShipSelection = (event) => {
      setSelectedShip(event.detail.ship);
    };

    window.addEventListener('shipSelected', handleShipSelection);
    return () => {
      window.removeEventListener('shipSelected', handleShipSelection);
    };
  }, []);

  // Update selected ship when prop changes
  useEffect(() => {
    if (propSelectedShip) {
      setSelectedShip(propSelectedShip);
    }
  }, [propSelectedShip]);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const performScan = async (type) => {
    if (!selectedShip || scanning) return;

    try {
      setScanning(true);
      setScanType(type);
      
      const response = await fetch(`/api/ships/${selectedShip.symbol}/scan/${type}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`Scan failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (onScanComplete) {
        onScanComplete(type, result.data);
      }
      
      alert(`${type.charAt(0).toUpperCase() + type.slice(1)} scan completed successfully!`);
    } catch (error) {
      console.error('Scan error:', error);
      alert(`Scan failed: ${error.message}`);
    } finally {
      setScanning(false);
      setScanType(null);
    }
  };

  const performSurvey = async () => {
    if (!selectedShip || scanning) return;

    try {
      setScanning(true);
      setScanType('survey');
      
      const response = await fetch(`/api/ships/${selectedShip.symbol}/survey`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`Survey failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (onScanComplete) {
        onScanComplete('survey', result.data);
      }
      
      alert('Resource survey completed successfully!');
    } catch (error) {
      console.error('Survey error:', error);
      alert(`Survey failed: ${error.message}`);
    } finally {
      setScanning(false);
      setScanType(null);
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
              <h4>🛸 {selectedShip.symbol}</h4>
              <p>Status: <span className={`status ${selectedShip.nav?.status?.toLowerCase()}`}>
                {selectedShip.nav?.status || 'UNKNOWN'}
              </span></p>
              <p>Location: {selectedShip.nav?.waypointSymbol || 'N/A'}</p>
            </div>
          )}

          <div className="action-section">
            <h4>🔍 Scanning & Intelligence</h4>
            <div className="action-buttons">
              <button 
                className="scan-btn systems"
                onClick={() => performScan('systems')}
                disabled={!selectedShip || scanning}
                title="Long-range sensors - Detect nearby systems and celestial objects"
              >
                {scanning && scanType === 'systems' ? '🔄 Scanning...' : '🌌 Long-Range Sensors'}
              </button>
              
              <button 
                className="scan-btn waypoints"
                onClick={() => performScan('waypoints')}
                disabled={!selectedShip || scanning}
                title="Planetary survey - Scan waypoints for resources and composition"
              >
                {scanning && scanType === 'waypoints' ? '🔄 Scanning...' : '🪐 Planetary Survey'}
              </button>
              
              <button 
                className="scan-btn ships"
                onClick={() => performScan('ships')}
                disabled={!selectedShip || scanning}
                title="Signal interception and threat assessment - Scan nearby ships"
              >
                {scanning && scanType === 'ships' ? '🔄 Scanning...' : '📡 Ship Scanner'}
              </button>
              
              <button 
                className="scan-btn survey"
                onClick={performSurvey}
                disabled={!selectedShip || scanning}
                title="Resource mapping - Create detailed survey of current waypoint"
              >
                {scanning && scanType === 'survey' ? '🔄 Surveying...' : '⛏️ Resource Survey'}
              </button>
            </div>
          </div>

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
        </div>
      )}
    </div>
  );
};

export default ShipActionsSidebar;