import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Map from './Map';
import ShipModifications from './ShipModifications';
import ShipActionsSidebar from './ShipActionsSidebar';

const Fleet = ({ selectedShip, onShipSelect, onShipUpdate }) => {
  const [ships, setShips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModifications, setShowModifications] = useState(false);
  const [message, setMessage] = useState(null);

  // Auto-hide messages after 5 seconds
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        setMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const fetchShips = useCallback(async () => {
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
  }, [selectedShip, onShipSelect]);

  useEffect(() => {
    fetchShips();
  }, [fetchShips]);

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

  const handleMessage = (messageText, type = 'info') => {
    setMessage({ text: messageText, type });
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
        <h1>Fleet Management</h1>
        <p>Total Ships: {ships.length}</p>
        {selectedShip && (
          <p>Selected: <strong>{selectedShip.symbol}</strong> at {selectedShip.nav?.waypointSymbol}</p>
        )}
      </div>

      <div className="fleet-layout">
        {/* Main Fleet Content */}
        <div className="fleet-main">
          {/* Map Component */}
          <Map selectedShip={selectedShip} onShipUpdate={handleShipUpdate} />

          {ships.length === 0 ? (
            <div className="card">
              <p>No ships found. You may need to purchase your first ship!</p>
            </div>
          ) : (
            <div className="fleet-ships">
              <h2>Ships</h2>
              <div className="grid">
                {ships.map((ship) => (
                  <div 
                    key={ship.symbol} 
                    className={`ship-card ${selectedShip?.symbol === ship.symbol ? 'selected' : ''}`}
                    onClick={() => handleShipClick(ship)}
                  >
                <div className="ship-header">
                  <span className="ship-name">{ship.symbol}</span>
                  <span className={`ship-status ${getShipStatusColor(ship.nav?.status)}`}>
                    {ship.nav?.status || 'UNKNOWN'}
                  </span>
                </div>

                <div className="ship-details">
                  <div className="detail-item">
                    <div className="detail-value">{ship.registration?.name || 'N/A'}</div>
                    <div className="detail-label">Ship Name</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-value">{ship.registration?.role || 'N/A'}</div>
                    <div className="detail-label">Role</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-value">{ship.nav?.waypointSymbol || 'N/A'}</div>
                    <div className="detail-label">Location</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-value">{ship.crew?.current || 0}/{ship.crew?.capacity || 0}</div>
                    <div className="detail-label">Crew</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-value">{ship.cargo?.units || 0}/{ship.cargo?.capacity || 0}</div>
                    <div className="detail-label">Cargo</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-value">{ship.frame?.name || 'N/A'}</div>
                    <div className="detail-label">Frame</div>
                  </div>
                </div>

                {ship.cargo && ship.cargo.inventory && ship.cargo.inventory.length > 0 && (
                  <div className="cargo-section">
                    <h4>Cargo Contents:</h4>
                    <div className="cargo-grid">
                      {ship.cargo.inventory.map((item, index) => (
                        <div key={index} className="cargo-item">
                          <span className="cargo-symbol">{item.symbol}</span>
                          <span className="cargo-units">{item.units}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {ship.modules && ship.modules.length > 0 && (
                  <div className="modules-section">
                    <h4>Modules:</h4>
                    <div className="modules-grid">
                      {ship.modules.map((module, index) => (
                        <div key={index} className="module-item">
                          {module.name || module.symbol}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {ship.mounts && ship.mounts.length > 0 && (
                  <div className="mounts-section">
                    <h4>Mounts:</h4>
                    <div className="mounts-grid">
                      {ship.mounts.map((mount, index) => (
                        <div key={index} className="mount-item">
                          {mount.name || mount.symbol}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="ship-actions">
                  <button 
                    className="modify-ship-btn"
                    onClick={() => {
                      onShipSelect(ship);
                      setShowModifications(true);
                    }}
                  >
                    🔧 Modify Ship
                  </button>
                </div>
              </div>
            ))}
          </div>
            </div>
          )}
        </div>

        {/* Ship Actions Sidebar */}
        <ShipActionsSidebar 
          selectedShip={selectedShip}
          onShipUpdate={handleShipUpdate}
        />
      </div>

      {message && (
        <div className={`message message-${message.type}`}>
          {message.text}
          <button 
            className="message-close" 
            onClick={() => setMessage(null)}
            aria-label="Close message"
          >
            ×
          </button>
        </div>
      )}
      
      <div className="fleet-layout">
        <div className="fleet-main">
          <div className="card">
            <h1>Fleet Management</h1>
            <p>Total Ships: {ships.length}</p>
            {selectedShip && (
              <p>Selected: <strong>{selectedShip.symbol}</strong> at {selectedShip.nav?.waypointSymbol}</p>
            )}
          </div>

          {/* Map Component */}
          <Map selectedShip={selectedShip} onShipUpdate={handleShipUpdate} />

          {ships.length === 0 ? (
            <div className="card">
              <p>No ships found. You may need to purchase your first ship!</p>
            </div>
          ) : (
            <div className="fleet-ships">
              <h2>Ships</h2>
              <div className="grid">
                {ships.map((ship) => (
                  <div 
                    key={ship.symbol} 
                    className={`ship-card ${selectedShip?.symbol === ship.symbol ? 'selected' : ''}`}
                    onClick={() => handleShipClick(ship)}
                  >
                    <div className="ship-header">
                      <span className="ship-name">{ship.symbol}</span>
                      <span className={`ship-status ${getShipStatusColor(ship.nav?.status)}`}>
                        {ship.nav?.status || 'UNKNOWN'}
                      </span>
                    </div>

                    <div className="ship-details">
                      <div className="detail-item">
                        <div className="detail-value">{ship.registration?.name || 'N/A'}</div>
                        <div className="detail-label">Ship Name</div>
                      </div>
                      <div className="detail-item">
                        <div className="detail-value">{ship.registration?.role || 'N/A'}</div>
                        <div className="detail-label">Role</div>
                      </div>
                      <div className="detail-item">
                        <div className="detail-value">{ship.nav?.waypointSymbol || 'N/A'}</div>
                        <div className="detail-label">Location</div>
                      </div>
                      <div className="detail-item">
                        <div className="detail-value">{ship.crew?.current || 0}/{ship.crew?.capacity || 0}</div>
                        <div className="detail-label">Crew</div>
                      </div>
                      <div className="detail-item">
                        <div className="detail-value">{ship.cargo?.units || 0}/{ship.cargo?.capacity || 0}</div>
                        <div className="detail-label">Cargo</div>
                      </div>
                      <div className="detail-item">
                        <div className="detail-value">{ship.frame?.name || 'N/A'}</div>
                        <div className="detail-label">Frame</div>
                      </div>
                    </div>

                    {ship.cargo && ship.cargo.inventory && ship.cargo.inventory.length > 0 && (
                      <div className="cargo-section">
                        <h4>Cargo Contents:</h4>
                        <div className="cargo-grid">
                          {ship.cargo.inventory.map((item, index) => (
                            <div key={index} className="cargo-item">
                              <span className="cargo-symbol">{item.symbol}</span>
                              <span className="cargo-units">{item.units}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {ship.modules && ship.modules.length > 0 && (
                      <div className="modules-section">
                        <h4>Modules:</h4>
                        <div className="modules-grid">
                          {ship.modules.map((module, index) => (
                            <div key={index} className="module-item">
                              {module.name || module.symbol}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {ship.mounts && ship.mounts.length > 0 && (
                      <div className="mounts-section">
                        <h4>Mounts:</h4>
                        <div className="mounts-grid">
                          {ship.mounts.map((mount, index) => (
                            <div key={index} className="mount-item">
                              {mount.name || mount.symbol}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Ship Modifications Modal */}
      {showModifications && selectedShip && (
        <div className="modal-overlay">
          <ShipModifications 
            selectedShip={selectedShip}
            onShipUpdate={handleShipUpdate}
            onClose={() => setShowModifications(false)}
          />
        </div>
      )}
    </div>
  );
};

export default Fleet;
