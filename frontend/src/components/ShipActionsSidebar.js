import React, { useState } from 'react';
import axios from 'axios';

const ShipActionsSidebar = ({ selectedShip, onShipUpdate, onMessage }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [loading, setLoading] = useState({});
  const [operationResults, setOperationResults] = useState(null);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const setLoadingState = (action, isLoading) => {
    setLoading(prev => ({ ...prev, [action]: isLoading }));
  };

  const showMessage = (message, type = 'info') => {
    if (onMessage) {
      onMessage(message, type);
    } else {
      alert(message);
    }
  };

  const executeShipAction = async (action, endpoint, payload = null, method = 'POST') => {
    if (!selectedShip) {
      showMessage('Please select a ship first', 'warning');
      return;
    }

    setLoadingState(action, true);
    try {
      const config = {
        method: method,
        url: `/api/ships/${selectedShip.symbol}/${endpoint}`,
      };
      
      if (payload && method === 'POST') {
        config.data = payload;
      }

      const response = await axios(config);
      
      if (response.data?.data) {
        if (response.data.data.nav) {
          // Update ship navigation status
          const updatedShip = { 
            ...selectedShip, 
            nav: { ...selectedShip.nav, ...response.data.data.nav }
          };
          onShipUpdate && onShipUpdate(updatedShip);
        } else if (response.data.data.ship) {
          // Full ship update
          onShipUpdate && onShipUpdate(response.data.data.ship);
        }
        
        // Show transaction details if available
        if (response.data.data.transaction) {
          const tx = response.data.data.transaction;
          showMessage(`${action} successful! ${tx.totalPrice ? `Cost: ${tx.totalPrice} credits` : ''}`, 'success');
        } else {
          showMessage(`${action} successful!`, 'success');
        }
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || `Failed to ${action.toLowerCase()}`;
      showMessage(errorMsg, 'error');
    } finally {
      setLoadingState(action, false);
    }
  };

  // Basic ship actions
  const handleDock = () => executeShipAction('Dock', 'dock');
  const handleOrbit = () => executeShipAction('Orbit', 'orbit');
  const handleRefuel = () => executeShipAction('Refuel', 'refuel');
  const handleRepair = () => executeShipAction('Repair', 'repair');
  
  const handleScrap = () => {
    if (window.confirm(`Are you sure you want to scrap ${selectedShip?.symbol}? This action cannot be undone!`)) {
      executeShipAction('Scrap', 'scrap');
    }
  };

  const handleGetRepairCost = () => executeShipAction('Get Repair Cost', 'repair', null, 'GET');
  const handleGetScrapValue = () => executeShipAction('Get Scrap Value', 'scrap', null, 'GET');

  const handleTransfer = () => {
    const targetShip = prompt('Enter target ship symbol:');
    const tradeSymbol = prompt('Enter cargo symbol to transfer:');
    const units = prompt('Enter number of units to transfer:');
    
    if (targetShip && tradeSymbol && units) {
      const payload = {
        shipSymbol: targetShip,
        tradeSymbol: tradeSymbol,
        units: parseInt(units)
      };
      executeShipAction('Transfer Cargo', 'transfer', payload);
    }
  };

  // Specialized operation handlers
  const handleOperation = async (operationType, payload = {}) => {
    if (!selectedShip) {
      showMessage('Please select a ship first', 'warning');
      return;
    }

    try {
      setLoadingState(operationType, true);
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
      setLoadingState(operationType, false);
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

  // Helper functions for action availability
  const getActionRequirement = (action) => {
    if (!selectedShip) return '(No ship selected)';
    
    switch (action) {
      case 'dock':
        return selectedShip.nav?.status === 'DOCKED' ? '(Already docked)' : 
               selectedShip.nav?.status === 'IN_TRANSIT' ? '(Ship in transit)' : '';
      case 'orbit':
        return selectedShip.nav?.status === 'IN_ORBIT' ? '(Already in orbit)' : 
               selectedShip.nav?.status === 'IN_TRANSIT' ? '(Ship in transit)' : '';
      case 'refuel':
      case 'repair':
      case 'scrap':
        return selectedShip.nav?.status !== 'DOCKED' ? '(Must be docked)' : '';
      default:
        return '';
    }
  };

  const canPerformAction = (action) => {
    if (!selectedShip) return false;
    
    switch (action) {
      case 'dock':
        return selectedShip.nav?.status === 'IN_ORBIT';
      case 'orbit':
        return selectedShip.nav?.status === 'DOCKED';
      case 'refuel':
      case 'repair':
      case 'scrap':
        return selectedShip.nav?.status === 'DOCKED';
      default:
        return true;
    }
  };

  const isButtonDisabled = (action) => {
    return loading[action] || !canPerformAction(action.toLowerCase());
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
              <p>Status: <span className={`status-${selectedShip.nav?.status?.toLowerCase()}`}>
                {selectedShip.nav?.status}
              </span></p>
              <p>Location: {selectedShip.nav?.waypointSymbol}</p>
              <p>Cargo: {selectedShip.cargo?.units}/{selectedShip.cargo?.capacity}</p>
            </div>
          )}

          {/* Basic Navigation */}
          <div className="action-section">
            <h4>🚀 Navigation</h4>
            <div className="action-buttons">
              <button 
                onClick={handleDock}
                disabled={!canPerformAction('dock') || isButtonDisabled('Dock')}
                className="action-btn dock-btn"
                title={`Dock ship ${getActionRequirement('dock')}`}
              >
                {loading.Dock ? '🔄' : '🛬'} Dock {getActionRequirement('dock')}
              </button>
              <button 
                onClick={handleOrbit}
                disabled={!canPerformAction('orbit') || isButtonDisabled('Orbit')}
                className="action-btn orbit-btn"
                title={`Enter orbit ${getActionRequirement('orbit')}`}
              >
                {loading.Orbit ? '🔄' : '🌍'} Orbit {getActionRequirement('orbit')}
              </button>
            </div>
          </div>

          {/* Mining Operations */}
          <div className="action-section">
            <h4>⛏️ Mining Operations</h4>
            <div className="action-buttons">
              <button 
                onClick={() => handleMiningOperation('survey')}
                disabled={loading.survey || !selectedShip}
                className="action-btn survey-btn"
              >
                {loading.survey ? '🔄' : '📊'} Create Survey
              </button>
              <button 
                onClick={() => handleMiningOperation('extract')}
                disabled={loading.extract || !selectedShip}
                className="action-btn extract-btn"
              >
                {loading.extract ? '🔄' : '⛏️'} Extract Resources
              </button>
            </div>
          </div>

          {/* Maintenance */}
          <div className="action-section">
            <h4>⛽ Maintenance</h4>
            <div className="action-buttons">
              <button 
                onClick={handleRefuel}
                disabled={!canPerformAction('refuel') || isButtonDisabled('Refuel')}
                className="action-btn refuel-btn"
                title={`Refuel ship ${getActionRequirement('refuel')}`}
              >
                {loading.Refuel ? '🔄' : '⛽'} Refuel {getActionRequirement('refuel')}
              </button>
              <button 
                onClick={handleGetRepairCost}
                disabled={!canPerformAction('repair') || isButtonDisabled('Get Repair Cost')}
                className="action-btn repair-cost-btn"
                title={`Check repair cost ${getActionRequirement('repair')}`}
              >
                {loading['Get Repair Cost'] ? '🔄' : '🔍'} Check Repair Cost {getActionRequirement('repair')}
              </button>
              <button 
                onClick={handleRepair}
                disabled={!canPerformAction('repair') || isButtonDisabled('Repair')}
                className="action-btn repair-btn"
                title={`Repair ship ${getActionRequirement('repair')}`}
              >
                {loading.Repair ? '🔄' : '🔧'} Repair {getActionRequirement('repair')}
              </button>
            </div>
          </div>

          {/* Salvage Operations */}
          <div className="action-section">
            <h4>🔧 Salvage Missions</h4>
            <div className="action-buttons">
              <button 
                onClick={handleSalvageOperation}
                disabled={loading.salvage || !selectedShip}
                className="action-btn salvage-btn"
              >
                {loading.salvage ? '🔄' : '🚢'} Salvage Operation
              </button>
            </div>
          </div>

          {/* Exploration */}
          <div className="action-section">
            <h4>🗺️ Exploration</h4>
            <div className="action-buttons">
              <button 
                onClick={handleExplorationOperation}
                disabled={loading.explore || !selectedShip}
                className="action-btn exploration-btn"
              >
                {loading.explore ? '🔄' : '🔍'} Chart Unknown Systems
              </button>
            </div>
          </div>

          {/* Diplomatic Missions */}
          <div className="action-section">
            <h4>🤝 Diplomatic Missions</h4>
            <div className="action-buttons">
              <button 
                onClick={handleDiplomaticMission}
                disabled={loading['diplomatic-mission'] || !selectedShip}
                className="action-btn diplomatic-btn"
              >
                {loading['diplomatic-mission'] ? '🔄' : '👨‍💼'} Transport Ambassador
              </button>
            </div>
          </div>

          {/* Search & Rescue */}
          <div className="action-section">
            <h4>🚁 Search & Rescue</h4>
            <div className="action-buttons">
              <button 
                onClick={handleSearchRescue}
                disabled={loading['search-rescue'] || !selectedShip}
                className="action-btn rescue-btn"
              >
                {loading['search-rescue'] ? '🔄' : '🆘'} Search & Rescue
              </button>
            </div>
          </div>

          {/* Escort Missions */}
          <div className="action-section">
            <h4>🛡️ Escort Missions</h4>
            <div className="action-buttons">
              <button 
                onClick={handleEscortMission}
                disabled={loading.escort || !selectedShip}
                className="action-btn escort-btn"
              >
                {loading.escort ? '🔄' : '🚢'} Escort Vessel
              </button>
            </div>
          </div>

          {/* Cargo & Fleet */}
          <div className="action-section">
            <h4>📦 Cargo & Fleet</h4>
            <div className="action-buttons">
              <button 
                onClick={handleTransfer}
                disabled={isButtonDisabled('Transfer Cargo')}
                className="action-btn transfer-btn"
                title="Transfer cargo to another ship"
              >
                {loading['Transfer Cargo'] ? '🔄' : '📦'} Transfer Cargo
              </button>
            </div>
          </div>

          <div className="action-section danger-section">
            <h4>⚠️ Dangerous Operations</h4>
            <div className="action-buttons">
              <button 
                onClick={handleGetScrapValue}
                disabled={!canPerformAction('scrap') || isButtonDisabled('Get Scrap Value')}
                className="action-btn scrap-value-btn"
                title={`Check scrap value ${getActionRequirement('scrap')}`}
              >
                {loading['Get Scrap Value'] ? '🔄' : '💰'} Check Scrap Value {getActionRequirement('scrap')}
              </button>
              <button 
                onClick={handleScrap}
                disabled={!canPerformAction('scrap') || isButtonDisabled('Scrap')}
                className="action-btn danger-btn"
                title={`Scrap ship for credits ${getActionRequirement('scrap')}`}
              >
                {loading.Scrap ? '🔄' : '💥'} Scrap Ship {getActionRequirement('scrap')}
              </button>
            </div>
          </div>

          {/* Operation Results */}
          {renderOperationResult()}

          {Object.values(loading).some(Boolean) && (
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