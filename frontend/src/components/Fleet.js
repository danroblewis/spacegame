import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Map from './Map';

const Fleet = () => {
  const [ships, setShips] = useState([]);
  const [selectedShip, setSelectedShip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('ships');
  
  // Fleet Management State
  const [fleetGroups, setFleetGroups] = useState([]);
  const [formations, setFormations] = useState([]);
  const [supplyRoutes, setSupplyRoutes] = useState([]);
  const [fleetOperations, setFleetOperations] = useState([]);
  const [fleetStatus, setFleetStatus] = useState({});
  const [selectedShips, setSelectedShips] = useState([]);
  
  // Combat State
  const [combatTargets, setCombatTargets] = useState([]);
  const [combatFormations, setCombatFormations] = useState([]);

  // Modal states
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [showFormationModal, setShowFormationModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [showCommandModal, setShowCommandModal] = useState(false);

  useEffect(() => {
    fetchAllFleetData();
  }, []);

  const fetchAllFleetData = async () => {
    try {
      setLoading(true);
      
      const [shipsRes, groupsRes, formationsRes, routesRes, operationsRes, statusRes, targetsRes, combatFormationsRes] = await Promise.all([
        axios.get('/api/ships'),
        axios.get('/api/fleet/groups'),
        axios.get('/api/fleet/formations'),
        axios.get('/api/fleet/supply-routes'),
        axios.get('/api/fleet/operations'),
        axios.get('/api/fleet/status'),
        axios.get('/api/fleet/combat/targets'),
        axios.get('/api/fleet/combat/formations')
      ]);

      setShips(shipsRes.data);
      setFleetGroups(groupsRes.data);
      setFormations(formationsRes.data);
      setSupplyRoutes(routesRes.data);
      setFleetOperations(operationsRes.data);
      setFleetStatus(statusRes.data);
      setCombatTargets(targetsRes.data);
      setCombatFormations(combatFormationsRes.data);
      
      // Auto-select first ship if none selected
      if (shipsRes.data.length > 0 && !selectedShip) {
        setSelectedShip(shipsRes.data[0]);
      }
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch fleet data');
    } finally {
      setLoading(false);
    }
  };

  const handleShipSelect = (ship) => {
    setSelectedShip(ship);
  };

  const handleShipUpdate = (updatedShip) => {
    setShips(prevShips => 
      prevShips.map(ship => 
        ship.symbol === updatedShip.symbol ? updatedShip : ship
      )
    );
    if (selectedShip && selectedShip.symbol === updatedShip.symbol) {
      setSelectedShip(updatedShip);
    }
  };

  const toggleShipSelection = (shipSymbol) => {
    setSelectedShips(prev => 
      prev.includes(shipSymbol) 
        ? prev.filter(s => s !== shipSymbol)
        : [...prev, shipSymbol]
    );
  };

  const executeFleetCommand = async (commandType, parameters = {}, groupShips = []) => {
    try {
      const response = await axios.post('/api/fleet/commands', {
        command_type: commandType,
        target_ships: groupShips.length > 0 ? groupShips : selectedShips,
        parameters: parameters,
        priority: 1
      });
      
      alert('Fleet command executed successfully!');
      await fetchAllFleetData(); // Refresh data
      setSelectedShips([]); // Clear selection
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to execute fleet command');
    }
  };

  const activateFormation = async (formationName) => {
    try {
      await axios.post(`/api/fleet/formations/${formationName}/activate`);
      alert(`Formation ${formationName} activated!`);
      await fetchAllFleetData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to activate formation');
    }
  };

  const deactivateFormation = async (formationName) => {
    try {
      await axios.post(`/api/fleet/formations/${formationName}/deactivate`);
      alert(`Formation ${formationName} deactivated!`);
      await fetchAllFleetData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to deactivate formation');
    }
  };

  const handleResourceTransfer = async (transferData) => {
    try {
      const response = await axios.post('/api/fleet/transfer', transferData);
      alert(response.data.message);
      await fetchAllFleetData(); // Refresh ship data
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to transfer resources');
    }
  };

  const initiateCombat = async (targetId, tactics = 'alpha_strike') => {
    try {
      const response = await axios.post('/api/fleet/combat/attack', {
        ships: selectedShips,
        target_id: targetId,
        tactics: tactics
      });
      
      alert(`Combat result: ${response.data.result}!`);
      await fetchAllFleetData();
      setSelectedShips([]);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to initiate combat');
    }
  };

  const coordinateAttack = async (targetId, roles, formation = 'line') => {
    try {
      const response = await axios.post('/api/fleet/combat/coordinate', {
        ships: selectedShips,
        target_id: targetId,
        roles: roles,
        formation: formation
      });
      
      alert('Coordinated attack executed successfully!');
      await fetchAllFleetData();
      setSelectedShips([]);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to coordinate attack');
    }
  };

  const getShipStatusColor = (status) => {
    switch (status) {
      case 'IN_TRANSIT':
        return 'active';
      case 'IN_ORBIT':
        return 'active';
      case 'IN_FORMATION':
        return 'formation';
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

  const getShipsByRole = (role) => {
    return ships.filter(ship => ship.registration?.role === role);
  };

  if (loading) {
    return <div className="loading">Loading fleet data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  const renderShipsTab = () => (
    <div className="fleet-ships">
      <div className="fleet-header">
        <h2>Ships ({ships.length})</h2>
        <div className="fleet-actions">
          <button onClick={() => setShowCommandModal(true)} disabled={selectedShips.length === 0}>
            Fleet Commands ({selectedShips.length} selected)
          </button>
          <button onClick={() => setShowTransferModal(true)} disabled={selectedShips.length !== 2}>
            Transfer Resources
          </button>
        </div>
      </div>
      
      <div className="grid">
        {ships.map((ship) => (
          <div 
            key={ship.symbol} 
            className={`ship-card ${selectedShip?.symbol === ship.symbol ? 'selected' : ''} 
                       ${selectedShips.includes(ship.symbol) ? 'multi-selected' : ''}`}
            onClick={() => handleShipSelect(ship)}
          >
            <div className="ship-header">
              <input 
                type="checkbox" 
                checked={selectedShips.includes(ship.symbol)}
                onChange={() => toggleShipSelection(ship.symbol)}
                onClick={(e) => e.stopPropagation()}
              />
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
          </div>
        ))}
      </div>
    </div>
  );

  const renderGroupsTab = () => (
    <div className="fleet-groups">
      <div className="fleet-header">
        <h2>Fleet Groups</h2>
        <button onClick={() => setShowGroupModal(true)}>Create Group</button>
      </div>
      
      <div className="groups-grid">
        {fleetGroups.map((group) => (
          <div key={group.name} className="group-card">
            <h3>{group.name}</h3>
            <p>Role: {group.role || 'General'}</p>
            <p>Ships: {group.ships.length}</p>
            <p>Formation: {group.formation || 'None'}</p>
            <div className="group-ships">
              {group.ships.map(shipSymbol => (
                <span key={shipSymbol} className="ship-tag">{shipSymbol}</span>
              ))}
            </div>
            <div className="group-actions">
              <button onClick={() => executeFleetCommand('dock', {}, group.ships)}>
                Dock All
              </button>
              <button onClick={() => executeFleetCommand('orbit', {}, group.ships)}>
                Orbit All
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderFormationsTab = () => (
    <div className="fleet-formations">
      <div className="fleet-header">
        <h2>Formations</h2>
        <button onClick={() => setShowFormationModal(true)}>Create Formation</button>
      </div>
      
      <div className="formations-grid">
        {formations.map((formation) => (
          <div key={formation.name} className={`formation-card ${formation.active ? 'active' : ''}`}>
            <h3>{formation.name}</h3>
            <p>Type: {formation.type}</p>
            <p>Leader: {formation.leader_ship}</p>
            <p>Members: {formation.member_ships.length}</p>
            
            <div className="formation-ships">
              {[formation.leader_ship, ...formation.member_ships].map(shipSymbol => (
                <span key={shipSymbol} className="ship-tag">{shipSymbol}</span>
              ))}
            </div>
            
            <div className="formation-actions">
              {formation.active ? (
                <button onClick={() => deactivateFormation(formation.name)} className="deactivate">
                  Deactivate
                </button>
              ) : (
                <button onClick={() => activateFormation(formation.name)} className="activate">
                  Activate
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderOperationsTab = () => (
    <div className="fleet-operations">
      <div className="fleet-header">
        <h2>Fleet Operations & Logistics Dashboard</h2>
        <div className="fleet-actions">
          <button onClick={() => alert('Create new operation coming soon!')}>
            New Operation
          </button>
          <button onClick={() => alert('Automation center coming soon!')}>
            Automation Center
          </button>
        </div>
      </div>

      {/* Operations Overview */}
      <div className="operations-overview">
        <div className="overview-stats">
          <div className="stat-card">
            <div className="stat-icon">⚡</div>
            <div className="stat-info">
              <div className="stat-value">{fleetOperations.filter(op => op.status === 'active').length}</div>
              <div className="stat-label">Active Operations</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div className="stat-info">
              <div className="stat-value">{fleetOperations.filter(op => op.status === 'completed').length}</div>
              <div className="stat-label">Completed Today</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">🚀</div>
            <div className="stat-info">
              <div className="stat-value">{ships.filter(ship => ship.nav?.status === 'IN_TRANSIT').length}</div>
              <div className="stat-label">Ships in Transit</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">⚙️</div>
            <div className="stat-info">
              <div className="stat-value">{supplyRoutes.filter(r => r.active).length}</div>
              <div className="stat-label">Active Routes</div>
            </div>
          </div>
        </div>
      </div>

      {/* Task Queue */}
      <div className="task-queue">
        <h3>Fleet Task Queue</h3>
        <div className="task-list">
          <div className="task-item priority-high">
            <div className="task-icon">🚨</div>
            <div className="task-content">
              <div className="task-title">Combat Response Required</div>
              <div className="task-description">Pirate activity detected at X1-DF55-20250Z</div>
            </div>
            <div className="task-actions">
              <button className="task-btn primary">Respond</button>
              <button className="task-btn">Postpone</button>
            </div>
          </div>
          
          <div className="task-item priority-medium">
            <div className="task-icon">⛽</div>
            <div className="task-content">
              <div className="task-title">Fuel Resupply Needed</div>
              <div className="task-description">DEMO_SHIP_2 fuel level below 30%</div>
            </div>
            <div className="task-actions">
              <button className="task-btn primary">Refuel</button>
              <button className="task-btn">Schedule</button>
            </div>
          </div>
          
          <div className="task-item priority-low">
            <div className="task-icon">🔧</div>
            <div className="task-content">
              <div className="task-title">Routine Maintenance</div>
              <div className="task-description">DEMO_SHIP_1 due for scheduled maintenance</div>
            </div>
            <div className="task-actions">
              <button className="task-btn primary">Schedule</button>
              <button className="task-btn">Skip</button>
            </div>
          </div>
        </div>
      </div>

      {/* Active Operations */}
      <div className="operations-section">
        <h3>Active Operations</h3>
        <div className="operations-grid">
          {fleetOperations.map((operation) => (
            <div key={operation.operation_id} className={`operation-card ${operation.status}`}>
              <div className="operation-header">
                <h4>{operation.operation_type} Operation</h4>
                <span className={`status-badge ${operation.status}`}>
                  {operation.status}
                </span>
              </div>
              
              <div className="operation-details">
                <p><strong>ID:</strong> {operation.operation_id}</p>
                <p><strong>Location:</strong> {operation.target_location}</p>
                <p><strong>Ships:</strong> {operation.assigned_ships.length}</p>
                {operation.estimated_completion && (
                  <p><strong>ETA:</strong> {new Date(operation.estimated_completion).toLocaleTimeString()}</p>
                )}
              </div>
              
              {operation.progress && (
                <div className="progress-section">
                  <h5>Progress:</h5>
                  <div className="progress-details">
                    {Object.entries(operation.progress).map(([key, value]) => (
                      <div key={key} className="progress-item">
                        <span className="progress-key">{key}:</span>
                        <span className="progress-value">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="operation-ships">
                {operation.assigned_ships.map(shipSymbol => (
                  <span key={shipSymbol} className="ship-tag">{shipSymbol}</span>
                ))}
              </div>

              <div className="operation-actions">
                {operation.status === 'active' && (
                  <>
                    <button className="op-btn pause">Pause</button>
                    <button className="op-btn cancel">Cancel</button>
                  </>
                )}
                <button className="op-btn details">Details</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fleet Automation Dashboard */}
      <div className="automation-dashboard">
        <h3>Fleet Automation Status</h3>
        <div className="automation-toggles">
          <div className="toggle-group">
            <div className="automation-toggle active">
              <div className="toggle-info">
                <div className="toggle-title">Auto-Mining</div>
                <div className="toggle-description">Automatically deploy mining operations</div>
              </div>
              <div className="toggle-switch">
                <input type="checkbox" checked />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="automation-toggle">
              <div className="toggle-info">
                <div className="toggle-title">Smart Routing</div>
                <div className="toggle-description">Optimize ship routes automatically</div>
              </div>
              <div className="toggle-switch">
                <input type="checkbox" />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="automation-toggle active">
              <div className="toggle-info">
                <div className="toggle-title">Supply Chain</div>
                <div className="toggle-description">Automated resource distribution</div>
              </div>
              <div className="toggle-switch">
                <input type="checkbox" checked />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="automation-toggle">
              <div className="toggle-info">
                <div className="toggle-title">Fleet Defense</div>
                <div className="toggle-description">Automatic threat response</div>
              </div>
              <div className="toggle-switch">
                <input type="checkbox" />
                <span className="slider"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const activateSupplyRoute = async (routeName) => {
    try {
      await axios.post(`/api/fleet/supply-routes/${routeName}/activate`);
      alert(`Supply route ${routeName} activated!`);
      await fetchAllFleetData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to activate supply route');
    }
  };

  const renderSupplyTab = () => (
    <div className="supply-routes">
      <div className="fleet-header">
        <h2>Supply Chain & Logistics</h2>
        <div className="fleet-actions">
          <button onClick={() => alert('Supply route creator coming soon!')}>
            Create Supply Route
          </button>
          <button onClick={() => alert('Automation dashboard coming soon!')}>
            Automation Settings
          </button>
        </div>
      </div>
      
      <div className="supply-overview">
        <div className="supply-stats">
          <div className="stat">
            <div className="stat-value">{supplyRoutes.length}</div>
            <div className="stat-label">Total Routes</div>
          </div>
          <div className="stat">
            <div className="stat-value">{supplyRoutes.filter(r => r.active).length}</div>
            <div className="stat-label">Active Routes</div>
          </div>
          <div className="stat">
            <div className="stat-value">{supplyRoutes.filter(r => r.schedule?.auto_start).length}</div>
            <div className="stat-label">Automated</div>
          </div>
        </div>
      </div>
      
      <div className="supply-grid">
        {supplyRoutes.map((route) => (
          <div key={route.name} className={`supply-card ${route.active ? 'active' : ''}`}>
            <div className="supply-header">
              <h3>{route.name}</h3>
              {route.schedule?.auto_start && (
                <span className="automation-badge">AUTOMATED</span>
              )}
            </div>
            
            <div className="route-details">
              <div className="route-path">
                <div className="waypoint source">
                  <span className="waypoint-label">From:</span>
                  <span className="waypoint-name">{route.source_waypoint}</span>
                </div>
                <div className="route-arrow">→</div>
                <div className="waypoint destination">
                  <span className="waypoint-label">To:</span>
                  <span className="waypoint-name">{route.destination_waypoint}</span>
                </div>
              </div>
              
              <div className="route-info">
                <p><strong>Resources:</strong> {route.resource_types.join(', ')}</p>
                <p><strong>Ships:</strong> {route.assigned_ships.length}</p>
                {route.schedule && (
                  <p><strong>Schedule:</strong> {route.schedule.frequency}</p>
                )}
              </div>
            </div>
            
            <div className="route-ships">
              {route.assigned_ships.map(shipSymbol => (
                <span key={shipSymbol} className="ship-tag">{shipSymbol}</span>
              ))}
            </div>
            
            <div className="route-progress">
              <div className="progress-bar">
                <div className="progress-fill" style={{width: '60%'}}></div>
              </div>
              <small>Route Progress: 60% complete</small>
            </div>
            
            <div className="route-actions">
              <button 
                className={route.active ? 'deactivate' : 'activate'}
                onClick={() => activateSupplyRoute(route.name)}
              >
                {route.active ? 'Deactivate' : 'Activate'}
              </button>
              <button onClick={() => alert('Route details coming soon!')}>
                Configure
              </button>
              {route.active && (
                <button onClick={() => alert('Manual run initiated!')}>
                  Run Now
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="logistics-automation">
        <h3>Fleet Logistics Automation</h3>
        <div className="automation-grid">
          <div className="automation-card">
            <h4>Auto-Mining Operations</h4>
            <p>Automatically deploy mining ships to resource-rich locations</p>
            <button>Enable Auto-Mining</button>
          </div>
          
          <div className="automation-card">
            <h4>Smart Cargo Distribution</h4>
            <p>Intelligently distribute resources based on demand</p>
            <button>Enable Smart Distribution</button>
          </div>
          
          <div className="automation-card">
            <h4>Fleet Maintenance</h4>
            <p>Automatically schedule maintenance and repairs</p>
            <button>Enable Auto-Maintenance</button>
          </div>
          
          <div className="automation-card">
            <h4>Trade Route Optimization</h4>
            <p>Optimize trade routes for maximum efficiency</p>
            <button>Enable Optimization</button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCombatTab = () => (
    <div className="fleet-combat">
      <div className="fleet-header">
        <h2>Combat Operations</h2>
        <div className="fleet-actions">
          <button onClick={() => alert('Combat formation creator coming soon!')} disabled={selectedShips.length === 0}>
            Create Combat Formation ({selectedShips.length} selected)
          </button>
        </div>
      </div>

      <div className="combat-sections">
        {/* Combat Targets */}
        <div className="combat-targets">
          <h3>Available Targets</h3>
          <div className="targets-grid">
            {combatTargets.map((target) => (
              <div key={target.target_id} className={`target-card threat-${target.threat_level}`}>
                <h4>{target.target_id}</h4>
                <p>Type: {target.target_type}</p>
                <p>Location: {target.location}</p>
                <p>Threat Level: {target.threat_level}/10</p>
                <p>Health: {target.estimated_health}</p>
                
                <div className="target-actions">
                  <button 
                    onClick={() => initiateCombat(target.target_id, 'alpha_strike')}
                    disabled={selectedShips.length === 0}
                  >
                    Alpha Strike
                  </button>
                  <button 
                    onClick={() => initiateCombat(target.target_id, 'surround')}
                    disabled={selectedShips.length < 2}
                  >
                    Surround
                  </button>
                  <button 
                    onClick={() => coordinateAttack(target.target_id, {}, 'pincer')}
                    disabled={selectedShips.length < 3}
                  >
                    Coordinated Attack
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Combat Formations */}
        <div className="combat-formations-section">
          <h3>Combat Formations</h3>
          <div className="combat-formations-grid">
            {combatFormations.map((formation) => (
              <div key={formation.formation_id} className={`combat-formation-card ${formation.status}`}>
                <h4>{formation.name}</h4>
                <p>Target: {formation.target}</p>
                <p>Tactics: {formation.tactics}</p>
                <p>Status: {formation.status}</p>
                <p>Ships: {formation.ships.length}</p>
                
                <div className="formation-roles">
                  <h5>Ship Roles:</h5>
                  {Object.entries(formation.roles).map(([ship, role]) => (
                    <div key={ship} className="role-assignment">
                      <span className="ship-tag">{ship}</span>
                      <span className="role-tag">{role}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fleet">
      <div className="card">
        <h1>Fleet Management</h1>
        <div className="fleet-stats">
          <div className="stat">
            <div className="stat-value">{fleetStatus.total_ships}</div>
            <div className="stat-label">Total Ships</div>
          </div>
          <div className="stat">
            <div className="stat-value">{fleetStatus.active_ships}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat">
            <div className="stat-value">{fleetStatus.active_operations}</div>
            <div className="stat-label">Operations</div>
          </div>
          <div className="stat">
            <div className="stat-value">{fleetStatus.active_formations}</div>
            <div className="stat-label">Formations</div>
          </div>
        </div>
        {selectedShip && (
          <p>Selected: <strong>{selectedShip.symbol}</strong> at {selectedShip.nav?.waypointSymbol}</p>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="fleet-tabs">
        {['ships', 'groups', 'formations', 'operations', 'supply', 'combat'].map(tab => (
          <button 
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Map Component */}
      {activeTab === 'ships' && (
        <Map selectedShip={selectedShip} onShipUpdate={handleShipUpdate} />
      )}

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'ships' && renderShipsTab()}
        {activeTab === 'groups' && renderGroupsTab()}
        {activeTab === 'formations' && renderFormationsTab()}
        {activeTab === 'operations' && renderOperationsTab()}
        {activeTab === 'supply' && renderSupplyTab()}
        {activeTab === 'combat' && renderCombatTab()}
      </div>

      {/* Modals would go here - simplified for now */}
      {showCommandModal && (
        <FleetCommandModal 
          selectedShips={selectedShips}
          onClose={() => setShowCommandModal(false)}
          onExecute={executeFleetCommand}
        />
      )}
      
      {showTransferModal && (
        <ResourceTransferModal 
          ships={ships}
          selectedShips={selectedShips}
          onClose={() => setShowTransferModal(false)}
          onTransfer={handleResourceTransfer}
        />
      )}
    </div>
  );
};

// Fleet Command Modal Component
const FleetCommandModal = ({ selectedShips, onClose, onExecute }) => {
  const [command, setCommand] = useState('dock');
  const [waypointSymbol, setWaypointSymbol] = useState('');

  const handleExecute = () => {
    const parameters = command === 'navigate' ? { waypointSymbol } : {};
    onExecute(command, parameters);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h3>Fleet Command</h3>
        <p>Executing command for {selectedShips.length} ships</p>
        
        <div className="form-group">
          <label>Command:</label>
          <select value={command} onChange={(e) => setCommand(e.target.value)}>
            <option value="dock">Dock</option>
            <option value="orbit">Orbit</option>
            <option value="navigate">Navigate</option>
            <option value="mine">Mine</option>
          </select>
        </div>

        {command === 'navigate' && (
          <div className="form-group">
            <label>Destination:</label>
            <input 
              type="text" 
              value={waypointSymbol} 
              onChange={(e) => setWaypointSymbol(e.target.value)}
              placeholder="X1-DF55-20250X"
            />
          </div>
        )}

        <div className="modal-actions">
          <button onClick={onClose}>Cancel</button>
          <button onClick={handleExecute}>Execute</button>
        </div>
      </div>
    </div>
  );
};

// Resource Transfer Modal Component
const ResourceTransferModal = ({ ships, selectedShips, onClose, onTransfer }) => {
  const [fromShip, setFromShip] = useState(selectedShips[0] || '');
  const [toShip, setToShip] = useState(selectedShips[1] || '');
  const [resourceSymbol, setResourceSymbol] = useState('');
  const [quantity, setQuantity] = useState(1);

  const getShipCargo = (shipSymbol) => {
    const ship = ships.find(s => s.symbol === shipSymbol);
    return ship?.cargo?.inventory || [];
  };

  const getAvailableQuantity = () => {
    const cargo = getShipCargo(fromShip);
    const item = cargo.find(item => item.symbol === resourceSymbol);
    return item?.units || 0;
  };

  const handleTransfer = () => {
    if (!fromShip || !toShip || !resourceSymbol || quantity <= 0) {
      alert('Please fill in all fields');
      return;
    }
    
    onTransfer({
      from_ship: fromShip,
      to_ship: toShip,
      resource_symbol: resourceSymbol,
      quantity: quantity
    });
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h3>Transfer Resources</h3>
        
        <div className="form-group">
          <label>From Ship:</label>
          <select value={fromShip} onChange={(e) => setFromShip(e.target.value)}>
            <option value="">Select ship...</option>
            {ships.map(ship => (
              <option key={ship.symbol} value={ship.symbol}>
                {ship.symbol} - {ship.registration?.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>To Ship:</label>
          <select value={toShip} onChange={(e) => setToShip(e.target.value)}>
            <option value="">Select ship...</option>
            {ships.filter(ship => ship.symbol !== fromShip).map(ship => (
              <option key={ship.symbol} value={ship.symbol}>
                {ship.symbol} - {ship.registration?.name}
              </option>
            ))}
          </select>
        </div>

        {fromShip && (
          <div className="form-group">
            <label>Resource:</label>
            <select value={resourceSymbol} onChange={(e) => setResourceSymbol(e.target.value)}>
              <option value="">Select resource...</option>
              {getShipCargo(fromShip).map(item => (
                <option key={item.symbol} value={item.symbol}>
                  {item.symbol} ({item.units} available)
                </option>
              ))}
            </select>
          </div>
        )}

        {resourceSymbol && (
          <div className="form-group">
            <label>Quantity:</label>
            <input 
              type="number" 
              value={quantity} 
              onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
              min="1"
              max={getAvailableQuantity()}
            />
            <small>Available: {getAvailableQuantity()}</small>
          </div>
        )}

        <div className="modal-actions">
          <button onClick={onClose}>Cancel</button>
          <button onClick={handleTransfer}>Transfer</button>
        </div>
      </div>
    </div>
  );
};

export default Fleet;
