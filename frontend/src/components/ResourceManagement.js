import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ResourceManagement.css';

const ResourceManagement = () => {
  const [ships, setShips] = useState([]);
  const [selectedShip, setSelectedShip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [resourceData, setResourceData] = useState({});
  const [activeTab, setActiveTab] = useState('fuel');

  // Resource management actions state
  const [fuelOptimization, setFuelOptimization] = useState(false);
  const [powerBalance, setPowerBalance] = useState('normal');
  const [heatSinkActive, setHeatSinkActive] = useState(false);
  const [lifeSupportLevel, setLifeSupportLevel] = useState('standard');
  const [recyclingActive, setRecyclingActive] = useState(false);
  const [emergencyMode, setEmergencyMode] = useState(false);

  useEffect(() => {
    fetchShips();
  }, []);

  useEffect(() => {
    if (selectedShip) {
      fetchResourceData(selectedShip.symbol);
    }
  }, [selectedShip]);

  const fetchShips = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/ships');
      setShips(response.data);
      
      if (response.data.length > 0 && !selectedShip) {
        setSelectedShip(response.data[0]);
      }
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch ships');
    } finally {
      setLoading(false);
    }
  };

  const fetchResourceData = async (shipSymbol) => {
    try {
      const response = await axios.get(`/api/ships/${shipSymbol}/resources`);
      setResourceData(response.data);
    } catch (err) {
      // If endpoint doesn't exist yet, use mock data
      setResourceData({
        fuel: { current: 85, capacity: 100, efficiency: 92, consumption_rate: 1.2 },
        power: { current: 78, capacity: 100, distribution: { engines: 35, life_support: 25, systems: 18 } },
        heat: { current: 45, max_safe: 80, dissipation_rate: 2.1, thermal_vents: 4 },
        life_support: { oxygen: 98, temperature: 22, humidity: 45, crew_comfort: 85 },
        waste: { organic: 12, recyclable: 8, hazardous: 3, recycling_efficiency: 75 },
        emergency: { medical: 95, rations: 87, oxygen_backup: 100, repair_kits: 3 }
      });
    }
  };

  const handleResourceAction = async (action, parameters) => {
    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/resources/${action}`, parameters);
      // Update local state or refetch data
      await fetchResourceData(selectedShip.symbol);
      return response.data;
    } catch (err) {
      console.error(`Failed to execute ${action}:`, err);
      // For demo purposes, simulate the action locally
      simulateResourceAction(action, parameters);
    }
  };

  const simulateResourceAction = (action, parameters) => {
    // Simulate resource changes for demo
    setResourceData(prev => {
      const newData = { ...prev };
      
      switch (action) {
        case 'optimize-fuel':
          newData.fuel.efficiency = Math.min(100, newData.fuel.efficiency + 5);
          break;
        case 'balance-power':
          newData.power.current = Math.max(50, Math.min(100, newData.power.current + (Math.random() - 0.5) * 10));
          break;
        case 'activate-heat-sink':
          newData.heat.current = Math.max(20, newData.heat.current - 10);
          break;
        case 'adjust-life-support':
          newData.life_support.crew_comfort = Math.min(100, newData.life_support.crew_comfort + 5);
          break;
        case 'start-recycling':
          newData.waste.recyclable = Math.max(0, newData.waste.recyclable - 3);
          break;
        case 'deploy-emergency':
          newData.emergency.repair_kits = Math.max(0, newData.emergency.repair_kits - 1);
          break;
      }
      
      return newData;
    });
  };

  const getStatusColor = (value, threshold = 70) => {
    if (value >= threshold) return '#4CAF50'; // Green
    if (value >= threshold * 0.7) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const renderFuelManagement = () => (
    <div className="resource-section">
      <h3>⛽ Fuel Efficiency</h3>
      <div className="resource-grid">
        <div className="resource-item">
          <div className="resource-header">
            <span>Fuel Level</span>
            <span style={{ color: getStatusColor(resourceData.fuel?.current || 0) }}>
              {resourceData.fuel?.current || 0}%
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${resourceData.fuel?.current || 0}%`,
                backgroundColor: getStatusColor(resourceData.fuel?.current || 0)
              }}
            />
          </div>
        </div>
        
        <div className="resource-item">
          <div className="resource-header">
            <span>Efficiency</span>
            <span>{resourceData.fuel?.efficiency || 0}%</span>
          </div>
          <div className="resource-stats">
            <p>Consumption Rate: {resourceData.fuel?.consumption_rate || 0} units/hour</p>
          </div>
        </div>
      </div>
      
      <div className="resource-controls">
        <button 
          className={`resource-btn ${fuelOptimization ? 'active' : ''}`}
          onClick={() => {
            setFuelOptimization(!fuelOptimization);
            handleResourceAction('optimize-fuel', { enable: !fuelOptimization });
          }}
        >
          {fuelOptimization ? 'Optimization Active' : 'Enable Optimization'}
        </button>
        <button 
          className="resource-btn secondary"
          onClick={() => handleResourceAction('refuel', {})}
        >
          Refuel Ship
        </button>
      </div>
    </div>
  );

  const renderPowerManagement = () => (
    <div className="resource-section">
      <h3>⚡ Power Management</h3>
      <div className="resource-grid">
        <div className="resource-item">
          <div className="resource-header">
            <span>Total Power</span>
            <span style={{ color: getStatusColor(resourceData.power?.current || 0) }}>
              {resourceData.power?.current || 0}%
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${resourceData.power?.current || 0}%`,
                backgroundColor: getStatusColor(resourceData.power?.current || 0)
              }}
            />
          </div>
        </div>
        
        <div className="resource-item">
          <div className="resource-header">
            <span>Power Distribution</span>
          </div>
          <div className="power-distribution">
            <div className="power-bar">
              <span>Engines</span>
              <div className="mini-progress">
                <div style={{ width: `${resourceData.power?.distribution?.engines || 0}%` }} />
              </div>
              <span>{resourceData.power?.distribution?.engines || 0}%</span>
            </div>
            <div className="power-bar">
              <span>Life Support</span>
              <div className="mini-progress">
                <div style={{ width: `${resourceData.power?.distribution?.life_support || 0}%` }} />
              </div>
              <span>{resourceData.power?.distribution?.life_support || 0}%</span>
            </div>
            <div className="power-bar">
              <span>Systems</span>
              <div className="mini-progress">
                <div style={{ width: `${resourceData.power?.distribution?.systems || 0}%` }} />
              </div>
              <span>{resourceData.power?.distribution?.systems || 0}%</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="resource-controls">
        <select 
          value={powerBalance} 
          onChange={(e) => {
            setPowerBalance(e.target.value);
            handleResourceAction('balance-power', { mode: e.target.value });
          }}
          className="resource-select"
        >
          <option value="efficiency">Efficiency Mode</option>
          <option value="normal">Normal Mode</option>
          <option value="performance">Performance Mode</option>
          <option value="emergency">Emergency Mode</option>
        </select>
      </div>
    </div>
  );

  const renderHeatDissipation = () => (
    <div className="resource-section">
      <h3>🌡️ Heat Dissipation</h3>
      <div className="resource-grid">
        <div className="resource-item">
          <div className="resource-header">
            <span>Heat Level</span>
            <span style={{ color: getStatusColor(100 - (resourceData.heat?.current || 0), 50) }}>
              {resourceData.heat?.current || 0}°C
            </span>
          </div>
          <div className="progress-bar heat-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${(resourceData.heat?.current || 0) / (resourceData.heat?.max_safe || 100) * 100}%`,
                backgroundColor: (resourceData.heat?.current || 0) > (resourceData.heat?.max_safe || 80) ? '#F44336' : '#4CAF50'
              }}
            />
          </div>
          <span className="heat-warning">Max Safe: {resourceData.heat?.max_safe || 80}°C</span>
        </div>
        
        <div className="resource-item">
          <div className="resource-header">
            <span>Thermal Systems</span>
          </div>
          <div className="resource-stats">
            <p>Dissipation Rate: {resourceData.heat?.dissipation_rate || 0} °C/min</p>
            <p>Active Vents: {resourceData.heat?.thermal_vents || 0}</p>
          </div>
        </div>
      </div>
      
      <div className="resource-controls">
        <button 
          className={`resource-btn ${heatSinkActive ? 'active' : ''}`}
          onClick={() => {
            setHeatSinkActive(!heatSinkActive);
            handleResourceAction('activate-heat-sink', { enable: !heatSinkActive });
          }}
        >
          {heatSinkActive ? 'Heat Sinks Active' : 'Activate Heat Sinks'}
        </button>
        <button 
          className="resource-btn secondary"
          onClick={() => handleResourceAction('emergency-cooling', {})}
        >
          Emergency Cooling
        </button>
      </div>
    </div>
  );

  const renderLifeSupport = () => (
    <div className="resource-section">
      <h3>🫁 Life Support</h3>
      <div className="resource-grid">
        <div className="resource-item">
          <div className="resource-header">
            <span>Oxygen Level</span>
            <span style={{ color: getStatusColor(resourceData.life_support?.oxygen || 0) }}>
              {resourceData.life_support?.oxygen || 0}%
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${resourceData.life_support?.oxygen || 0}%`,
                backgroundColor: getStatusColor(resourceData.life_support?.oxygen || 0)
              }}
            />
          </div>
        </div>
        
        <div className="resource-item">
          <div className="resource-header">
            <span>Environment Status</span>
          </div>
          <div className="environment-stats">
            <div className="env-stat">
              <span>Temperature</span>
              <span>{resourceData.life_support?.temperature || 0}°C</span>
            </div>
            <div className="env-stat">
              <span>Humidity</span>
              <span>{resourceData.life_support?.humidity || 0}%</span>
            </div>
            <div className="env-stat">
              <span>Crew Comfort</span>
              <span style={{ color: getStatusColor(resourceData.life_support?.crew_comfort || 0) }}>
                {resourceData.life_support?.crew_comfort || 0}%
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="resource-controls">
        <select 
          value={lifeSupportLevel} 
          onChange={(e) => {
            setLifeSupportLevel(e.target.value);
            handleResourceAction('adjust-life-support', { level: e.target.value });
          }}
          className="resource-select"
        >
          <option value="minimal">Minimal</option>
          <option value="standard">Standard</option>
          <option value="optimal">Optimal</option>
          <option value="luxury">Luxury</option>
        </select>
      </div>
    </div>
  );

  const renderWasteRecycling = () => (
    <div className="resource-section">
      <h3>♻️ Waste Recycling</h3>
      <div className="resource-grid">
        <div className="resource-item">
          <div className="resource-header">
            <span>Waste Levels</span>
          </div>
          <div className="waste-breakdown">
            <div className="waste-type">
              <span>Organic</span>
              <div className="mini-progress">
                <div style={{ width: `${(resourceData.waste?.organic || 0) * 5}%`, backgroundColor: '#4CAF50' }} />
              </div>
              <span>{resourceData.waste?.organic || 0} units</span>
            </div>
            <div className="waste-type">
              <span>Recyclable</span>
              <div className="mini-progress">
                <div style={{ width: `${(resourceData.waste?.recyclable || 0) * 8}%`, backgroundColor: '#2196F3' }} />
              </div>
              <span>{resourceData.waste?.recyclable || 0} units</span>
            </div>
            <div className="waste-type">
              <span>Hazardous</span>
              <div className="mini-progress">
                <div style={{ width: `${(resourceData.waste?.hazardous || 0) * 15}%`, backgroundColor: '#F44336' }} />
              </div>
              <span>{resourceData.waste?.hazardous || 0} units</span>
            </div>
          </div>
        </div>
        
        <div className="resource-item">
          <div className="resource-header">
            <span>Recycling Efficiency</span>
            <span>{resourceData.waste?.recycling_efficiency || 0}%</span>
          </div>
        </div>
      </div>
      
      <div className="resource-controls">
        <button 
          className={`resource-btn ${recyclingActive ? 'active' : ''}`}
          onClick={() => {
            setRecyclingActive(!recyclingActive);
            handleResourceAction('start-recycling', { enable: !recyclingActive });
          }}
        >
          {recyclingActive ? 'Recycling Active' : 'Start Recycling'}
        </button>
        <button 
          className="resource-btn secondary"
          onClick={() => handleResourceAction('jettison-waste', {})}
        >
          Jettison Waste
        </button>
      </div>
    </div>
  );

  const renderEmergencySupplies = () => (
    <div className="resource-section">
      <h3>🆘 Emergency Supplies</h3>
      <div className="resource-grid">
        <div className="resource-item">
          <div className="resource-header">
            <span>Supply Status</span>
          </div>
          <div className="emergency-supplies">
            <div className="supply-item">
              <span>Medical Supplies</span>
              <div className="supply-bar">
                <div style={{ 
                  width: `${resourceData.emergency?.medical || 0}%`,
                  backgroundColor: getStatusColor(resourceData.emergency?.medical || 0)
                }} />
              </div>
              <span>{resourceData.emergency?.medical || 0}%</span>
            </div>
            <div className="supply-item">
              <span>Emergency Rations</span>
              <div className="supply-bar">
                <div style={{ 
                  width: `${resourceData.emergency?.rations || 0}%`,
                  backgroundColor: getStatusColor(resourceData.emergency?.rations || 0)
                }} />
              </div>
              <span>{resourceData.emergency?.rations || 0}%</span>
            </div>
            <div className="supply-item">
              <span>Oxygen Backup</span>
              <div className="supply-bar">
                <div style={{ 
                  width: `${resourceData.emergency?.oxygen_backup || 0}%`,
                  backgroundColor: getStatusColor(resourceData.emergency?.oxygen_backup || 0)
                }} />
              </div>
              <span>{resourceData.emergency?.oxygen_backup || 0}%</span>
            </div>
            <div className="supply-item">
              <span>Repair Kits</span>
              <div className="supply-count">
                <span>{resourceData.emergency?.repair_kits || 0} kits available</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="resource-controls">
        <button 
          className={`resource-btn ${emergencyMode ? 'active emergency' : ''}`}
          onClick={() => {
            setEmergencyMode(!emergencyMode);
            handleResourceAction('deploy-emergency', { mode: !emergencyMode });
          }}
        >
          {emergencyMode ? 'Emergency Mode Active' : 'Deploy Emergency Protocol'}
        </button>
        <button 
          className="resource-btn secondary"
          onClick={() => handleResourceAction('resupply', {})}
        >
          Request Resupply
        </button>
      </div>
    </div>
  );

  if (loading) {
    return <div className="loading">Loading resource data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="resource-management">
      <div className="card">
        <h1>Resource Management</h1>
        <div className="ship-selector">
          <label>Select Ship: </label>
          <select 
            value={selectedShip?.symbol || ''} 
            onChange={(e) => {
              const ship = ships.find(s => s.symbol === e.target.value);
              setSelectedShip(ship);
            }}
          >
            {ships.map(ship => (
              <option key={ship.symbol} value={ship.symbol}>
                {ship.symbol} ({ship.registration?.name || 'Unnamed'})
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="resource-tabs">
        <button 
          className={`tab-btn ${activeTab === 'fuel' ? 'active' : ''}`}
          onClick={() => setActiveTab('fuel')}
        >
          ⛽ Fuel
        </button>
        <button 
          className={`tab-btn ${activeTab === 'power' ? 'active' : ''}`}
          onClick={() => setActiveTab('power')}
        >
          ⚡ Power
        </button>
        <button 
          className={`tab-btn ${activeTab === 'heat' ? 'active' : ''}`}
          onClick={() => setActiveTab('heat')}
        >
          🌡️ Heat
        </button>
        <button 
          className={`tab-btn ${activeTab === 'life' ? 'active' : ''}`}
          onClick={() => setActiveTab('life')}
        >
          🫁 Life Support
        </button>
        <button 
          className={`tab-btn ${activeTab === 'waste' ? 'active' : ''}`}
          onClick={() => setActiveTab('waste')}
        >
          ♻️ Waste
        </button>
        <button 
          className={`tab-btn ${activeTab === 'emergency' ? 'active' : ''}`}
          onClick={() => setActiveTab('emergency')}
        >
          🆘 Emergency
        </button>
      </div>

      <div className="resource-content">
        {activeTab === 'fuel' && renderFuelManagement()}
        {activeTab === 'power' && renderPowerManagement()}
        {activeTab === 'heat' && renderHeatDissipation()}
        {activeTab === 'life' && renderLifeSupport()}
        {activeTab === 'waste' && renderWasteRecycling()}
        {activeTab === 'emergency' && renderEmergencySupplies()}
      </div>
    </div>
  );
};

export default ResourceManagement;