import React, { useState } from 'react';
import axios from 'axios';

const ShipActionsSidebar = ({ selectedShip, onShipUpdate }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [operationResults, setOperationResults] = useState(null);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleOperation = async (operationType, payload = {}) => {
    if (!selectedShip) {
      alert('Please select a ship first');
      return;
    }

    try {
      setLoading(true);
      setOperationResults(null);
      
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/${operationType}`, payload);
      
      setOperationResults({
        type: operationType,
        data: response.data.data,
        success: true
      });

      // Refresh ship data if operation completed successfully
      if (onShipUpdate) {
        setTimeout(async () => {
          try {
            const shipResponse = await axios.get('/api/ships');
            const updatedShip = shipResponse.data.find(ship => ship.symbol === selectedShip.symbol);
            if (updatedShip) {
              onShipUpdate(updatedShip);
            }
          } catch (err) {
            console.error('Failed to refresh ship data:', err);
          }
        }, 1000);
      }

    } catch (err) {
      setOperationResults({
        type: operationType,
        error: err.response?.data?.detail || 'Operation failed',
        success: false
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMiningOperation = async (operationType) => {
    if (operationType === 'survey') {
      await handleOperation('survey');
    } else if (operationType === 'extract') {
      await handleOperation('extract', {});
    }
  };

  const handleSalvageOperation = async () => {
    const targetSymbol = prompt('Enter target derelict ship or debris field symbol:');
    if (targetSymbol) {
      await handleOperation('salvage', { targetSymbol });
    }
  };

  const handleExplorationOperation = async () => {
    const targetSystem = prompt('Enter system symbol to explore:');
    if (targetSystem) {
      await handleOperation('explore', { targetSystem });
    }
  };

  const handleDiplomaticMission = async () => {
    const ambassadorSymbol = prompt('Enter ambassador cargo symbol:');
    const destinationSymbol = prompt('Enter diplomatic destination:');
    if (ambassadorSymbol && destinationSymbol) {
      await handleOperation('diplomatic-mission', { ambassadorSymbol, destinationSymbol });
    }
  };

  const handleSearchRescue = async () => {
    const searchArea = prompt('Enter search area (waypoint symbol):');
    const targetType = prompt('Search for SHIP or CREW?').toUpperCase();
    if (searchArea && (targetType === 'SHIP' || targetType === 'CREW')) {
      await handleOperation('search-rescue', { searchArea, targetType });
    }
  };

  const handleEscortMission = async () => {
    const protectedVesselSymbol = prompt('Enter protected vessel symbol:');
    const routeWaypoints = prompt('Enter route waypoints (comma-separated):')?.split(',').map(w => w.trim());
    if (protectedVesselSymbol && routeWaypoints) {
      await handleOperation('escort', { protectedVesselSymbol, routeWaypoints });
    }
  };

  const renderOperationResult = () => {
    if (!operationResults) return null;

    const { type, data, error, success } = operationResults;

    return (
      <div className={`operation-result ${success ? 'success' : 'error'}`}>
        <h4>Operation: {type.replace('-', ' ').toUpperCase()}</h4>
        {success ? (
          <div>
            {type === 'survey' && data.surveys && (
              <div>
                <p>✅ Survey created!</p>
                <p>Deposits found: {data.surveys[0]?.deposits?.map(d => d.symbol).join(', ')}</p>
              </div>
            )}
            {type === 'extract' && data.extraction && (
              <div>
                <p>✅ Extracted {data.extraction.yield.units} units of {data.extraction.yield.symbol}</p>
              </div>
            )}
            {type === 'salvage' && data.salvage && (
              <div>
                <p>✅ Salvage operation completed!</p>
                <p>Items recovered: {data.salvage.items.map(item => `${item.units} ${item.symbol}`).join(', ')}</p>
              </div>
            )}
            {type === 'explore' && data.exploration && (
              <div>
                <p>✅ Exploration completed!</p>
                <p>System: {data.exploration.systemSymbol}</p>
                <p>Charting progress: {data.exploration.chartingProgress}%</p>
                <p>New waypoints: {data.exploration.newWaypoints?.length || 0}</p>
              </div>
            )}
            {type === 'diplomatic-mission' && data.mission && (
              <div>
                <p>✅ Diplomatic mission started!</p>
                <p>Ambassador: {data.mission.ambassador}</p>
                <p>Bonus: {data.mission.diplomatic_bonus} credits</p>
              </div>
            )}
            {type === 'search-rescue' && data.search_rescue && (
              <div>
                <p>✅ Search & rescue completed!</p>
                {data.search_rescue.found ? (
                  <p>Found: {data.search_rescue.found}</p>
                ) : (
                  <p>No targets found in search area</p>
                )}
              </div>
            )}
            {type === 'escort' && data.escort && (
              <div>
                <p>✅ Escort mission started!</p>
                <p>Protecting: {data.escort.protectedVessel}</p>
                <p>Fee: {data.escort.escort_fee} credits</p>
              </div>
            )}
            {data.cooldown && (
              <p>⏱️ Cooldown: {data.cooldown.remainingSeconds}s</p>
            )}
          </div>
        ) : (
          <p>❌ {error}</p>
        )}
      </div>
    );
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
              <h4>Selected Ship: {selectedShip.symbol}</h4>
              <p>Status: {selectedShip.nav?.status}</p>
              <p>Location: {selectedShip.nav?.waypointSymbol}</p>
              <p>Cargo: {selectedShip.cargo?.units}/{selectedShip.cargo?.capacity}</p>
            </div>
          )}

          {/* Mining Operations */}
          <div className="action-section">
            <h4>⛏️ Mining Operations</h4>
            <div className="action-buttons">
              <button 
                onClick={() => handleMiningOperation('survey')}
                disabled={loading || !selectedShip}
                className="action-btn survey-btn"
              >
                📊 Create Survey
              </button>
              <button 
                onClick={() => handleMiningOperation('extract')}
                disabled={loading || !selectedShip}
                className="action-btn extract-btn"
              >
                ⛏️ Extract Resources
              </button>
            </div>
          </div>

          {/* Salvage Operations */}
          <div className="action-section">
            <h4>🔧 Salvage Missions</h4>
            <div className="action-buttons">
              <button 
                onClick={handleSalvageOperation}
                disabled={loading || !selectedShip}
                className="action-btn salvage-btn"
              >
                🚢 Salvage Operation
              </button>
            </div>
          </div>

          {/* Exploration */}
          <div className="action-section">
            <h4>🗺️ Exploration</h4>
            <div className="action-buttons">
              <button 
                onClick={handleExplorationOperation}
                disabled={loading || !selectedShip}
                className="action-btn exploration-btn"
              >
                🔍 Chart Unknown Systems
              </button>
            </div>
          </div>

          {/* Diplomatic Missions */}
          <div className="action-section">
            <h4>🤝 Diplomatic Missions</h4>
            <div className="action-buttons">
              <button 
                onClick={handleDiplomaticMission}
                disabled={loading || !selectedShip}
                className="action-btn diplomatic-btn"
              >
                👨‍💼 Transport Ambassador
              </button>
            </div>
          </div>

          {/* Search & Rescue */}
          <div className="action-section">
            <h4>🚁 Search & Rescue</h4>
            <div className="action-buttons">
              <button 
                onClick={handleSearchRescue}
                disabled={loading || !selectedShip}
                className="action-btn rescue-btn"
              >
                🆘 Search & Rescue
              </button>
            </div>
          </div>

          {/* Escort Missions */}
          <div className="action-section">
            <h4>🛡️ Escort Missions</h4>
            <div className="action-buttons">
              <button 
                onClick={handleEscortMission}
                disabled={loading || !selectedShip}
                className="action-btn escort-btn"
              >
                🚢 Escort Vessel
              </button>
            </div>
          </div>

          {/* Operation Results */}
          {renderOperationResult()}

          {loading && (
            <div className="loading-indicator">
              <p>🔄 Operation in progress...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ShipActionsSidebar;