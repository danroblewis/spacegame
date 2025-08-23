import React, { useState } from 'react';
import axios from 'axios';

const ShipActionsSidebar = ({ selectedShip, onShipUpdate, onMessage }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [loading, setLoading] = useState({});

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

  // Scanning functions
  const handleSystemScan = () => executeShipAction('System Scan', 'scan/systems');
  const handleWaypointScan = () => executeShipAction('Waypoint Scan', 'scan/waypoints');
  const handleShipScan = () => executeShipAction('Ship Scan', 'scan/ships');
  const handleSurvey = () => executeShipAction('Survey', 'survey');

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

  const isButtonDisabled = (action) => {
    return loading[action] || !selectedShip;
  };

  const getActionRequirement = (action) => {
    if (!selectedShip) return '';
    
    const status = selectedShip.nav?.status;
    switch (action) {
      case 'dock':
        return status === 'DOCKED' ? '(Already docked)' : '(Requires orbit)';
      case 'orbit':
        return status === 'IN_ORBIT' ? '(Already in orbit)' : '(Requires docked)';
      case 'refuel':
      case 'repair':
      case 'scrap':
        return status !== 'DOCKED' ? '(Requires docked)' : '';
      default:
        return '';
    }
  };

  const canPerformAction = (action) => {
    if (!selectedShip) return false;
    
    const status = selectedShip.nav?.status;
    switch (action) {
      case 'dock':
        return status === 'IN_ORBIT';
      case 'orbit':
        return status === 'DOCKED';
      case 'refuel':
      case 'repair':
      case 'scrap':
        return status === 'DOCKED';
      case 'transfer':
        return true; // Can transfer in any state, API will validate
      default:
        return true;
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
              <h4>{selectedShip.symbol}</h4>
              <p>Status: <span className={`status-${selectedShip.nav?.status?.toLowerCase()}`}>
                {selectedShip.nav?.status}
              </span></p>
              <p>Location: {selectedShip.nav?.waypointSymbol}</p>
            </div>
          )}

          <div className="action-section">
            <h4>🎯 Navigation</h4>
            <div className="action-buttons">
              <button 
                onClick={handleDock}
                disabled={!canPerformAction('dock') || isButtonDisabled('Dock')}
                className="action-btn dock-btn"
                title={`Dock at current waypoint ${getActionRequirement('dock')}`}
              >
                {loading.Dock ? '🔄' : '🚢'} Dock {getActionRequirement('dock')}
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
                className="action-btn info-btn"
                title="Get repair cost estimate"
              >
                {loading['Get Repair Cost'] ? '🔄' : '💰'} Repair Cost
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

          <div className="action-section">
            <h4>🔍 Scanning & Intelligence</h4>
            <div className="action-buttons">
              <button 
                onClick={handleSystemScan}
                disabled={isButtonDisabled('System Scan')}
                className="action-btn scan-btn systems"
                title="Long-range sensors - Detect nearby systems and celestial objects"
              >
                {loading['System Scan'] ? '🔄' : '🌌'} Long-Range Sensors
              </button>
              
              <button 
                onClick={handleWaypointScan}
                disabled={isButtonDisabled('Waypoint Scan')}
                className="action-btn scan-btn waypoints"
                title="Planetary survey - Scan waypoints for resources and composition"
              >
                {loading['Waypoint Scan'] ? '🔄' : '🪐'} Planetary Survey
              </button>
              
              <button 
                onClick={handleShipScan}
                disabled={isButtonDisabled('Ship Scan')}
                className="action-btn scan-btn ships"
                title="Signal interception and threat assessment - Scan nearby ships"
              >
                {loading['Ship Scan'] ? '🔄' : '📡'} Ship Scanner
              </button>
              
              <button 
                onClick={handleSurvey}
                disabled={isButtonDisabled('Survey')}
                className="action-btn scan-btn survey"
                title="Resource mapping - Create detailed survey of current waypoint"
              >
                {loading['Survey'] ? '🔄' : '⛏️'} Resource Survey
              </button>
            </div>
          </div>

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
                className="action-btn info-btn"
                title="Get scrap value estimate"
              >
                {loading['Get Scrap Value'] ? '🔄' : '💰'} Scrap Value
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
        </div>
      )}
    </div>
  );
};

export default ShipActionsSidebar;