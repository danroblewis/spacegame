import React, { useState } from 'react';
import axios from 'axios';

const ShipActionsSidebar = ({ selectedShip, onShipUpdate, onMessage }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [loading, setLoading] = useState({});
  const [combatState, setCombatState] = useState({
    weaponsArmed: false,
    shieldsActive: false,
    targetLocked: false,
    evasiveMode: false,
    pointDefenseActive: false
  });

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const getWeapons = () => {
    if (!selectedShip || !selectedShip.mounts) return [];
    return selectedShip.mounts.filter(mount => 
      mount.symbol && (
        mount.symbol.includes('LASER_CANNON') ||
        mount.symbol.includes('MISSILE_LAUNCHER') ||
        mount.symbol.includes('TURRET')
      )
    );
  };

  const getShields = () => {
    if (!selectedShip || !selectedShip.modules) return [];
    return selectedShip.modules.filter(module => 
      module.symbol && module.symbol.includes('SHIELD_GENERATOR')
    );
  };

  const handleWeaponArm = () => {
    setCombatState(prev => ({ ...prev, weaponsArmed: !prev.weaponsArmed }));
  };

  const handleShieldToggle = () => {
    setCombatState(prev => ({ ...prev, shieldsActive: !prev.shieldsActive }));
  };

  const handleTargetAcquisition = () => {
    setCombatState(prev => ({ ...prev, targetLocked: !prev.targetLocked }));
  };

  const handleEvasiveManeuvers = () => {
    setCombatState(prev => ({ ...prev, evasiveMode: !prev.evasiveMode }));
  };

  const handlePointDefense = () => {
    setCombatState(prev => ({ ...prev, pointDefenseActive: !prev.pointDefenseActive }));
  };

  const handleMissileLaunch = () => {
    if (!combatState.weaponsArmed || !combatState.targetLocked) {
      alert('Weapons must be armed and target must be locked before launching missiles');
      return;
    }
    alert('Missile launched!');
  };

  const weapons = getWeapons();
  const shields = getShields();

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

          <div className="action-section">
            <h4>⚔️ Combat & Defense</h4>
            <div className="combat-section">
              
              {/* Weapon Systems */}
              <div className="combat-subsection">
                <h5>🔫 Weapon Systems</h5>
                {weapons.length > 0 ? (
                  <div className="weapon-list">
                    {weapons.map((weapon, index) => (
                      <div key={index} className="weapon-item">
                        <span className="weapon-name">{weapon.name || weapon.symbol}</span>
                        <span className={`weapon-status ${combatState.weaponsArmed ? 'armed' : 'disarmed'}`}>
                          {combatState.weaponsArmed ? 'ARMED' : 'DISARMED'}
                        </span>
                      </div>
                    ))}
                    <button 
                      className={`combat-btn ${combatState.weaponsArmed ? 'active' : ''}`}
                      onClick={handleWeaponArm}
                    >
                      {combatState.weaponsArmed ? '🔴 Disarm Weapons' : '🟢 Arm Weapons'}
                    </button>
                  </div>
                ) : (
                  <div className="no-equipment">No weapons installed</div>
                )}
              </div>

              {/* Shield Systems */}
              <div className="combat-subsection">
                <h5>🛡️ Shield Systems</h5>
                {shields.length > 0 ? (
                  <div className="shield-list">
                    {shields.map((shield, index) => (
                      <div key={index} className="shield-item">
                        <span className="shield-name">{shield.name || shield.symbol}</span>
                        <span className={`shield-status ${combatState.shieldsActive ? 'active' : 'inactive'}`}>
                          {combatState.shieldsActive ? 'ACTIVE' : 'INACTIVE'}
                        </span>
                      </div>
                    ))}
                    <button 
                      className={`combat-btn ${combatState.shieldsActive ? 'active' : ''}`}
                      onClick={handleShieldToggle}
                    >
                      {combatState.shieldsActive ? '⬇️ Lower Shields' : '⬆️ Raise Shields'}
                    </button>
                  </div>
                ) : (
                  <div className="no-equipment">No shield generators installed</div>
                )}
              </div>

              {/* Combat Actions */}
              <div className="combat-subsection">
                <h5>🎯 Combat Actions</h5>
                <div className="combat-actions">
                  <button 
                    className={`combat-btn ${combatState.targetLocked ? 'active' : ''}`}
                    onClick={handleTargetAcquisition}
                  >
                    {combatState.targetLocked ? '🔒 Target Locked' : '🎯 Acquire Target'}
                  </button>
                  
                  <button 
                    className={`combat-btn ${combatState.evasiveMode ? 'active' : ''}`}
                    onClick={handleEvasiveManeuvers}
                  >
                    {combatState.evasiveMode ? '➡️ Standard Flight' : '🔄 Evasive Maneuvers'}
                  </button>
                  
                  <button 
                    className={`combat-btn ${combatState.pointDefenseActive ? 'active' : ''}`}
                    onClick={handlePointDefense}
                  >
                    {combatState.pointDefenseActive ? '🔴 Point Defense ON' : '⚪ Point Defense OFF'}
                  </button>
                  
                  <button 
                    className="combat-btn missile-btn"
                    onClick={handleMissileLaunch}
                    disabled={!combatState.weaponsArmed || !combatState.targetLocked}
                  >
                    🚀 Launch Missiles
                  </button>
                </div>
              </div>

              {/* Combat Status */}
              <div className="combat-status">
                <h6>Status</h6>
                <div className="status-indicators">
                  <div className={`status-item ${combatState.weaponsArmed ? 'active' : ''}`}>
                    ⚔️ Weapons {combatState.weaponsArmed ? 'Armed' : 'Disarmed'}
                  </div>
                  <div className={`status-item ${combatState.shieldsActive ? 'active' : ''}`}>
                    🛡️ Shields {combatState.shieldsActive ? 'Up' : 'Down'}
                  </div>
                  <div className={`status-item ${combatState.targetLocked ? 'active' : ''}`}>
                    🎯 Target {combatState.targetLocked ? 'Locked' : 'None'}
                  </div>
                  <div className={`status-item ${combatState.evasiveMode ? 'active' : ''}`}>
                    🔄 {combatState.evasiveMode ? 'Evasive' : 'Standard'} Flight
                  </div>
                </div>
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