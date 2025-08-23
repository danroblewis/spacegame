import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ShipActionsSidebar = ({ selectedShip, onShipUpdate, onMessage }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [securityStatus, setSecurityStatus] = useState(null);
  const [loading, setLoading] = useState({});
  const [message, setMessage] = useState('');

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

  // Fetch security status when selected ship changes
  useEffect(() => {
    if (selectedShip) {
      fetchSecurityStatus();
    }
  }, [selectedShip]);

  const fetchSecurityStatus = async () => {
    if (!selectedShip) return;
    
    try {
      const response = await axios.get(`/api/ships/${selectedShip.symbol}/security/status`);
      setSecurityStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch security status:', error);
    }
  };

  const handleSecurityAction = async (endpoint, action, actionName) => {
    if (!selectedShip) return;
    
    setLoading(prev => ({ ...prev, [endpoint]: true }));
    setMessage('');
    
    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/security/${endpoint}`, {
        action: action
      });
      
      setMessage(response.data.message);
      setSecurityStatus(response.data.status);
      
      // Clear message after 3 seconds
      setTimeout(() => setMessage(''), 3000);
      
    } catch (error) {
      setMessage(error.response?.data?.detail || `Failed to ${action} ${actionName}`);
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setLoading(prev => ({ ...prev, [endpoint]: false }));
    }
  };

  const handleRechargeCountermeasures = async () => {
    if (!selectedShip) return;
    
    setLoading(prev => ({ ...prev, recharge: true }));
    setMessage('');
    
    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/security/recharge-countermeasures`);
      setMessage(response.data.message);
      setSecurityStatus(response.data.status);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to recharge countermeasures');
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setLoading(prev => ({ ...prev, recharge: false }));
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
          )}

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

              {message && (
                <div className="action-message">
                  {message}
                </div>
              )}

              {securityStatus && (
                <div className="energy-status">
                  <span>⚡ Energy Usage: {securityStatus.energyConsumption}%</span>
                </div>
              )}

              <div className="action-section">
                <h4>🛡️ Security & Stealth</h4>
                
                {/* Cloaking Device */}
                <div className="action-group">
                  <div className="action-header">
                    <span className="action-icon">👻</span>
                    <span className="action-name">Cloaking Device</span>
                    {securityStatus?.cloakingActive && <span className="status-active">ACTIVE</span>}
                    {securityStatus?.cloakingCooldown > 0 && <span className="status-cooldown">COOLDOWN</span>}
                  </div>
                  <div className="action-buttons">
                    <button 
                      className={`action-btn ${securityStatus?.cloakingActive ? 'btn-danger' : 'btn-primary'}`}
                      onClick={() => handleSecurityAction('cloaking', securityStatus?.cloakingActive ? 'deactivate' : 'activate', 'cloaking')}
                      disabled={loading.cloaking || (securityStatus?.cloakingCooldown > 0)}
                    >
                      {loading.cloaking ? 'Processing...' : (securityStatus?.cloakingActive ? 'Deactivate' : 'Activate')}
                    </button>
                  </div>
                </div>

                {/* Signal Jamming */}
                <div className="action-group">
                  <div className="action-header">
                    <span className="action-icon">📡</span>
                    <span className="action-name">Signal Jamming</span>
                    {securityStatus?.signalJammingActive && <span className="status-active">ACTIVE</span>}
                  </div>
                  <div className="action-buttons">
                    <button 
                      className={`action-btn ${securityStatus?.signalJammingActive ? 'btn-danger' : 'btn-primary'}`}
                      onClick={() => handleSecurityAction('jamming', securityStatus?.signalJammingActive ? 'deactivate' : 'activate', 'jamming')}
                      disabled={loading.jamming}
                    >
                      {loading.jamming ? 'Processing...' : (securityStatus?.signalJammingActive ? 'Deactivate' : 'Activate')}
                    </button>
                  </div>
                  {securityStatus?.signalJammingActive && (
                    <div className="action-info">Range: {securityStatus.jammingRadius} units</div>
                  )}
                </div>

                {/* Electronic Warfare */}
                <div className="action-group">
                  <div className="action-header">
                    <span className="action-icon">💻</span>
                    <span className="action-name">Electronic Warfare</span>
                    {securityStatus?.electronicWarfareActive && <span className="status-active">ACTIVE</span>}
                  </div>
                  <div className="action-buttons">
                    <button 
                      className={`action-btn ${securityStatus?.electronicWarfareActive ? 'btn-danger' : 'btn-primary'}`}
                      onClick={() => handleSecurityAction('electronic-warfare', securityStatus?.electronicWarfareActive ? 'deactivate' : 'activate', 'electronic warfare')}
                      disabled={loading['electronic-warfare']}
                    >
                      {loading['electronic-warfare'] ? 'Processing...' : (securityStatus?.electronicWarfareActive ? 'Deactivate' : 'Activate')}
                    </button>
                  </div>
                </div>

                {/* Stealth Mode */}
                <div className="action-group">
                  <div className="action-header">
                    <span className="action-icon">🌫️</span>
                    <span className="action-name">Stealth Mode</span>
                    {securityStatus?.stealthModeActive && <span className="status-active">LEVEL {securityStatus.stealthModeLevel}</span>}
                  </div>
                  <div className="action-buttons">
                    <button 
                      className={`action-btn ${securityStatus?.stealthModeActive ? 'btn-danger' : 'btn-primary'}`}
                      onClick={() => handleSecurityAction('stealth-mode', securityStatus?.stealthModeActive ? 'deactivate' : 'activate', 'stealth mode')}
                      disabled={loading['stealth-mode']}
                    >
                      {loading['stealth-mode'] ? 'Processing...' : (securityStatus?.stealthModeActive ? 'Deactivate' : 'Activate')}
                    </button>
                  </div>
                </div>

                {/* Countermeasures */}
                <div className="action-group">
                  <div className="action-header">
                    <span className="action-icon">✨</span>
                    <span className="action-name">Countermeasures</span>
                    {securityStatus?.countermeasuresActive && <span className="status-active">DEPLOYED</span>}
                  </div>
                  <div className="action-buttons">
                    <button 
                      className="action-btn btn-primary"
                      onClick={() => handleSecurityAction('countermeasures', 'activate', 'countermeasures')}
                      disabled={loading.countermeasures || securityStatus?.countermeasuresCharges <= 0}
                    >
                      {loading.countermeasures ? 'Deploying...' : 'Deploy'}
                    </button>
                    <button 
                      className="action-btn btn-secondary"
                      onClick={handleRechargeCountermeasures}
                      disabled={loading.recharge}
                    >
                      {loading.recharge ? 'Recharging...' : 'Recharge'}
                    </button>
                  </div>
                  <div className="action-info">Charges: {securityStatus?.countermeasuresCharges || 0}/3</div>
                </div>

                {/* Encryption */}
                <div className="action-group">
                  <div className="action-header">
                    <span className="action-icon">🔐</span>
                    <span className="action-name">Encryption</span>
                    {securityStatus?.encryptionActive && <span className="status-active">LEVEL {securityStatus.encryptionLevel}</span>}
                  </div>
                  <div className="action-buttons">
                    <button 
                      className={`action-btn ${securityStatus?.encryptionActive ? 'btn-danger' : 'btn-primary'}`}
                      onClick={() => handleSecurityAction('encryption', securityStatus?.encryptionActive ? 'deactivate' : 'activate', 'encryption')}
                      disabled={loading.encryption}
                    >
                      {loading.encryption ? 'Processing...' : (securityStatus?.encryptionActive ? 'Deactivate' : 'Activate')}
                    </button>
                  </div>
                </div>
              </div>

              <div className="action-section">
                <h4>🌍 Navigation</h4>
                <div className="action-buttons">
                  <button 
                    onClick={handleDock}
                    disabled={!canPerformAction('dock') || isButtonDisabled('Dock')}
                    className="action-btn dock-btn"
                    title={`Dock ship ${getActionRequirement('dock')}`}
                  >
                    {loading.Dock ? '🔄' : '🏗️'} Dock {getActionRequirement('dock')}
                  </button>
                  
                  <button 
                    onClick={handleOrbit}
                    disabled={!canPerformAction('orbit') || isButtonDisabled('Orbit')}
                    className="action-btn orbit-btn"
                    title={`Put ship in orbit ${getActionRequirement('orbit')}`}
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
                    onClick={handleScrap}
                    disabled={!canPerformAction('scrap') || isButtonDisabled('Scrap')}
                    className="action-btn danger-btn"
                    title={`Scrap ship for credits ${getActionRequirement('scrap')}`}
                  >
                    {loading.Scrap ? '🔄' : '💥'} Scrap Ship {getActionRequirement('scrap')}
                  </button>
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