import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ScanResults from './ScanResults';

const Intelligence = () => {
  const [ships, setShips] = useState([]);
  const [selectedShip, setSelectedShip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scanResults, setScanResults] = useState({});
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchShips();
  }, []);

  const fetchShips = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/ships');
      setShips(response.data);
      
      // Auto-select first ship if none selected
      if (response.data.length > 0 && !selectedShip) {
        setSelectedShip(response.data[0]);
      }
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch ships');
    } finally {
      setLoading(false);
    }
  };

  const handleScanComplete = (scanType, scanData) => {
    const timestamp = new Date().toISOString();
    setScanResults(prev => ({
      ...prev,
      [scanType]: {
        data: scanData,
        timestamp: timestamp,
        shipSymbol: selectedShip?.symbol
      }
    }));
    
    // Switch to the appropriate tab
    setActiveTab(scanType);
  };

  const performScan = async (scanType) => {
    if (!selectedShip) return;

    try {
      const endpoint = scanType === 'survey' 
        ? `/api/ships/${selectedShip.symbol}/survey`
        : `/api/ships/${selectedShip.symbol}/scan/${scanType}`;
      
      const response = await axios.post(endpoint);
      handleScanComplete(scanType, response.data.data);
    } catch (error) {
      console.error('Scan error:', error);
      alert(`Scan failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  if (loading) {
    return <div className="loading">Loading intelligence data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  const getTabIcon = (tab) => {
    const icons = {
      'overview': '📊',
      'systems': '🌌',
      'waypoints': '🪐',
      'ships': '📡',
      'survey': '⛏️'
    };
    return icons[tab] || '📊';
  };

  const renderOverview = () => (
    <div className="intelligence-overview">
      <h2>🔍 Intelligence & Scanning Overview</h2>
      
      <div className="overview-grid">
        <div className="overview-card">
          <h3>Available Capabilities</h3>
          <div className="capabilities-list">
            <div className="capability-item">
              <span className="capability-icon">🌌</span>
              <div>
                <strong>Long-Range Sensors</strong>
                <p>Detect nearby systems and celestial objects</p>
              </div>
            </div>
            <div className="capability-item">
              <span className="capability-icon">🪐</span>
              <div>
                <strong>Planetary Survey</strong>
                <p>Analyze waypoints for resources and composition</p>
              </div>
            </div>
            <div className="capability-item">
              <span className="capability-icon">📡</span>
              <div>
                <strong>Ship Scanner</strong>
                <p>Signal interception and threat assessment</p>
              </div>
            </div>
            <div className="capability-item">
              <span className="capability-icon">⛏️</span>
              <div>
                <strong>Resource Survey</strong>
                <p>Detailed resource mapping for mining operations</p>
              </div>
            </div>
          </div>
        </div>

        <div className="overview-card">
          <h3>Recent Scan Activity</h3>
          {Object.keys(scanResults).length > 0 ? (
            <div className="recent-scans">
              {Object.entries(scanResults)
                .sort(([,a], [,b]) => new Date(b.timestamp) - new Date(a.timestamp))
                .slice(0, 5)
                .map(([type, result]) => (
                  <div key={type} className="recent-scan-item">
                    <span className="scan-icon">{getTabIcon(type)}</span>
                    <div className="scan-info">
                      <strong>{type.charAt(0).toUpperCase() + type.slice(1)} Scan</strong>
                      <p>by {result.shipSymbol} - {new Date(result.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                ))
              }
            </div>
          ) : (
            <p className="no-scans">No scan data available. Use the scanner controls to begin intelligence gathering.</p>
          )}
        </div>

        <div className="overview-card">
          <h3>Scanner Controls</h3>
          {selectedShip ? (
            <div className="scanner-controls">
              <div className="selected-ship-display">
                <strong>Active Ship: {selectedShip.symbol}</strong>
                <p>Status: {selectedShip.nav?.status}</p>
                <p>Location: {selectedShip.nav?.waypointSymbol}</p>
              </div>
              <div className="quick-scan-buttons">
                <button onClick={() => performScan('systems')} className="quick-scan-btn systems">
                  🌌 Long-Range Scan
                </button>
                <button onClick={() => performScan('waypoints')} className="quick-scan-btn waypoints">
                  🪐 Planetary Survey
                </button>
                <button onClick={() => performScan('ships')} className="quick-scan-btn ships">
                  📡 Ship Scan
                </button>
                <button onClick={() => performScan('survey')} className="quick-scan-btn survey">
                  ⛏️ Resource Survey
                </button>
              </div>
            </div>
          ) : (
            <p>No ship selected. Please select a ship from the fleet to use scanning capabilities.</p>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="intelligence">
      <div className="card">
        <h1>🛰️ Intelligence & Scanning Hub</h1>
        <div className="ship-selector">
          <label htmlFor="ship-select">Active Scanner Ship:</label>
          <select 
            id="ship-select"
            value={selectedShip?.symbol || ''} 
            onChange={(e) => {
              const ship = ships.find(s => s.symbol === e.target.value);
              setSelectedShip(ship);
            }}
          >
            <option value="">Select a ship...</option>
            {ships.map(ship => (
              <option key={ship.symbol} value={ship.symbol}>
                {ship.symbol} - {ship.nav?.waypointSymbol}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="intelligence-tabs">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'systems' ? 'active' : ''}`}
          onClick={() => setActiveTab('systems')}
          disabled={!scanResults.systems}
        >
          🌌 Systems ({scanResults.systems ? '●' : '○'})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'waypoints' ? 'active' : ''}`}
          onClick={() => setActiveTab('waypoints')}
          disabled={!scanResults.waypoints}
        >
          🪐 Waypoints ({scanResults.waypoints ? '●' : '○'})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'ships' ? 'active' : ''}`}
          onClick={() => setActiveTab('ships')}
          disabled={!scanResults.ships}
        >
          📡 Ships ({scanResults.ships ? '●' : '○'})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'survey' ? 'active' : ''}`}
          onClick={() => setActiveTab('survey')}
          disabled={!scanResults.survey}
        >
          ⛏️ Surveys ({scanResults.survey ? '●' : '○'})
        </button>
      </div>

      <div className="intelligence-content">
        {activeTab === 'overview' && renderOverview()}
        
        {activeTab !== 'overview' && scanResults[activeTab] && (
          <ScanResults 
            scanData={scanResults[activeTab].data}
            scanType={activeTab}
            timestamp={scanResults[activeTab].timestamp}
          />
        )}
        
        {activeTab !== 'overview' && !scanResults[activeTab] && (
          <div className="no-scan-data">
            <h3>No {activeTab} scan data available</h3>
            <p>Use the scanner controls to gather {activeTab} intelligence data.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Intelligence;