import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Map from './Map';

const Fleet = ({ selectedShip, onShipSelect, onShipUpdate }) => {
  const [ships, setShips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
        onShipSelect(response.data[0]);
      }
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch ships');
    } finally {
      setLoading(false);
    }
  };

  const handleShipClick = (ship) => {
    onShipSelect(ship);
  };

  const handleShipUpdate = (updatedShip) => {
    // Update the ship in the ships array
    setShips(prevShips => 
      prevShips.map(ship => 
        ship.symbol === updatedShip.symbol ? updatedShip : ship
      )
    );
    // Notify parent component
    onShipUpdate(updatedShip);
  };

  const getShipStatusColor = (status) => {
    switch (status) {
      case 'IN_TRANSIT':
        return 'active';
      case 'IN_ORBIT':
        return 'active';
      case 'DOCKED':
        return 'inactive';
      default:
        return 'inactive';
    }
  };

  const formatCargo = (cargo) => {
    if (!cargo || !cargo.inventory) return 'Empty';
    return cargo.inventory.map(item => `${item.symbol}: ${item.units}`).join(', ');
  };

  const formatEquipment = (ship) => {
    const weapons = ship.mounts?.filter(mount => 
      mount.symbol && (
        mount.symbol.includes('LASER_CANNON') ||
        mount.symbol.includes('MISSILE_LAUNCHER') ||
        mount.symbol.includes('TURRET')
      )
    ) || [];
    
    const shields = ship.modules?.filter(module => 
      module.symbol && module.symbol.includes('SHIELD_GENERATOR')
    ) || [];

    return {
      weapons: weapons.length,
      shields: shields.length
    };
  };

  if (loading) {
    return <div className="loading">Loading fleet data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="fleet">
      <div className="card">
        <div className="card-header">
          <h2>🚀 Fleet Management</h2>
          <p className="text-muted">Manage your ships and their operations</p>
        </div>
        
        <div className="fleet-content">
          <div className="ships-list">
            <h3>Ships ({ships.length})</h3>
            <div className="ships-grid">
              {ships.map((ship) => {
                const equipment = formatEquipment(ship);
                const isSelected = selectedShip && selectedShip.symbol === ship.symbol;
                
                return (
                  <div 
                    key={ship.symbol} 
                    className={`ship-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleShipClick(ship)}
                  >
                    <div className="ship-header">
                      <h4>{ship.registration?.name || ship.symbol}</h4>
                      <span className={`status ${getShipStatusColor(ship.nav?.status)}`}>
                        {ship.nav?.status || 'UNKNOWN'}
                      </span>
                    </div>
                    
                    <div className="ship-details">
                      <div className="detail-row">
                        <span className="label">Type:</span>
                        <span className="value">{ship.registration?.role || 'Unknown'}</span>
                      </div>
                      
                      <div className="detail-row">
                        <span className="label">Location:</span>
                        <span className="value">{ship.nav?.waypointSymbol || 'Unknown'}</span>
                      </div>
                      
                      <div className="detail-row">
                        <span className="label">Cargo:</span>
                        <span className="value">
                          {ship.cargo?.units || 0}/{ship.cargo?.capacity || 0}
                        </span>
                      </div>
                      
                      <div className="detail-row">
                        <span className="label">Equipment:</span>
                        <span className="value equipment">
                          ⚔️ {equipment.weapons} 🛡️ {equipment.shields}
                        </span>
                      </div>
                      
                      <div className="detail-row">
                        <span className="label">Crew:</span>
                        <span className="value">
                          {ship.crew?.current || 0}/{ship.crew?.capacity || 0}
                        </span>
                      </div>
                    </div>
                    
                    {isSelected && (
                      <div className="selected-indicator">
                        <span>✓ Selected for Actions</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          
          {selectedShip && (
            <div className="ship-details-panel">
              <h3>Ship Details: {selectedShip.registration?.name || selectedShip.symbol}</h3>
              
              <div className="details-grid">
                <div className="detail-section">
                  <h4>Navigation</h4>
                  <div className="detail-content">
                    <p><strong>Status:</strong> {selectedShip.nav?.status}</p>
                    <p><strong>Location:</strong> {selectedShip.nav?.waypointSymbol}</p>
                    <p><strong>System:</strong> {selectedShip.nav?.systemSymbol}</p>
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Equipment</h4>
                  <div className="detail-content">
                    <p><strong>Frame:</strong> {selectedShip.frame?.name}</p>
                    <p><strong>Engine:</strong> {selectedShip.engine?.name}</p>
                    <p><strong>Reactor:</strong> {selectedShip.reactor?.name}</p>
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Combat Equipment</h4>
                  <div className="detail-content">
                    {selectedShip.mounts?.filter(mount => 
                      mount.symbol && (
                        mount.symbol.includes('LASER_CANNON') ||
                        mount.symbol.includes('MISSILE_LAUNCHER') ||
                        mount.symbol.includes('TURRET')
                      )
                    ).map((weapon, index) => (
                      <p key={index}><strong>Weapon:</strong> {weapon.name || weapon.symbol}</p>
                    ))}
                    
                    {selectedShip.modules?.filter(module => 
                      module.symbol && module.symbol.includes('SHIELD_GENERATOR')
                    ).map((shield, index) => (
                      <p key={index}><strong>Shield:</strong> {shield.name || shield.symbol}</p>
                    ))}
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Cargo</h4>
                  <div className="detail-content">
                    <p><strong>Capacity:</strong> {selectedShip.cargo?.units}/{selectedShip.cargo?.capacity}</p>
                    <p><strong>Contents:</strong> {formatCargo(selectedShip.cargo)}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {selectedShip && (
        <div className="card">
          <div className="card-header">
            <h3>🗺️ System Map</h3>
            <p className="text-muted">Current system: {selectedShip.nav?.systemSymbol}</p>
          </div>
          <Map selectedShip={selectedShip} onShipUpdate={handleShipUpdate} />
        </div>
      )}
    </div>
  );
};

export default Fleet;
