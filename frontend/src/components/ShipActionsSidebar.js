import React, { useState } from 'react';

const ShipActionsSidebar = ({ selectedShip, onShipUpdate }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
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
        </div>
      )}
    </div>
  );
};

export default ShipActionsSidebar;