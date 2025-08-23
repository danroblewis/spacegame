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
      
      // Auto-select first ship if none selected and ships are available
      if (response.data.length > 0 && !selectedShip && onShipSelect) {
        onShipSelect(response.data[0]);
      }
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch ships');
    } finally {
      setLoading(false);
    }
  };

  const handleShipSelect = (ship) => {
    if (onShipSelect) {
      onShipSelect(ship);
    }
  };

  const handleShipUpdate = (updatedShip) => {
    // Update the ship in the ships array
    setShips(prevShips => 
      prevShips.map(ship => 
        ship.symbol === updatedShip.symbol ? updatedShip : ship
      )
    );
    // Update selected ship if it's the one that was updated
    if (onShipUpdate) {
      onShipUpdate(updatedShip);
    }
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
                onClick={() => handleShipSelect(ship)}
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
  );
};

export default Fleet;
