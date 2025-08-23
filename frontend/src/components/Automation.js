import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Automation = () => {
  const [automationStatus, setAutomationStatus] = useState(null);
  const [ships, setShips] = useState([]);
  const [selectedShip, setSelectedShip] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Auto-trading state
  const [autoTradeConfig, setAutoTradeConfig] = useState({
    enabled: false,
    min_profit_margin: 0.1,
    max_trade_distance: 10,
    preferred_goods: [],
    avoid_goods: []
  });

  // Route optimization state
  const [routeOptimization, setRouteOptimization] = useState({
    destination: '',
    optimize_for: 'fuel_efficiency'
  });

  // Combat AI state
  const [combatAIConfig, setCombatAIConfig] = useState({
    enabled: false,
    aggression_level: 'defensive',
    retreat_threshold: 0.3,
    target_priorities: ['pirates', 'hostiles']
  });

  // Resource monitoring state
  const [resourceMonitoring, setResourceMonitoring] = useState({});
  const [maintenancePredictions, setMaintenancePredictions] = useState({});
  const [crewAnalysis, setCrewAnalysis] = useState({});

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedShip && activeTab !== 'overview') {
      fetchShipSpecificData();
    }
  }, [selectedShip, activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statusRes, shipsRes] = await Promise.all([
        axios.get('/api/automation/status'),
        axios.get('/api/ships')
      ]);
      
      setAutomationStatus(statusRes.data);
      setShips(shipsRes.data);
      
      if (shipsRes.data.length > 0 && !selectedShip) {
        setSelectedShip(shipsRes.data[0].symbol);
      }
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const fetchShipSpecificData = async () => {
    if (!selectedShip) return;
    
    try {
      const promises = [];
      
      if (activeTab === 'maintenance') {
        promises.push(axios.get(`/api/automation/maintenance/predictions/${selectedShip}`));
      }
      if (activeTab === 'crew') {
        promises.push(axios.get(`/api/automation/crew-analysis/${selectedShip}`));
      }
      if (activeTab === 'resources') {
        promises.push(axios.get(`/api/automation/resource-optimization/${selectedShip}`));
      }
      
      const results = await Promise.all(promises);
      
      if (activeTab === 'maintenance' && results[0]) {
        setMaintenancePredictions(results[0].data);
      }
      if (activeTab === 'crew' && results[0]) {
        setCrewAnalysis(results[0].data);
      }
      if (activeTab === 'resources' && results[0]) {
        setResourceMonitoring(results[0].data);
      }
    } catch (err) {
      console.error('Failed to fetch ship-specific data:', err);
    }
  };

  const handleAutoTradeSubmit = async (e) => {
    e.preventDefault();
    if (!selectedShip) return;
    
    try {
      const config = { ship_symbol: selectedShip, ...autoTradeConfig };
      await axios.post('/api/automation/auto-trade/configure', config);
      alert('Auto-trading configured successfully!');
      fetchData();
    } catch (err) {
      alert('Failed to configure auto-trading: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRouteOptimization = async (e) => {
    e.preventDefault();
    if (!selectedShip || !routeOptimization.destination) return;
    
    try {
      const request = { ship_symbol: selectedShip, ...routeOptimization };
      const response = await axios.post('/api/automation/route-optimization', request);
      alert(`Route optimized! Savings: ${response.data.savings.fuel_saved} fuel, ${response.data.savings.time_saved} minutes`);
    } catch (err) {
      alert('Failed to optimize route: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCombatAISubmit = async (e) => {
    e.preventDefault();
    if (!selectedShip) return;
    
    try {
      const config = { ship_symbol: selectedShip, ...combatAIConfig };
      await axios.post('/api/automation/combat-ai/configure', config);
      alert('Combat AI configured successfully!');
      fetchData();
    } catch (err) {
      alert('Failed to configure combat AI: ' + (err.response?.data?.detail || err.message));
    }
  };

  const getStatusColor = (value, type = 'percentage') => {
    if (type === 'percentage') {
      if (value >= 0.8) return 'status-good';
      if (value >= 0.6) return 'status-warning';
      return 'status-critical';
    }
    return 'status-good';
  };

  const formatPercentage = (value) => {
    return `${Math.round(value * 100)}%`;
  };

  if (loading) {
    return <div className="loading">Loading automation data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="automation">
      <div className="card">
        <h1>🔄 Automation & AI Control Center</h1>
        <p>Manage all automated systems and AI-powered features for your fleet</p>
        
        <div className="ship-selector">
          <label>Select Ship: </label>
          <select 
            value={selectedShip} 
            onChange={(e) => setSelectedShip(e.target.value)}
          >
            <option value="">Choose a ship...</option>
            {ships.map(ship => (
              <option key={ship.symbol} value={ship.symbol}>
                {ship.symbol} ({ship.registration?.name || 'Unknown'})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        {[
          { id: 'overview', label: '📊 Overview', icon: '📊' },
          { id: 'auto-trade', label: '💰 Auto-Trading', icon: '💰' },
          { id: 'route', label: '🗺️ Route Optimization', icon: '🗺️' },
          { id: 'combat', label: '⚔️ Combat AI', icon: '⚔️' },
          { id: 'maintenance', label: '🔧 Maintenance', icon: '🔧' },
          { id: 'crew', label: '👥 Crew Management', icon: '👥' },
          { id: 'resources', label: '📦 Resource Monitoring', icon: '📦' }
        ].map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && automationStatus && (
          <div className="overview-tab">
            <div className="automation-grid">
              <div className="automation-card">
                <h3>💰 Auto-Trading</h3>
                <div className="stats">
                  <div className="stat">
                    <span className="stat-label">Active Ships:</span>
                    <span className="stat-value">{automationStatus.auto_trading.active_ships}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Trades Today:</span>
                    <span className="stat-value">{automationStatus.auto_trading.total_trades_today}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Profit Today:</span>
                    <span className="stat-value">{automationStatus.auto_trading.profit_today.toLocaleString()} credits</span>
                  </div>
                </div>
              </div>

              <div className="automation-card">
                <h3>🗺️ Route Optimization</h3>
                <div className="stats">
                  <div className="stat">
                    <span className="stat-label">Optimized Routes:</span>
                    <span className="stat-value">{automationStatus.route_optimization.optimized_routes}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Fuel Saved:</span>
                    <span className="stat-value">{automationStatus.route_optimization.fuel_saved} units</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Time Saved:</span>
                    <span className="stat-value">{automationStatus.route_optimization.time_saved} minutes</span>
                  </div>
                </div>
              </div>

              <div className="automation-card">
                <h3>⚔️ Combat AI</h3>
                <div className="stats">
                  <div className="stat">
                    <span className="stat-label">Active Ships:</span>
                    <span className="stat-value">{automationStatus.combat_ai.active_ships}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Threats Detected:</span>
                    <span className="stat-value">{automationStatus.combat_ai.threats_detected}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Engagements Today:</span>
                    <span className="stat-value">{automationStatus.combat_ai.engagements_today}</span>
                  </div>
                </div>
              </div>

              <div className="automation-card">
                <h3>🔧 Maintenance</h3>
                <div className="stats">
                  <div className="stat">
                    <span className="stat-label">Scheduled Tasks:</span>
                    <span className="stat-value">{automationStatus.maintenance.scheduled_tasks}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Overdue Tasks:</span>
                    <span className="stat-value">{automationStatus.maintenance.overdue_tasks}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Efficiency Rating:</span>
                    <span className="stat-value">{formatPercentage(automationStatus.maintenance.efficiency_rating)}</span>
                  </div>
                </div>
              </div>

              <div className="automation-card">
                <h3>👥 Crew Rotation</h3>
                <div className="stats">
                  <div className="stat">
                    <span className="stat-label">Managed Ships:</span>
                    <span className="stat-value">{automationStatus.crew_rotation.managed_ships}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Rotations This Week:</span>
                    <span className="stat-value">{automationStatus.crew_rotation.rotations_this_week}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Average Morale:</span>
                    <span className="stat-value">{formatPercentage(automationStatus.crew_rotation.average_morale)}</span>
                  </div>
                </div>
              </div>

              <div className="automation-card">
                <h3>📦 Resource Monitoring</h3>
                <div className="stats">
                  <div className="stat">
                    <span className="stat-label">Monitored Resources:</span>
                    <span className="stat-value">{automationStatus.resource_monitoring.monitored_resources}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Active Alerts:</span>
                    <span className="stat-value">{automationStatus.resource_monitoring.alerts_active}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Optimization Suggestions:</span>
                    <span className="stat-value">{automationStatus.resource_monitoring.optimization_suggestions}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'auto-trade' && (
          <div className="auto-trade-tab">
            <div className="card">
              <h3>💰 Auto-Trading Configuration</h3>
              <form onSubmit={handleAutoTradeSubmit}>
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={autoTradeConfig.enabled}
                      onChange={(e) => setAutoTradeConfig({...autoTradeConfig, enabled: e.target.checked})}
                    />
                    Enable Auto-Trading
                  </label>
                </div>
                
                <div className="form-group">
                  <label>Minimum Profit Margin:</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={autoTradeConfig.min_profit_margin}
                    onChange={(e) => setAutoTradeConfig({...autoTradeConfig, min_profit_margin: parseFloat(e.target.value)})}
                  />
                </div>
                
                <div className="form-group">
                  <label>Maximum Trade Distance:</label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={autoTradeConfig.max_trade_distance}
                    onChange={(e) => setAutoTradeConfig({...autoTradeConfig, max_trade_distance: parseInt(e.target.value)})}
                  />
                </div>
                
                <button type="submit" className="btn-primary" disabled={!selectedShip}>
                  Configure Auto-Trading
                </button>
              </form>
            </div>
            
            <div className="card">
              <h3>📈 Market Analysis</h3>
              <p>AI-powered market analysis will be displayed here once a ship is selected and auto-trading is configured.</p>
            </div>
          </div>
        )}

        {activeTab === 'route' && (
          <div className="route-tab">
            <div className="card">
              <h3>🗺️ Route Optimization</h3>
              <form onSubmit={handleRouteOptimization}>
                <div className="form-group">
                  <label>Destination:</label>
                  <input
                    type="text"
                    placeholder="e.g., X1-DF55-20250Z"
                    value={routeOptimization.destination}
                    onChange={(e) => setRouteOptimization({...routeOptimization, destination: e.target.value})}
                  />
                </div>
                
                <div className="form-group">
                  <label>Optimize For:</label>
                  <select
                    value={routeOptimization.optimize_for}
                    onChange={(e) => setRouteOptimization({...routeOptimization, optimize_for: e.target.value})}
                  >
                    <option value="fuel_efficiency">Fuel Efficiency</option>
                    <option value="time">Shortest Time</option>
                    <option value="profit">Maximum Profit</option>
                  </select>
                </div>
                
                <button type="submit" className="btn-primary" disabled={!selectedShip || !routeOptimization.destination}>
                  Optimize Route
                </button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'combat' && (
          <div className="combat-tab">
            <div className="card">
              <h3>⚔️ Combat AI Configuration</h3>
              <form onSubmit={handleCombatAISubmit}>
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={combatAIConfig.enabled}
                      onChange={(e) => setCombatAIConfig({...combatAIConfig, enabled: e.target.checked})}
                    />
                    Enable Combat AI
                  </label>
                </div>
                
                <div className="form-group">
                  <label>Aggression Level:</label>
                  <select
                    value={combatAIConfig.aggression_level}
                    onChange={(e) => setCombatAIConfig({...combatAIConfig, aggression_level: e.target.value})}
                  >
                    <option value="passive">Passive (Avoid all combat)</option>
                    <option value="defensive">Defensive (Defend when attacked)</option>
                    <option value="aggressive">Aggressive (Engage hostiles)</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Retreat Threshold:</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={combatAIConfig.retreat_threshold}
                    onChange={(e) => setCombatAIConfig({...combatAIConfig, retreat_threshold: parseFloat(e.target.value)})}
                  />
                  <small>Hull integrity percentage to retreat at</small>
                </div>
                
                <button type="submit" className="btn-primary" disabled={!selectedShip}>
                  Configure Combat AI
                </button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'maintenance' && maintenancePredictions && (
          <div className="maintenance-tab">
            <div className="card">
              <h3>🔧 Predictive Maintenance</h3>
              <div className="health-overview">
                <div className="overall-health">
                  <span className="health-label">Overall Ship Health:</span>
                  <span className={`health-value ${getStatusColor(maintenancePredictions.overall_health)}`}>
                    {formatPercentage(maintenancePredictions.overall_health)}
                  </span>
                </div>
              </div>
              
              <div className="components-grid">
                {Object.entries(maintenancePredictions.components || {}).map(([component, data]) => (
                  <div key={component} className="component-card">
                    <h4>{component.charAt(0).toUpperCase() + component.slice(1)}</h4>
                    <div className={`health-bar ${getStatusColor(data.health)}`}>
                      <div className="health-fill" style={{width: `${data.health * 100}%`}}></div>
                    </div>
                    <p>Health: {formatPercentage(data.health)}</p>
                    <p>Next Maintenance: {data.next_maintenance}</p>
                    <p className={`urgency urgency-${data.urgency}`}>Urgency: {data.urgency}</p>
                  </div>
                ))}
              </div>
              
              {maintenancePredictions.recommendations && (
                <div className="recommendations">
                  <h4>Recommendations:</h4>
                  <ul>
                    {maintenancePredictions.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'crew' && crewAnalysis && (
          <div className="crew-tab">
            <div className="card">
              <h3>👥 Crew Management</h3>
              <div className="crew-overview">
                <div className="crew-stats">
                  <div className="stat">
                    <span className="stat-label">Crew Size:</span>
                    <span className="stat-value">{crewAnalysis.crew_size}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Morale:</span>
                    <span className={`stat-value ${getStatusColor(crewAnalysis.morale)}`}>
                      {formatPercentage(crewAnalysis.morale)}
                    </span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Efficiency:</span>
                    <span className={`stat-value ${getStatusColor(crewAnalysis.efficiency)}`}>
                      {formatPercentage(crewAnalysis.efficiency)}
                    </span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Fatigue Level:</span>
                    <span className={`stat-value ${getStatusColor(1 - crewAnalysis.fatigue_level)}`}>
                      {formatPercentage(crewAnalysis.fatigue_level)}
                    </span>
                  </div>
                </div>
              </div>
              
              {crewAnalysis.crew_members && (
                <div className="crew-members">
                  <h4>Crew Members:</h4>
                  {crewAnalysis.crew_members.map((member, index) => (
                    <div key={index} className="crew-member-card">
                      <h5>{member.name}</h5>
                      <p><strong>Role:</strong> {member.role}</p>
                      <p><strong>Morale:</strong> {formatPercentage(member.morale)}</p>
                      <p><strong>Efficiency:</strong> {formatPercentage(member.efficiency)}</p>
                      <p><strong>Days Since Rotation:</strong> {member.days_since_rotation}</p>
                      <p className={`recommendation ${member.recommendation}`}>
                        {member.recommendation.replace(/_/g, ' ')}
                      </p>
                    </div>
                  ))}
                </div>
              )}
              
              {crewAnalysis.recommendations && (
                <div className="recommendations">
                  <h4>Recommendations:</h4>
                  <ul>
                    {crewAnalysis.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'resources' && resourceMonitoring && (
          <div className="resources-tab">
            <div className="card">
              <h3>📦 Resource Optimization</h3>
              <div className="efficiency-score">
                <span className="score-label">Efficiency Score:</span>
                <span className={`score-value ${getStatusColor(resourceMonitoring.efficiency_score)}`}>
                  {formatPercentage(resourceMonitoring.efficiency_score)}
                </span>
              </div>
              
              {resourceMonitoring.resources && (
                <div className="resources-grid">
                  {Object.entries(resourceMonitoring.resources).map(([resource, data]) => (
                    <div key={resource} className="resource-card">
                      <h4>{resource.charAt(0).toUpperCase() + resource.slice(1)}</h4>
                      <div className="resource-levels">
                        <div className="level-bar">
                          <div className="current-level" style={{width: `${(data.current / data.optimal) * 100}%`}}></div>
                        </div>
                        <p><strong>Current:</strong> {data.current}</p>
                        <p><strong>Optimal:</strong> {data.optimal}</p>
                        <p className={`status status-${data.status}`}>{data.status}</p>
                        <p className="recommendation">{data.recommendation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {resourceMonitoring.cost_savings && (
                <div className="cost-savings">
                  <h4>Cost Savings:</h4>
                  <p><strong>Weekly:</strong> {resourceMonitoring.cost_savings.weekly.toLocaleString()} credits</p>
                  <p><strong>Monthly:</strong> {resourceMonitoring.cost_savings.monthly.toLocaleString()} credits</p>
                </div>
              )}
              
              {resourceMonitoring.alerts && resourceMonitoring.alerts.length > 0 && (
                <div className="alerts">
                  <h4>Active Alerts:</h4>
                  <ul>
                    {resourceMonitoring.alerts.map((alert, index) => (
                      <li key={index} className="alert-item">{alert}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .automation {
          max-width: 1200px;
          margin: 0 auto;
        }

        .ship-selector {
          margin: 20px 0;
        }

        .ship-selector select {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .tab-navigation {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin: 20px 0;
          border-bottom: 2px solid #eee;
          padding-bottom: 10px;
        }

        .tab-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 16px;
          border: none;
          background: #f8f9fa;
          color: #666;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.3s ease;
          font-size: 14px;
        }

        .tab-button:hover {
          background: #e9ecef;
          color: #333;
        }

        .tab-button.active {
          background: #007bff;
          color: white;
        }

        .tab-icon {
          font-size: 16px;
        }

        .automation-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin: 20px 0;
        }

        .automation-card {
          background: white;
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .automation-card h3 {
          margin: 0 0 15px 0;
          color: #333;
          font-size: 18px;
        }

        .stats {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .stat {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .stat-label {
          color: #666;
          font-size: 14px;
        }

        .stat-value {
          font-weight: bold;
          color: #333;
        }

        .form-group {
          margin: 15px 0;
        }

        .form-group label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
          color: #333;
        }

        .form-group input,
        .form-group select {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .form-group small {
          display: block;
          margin-top: 5px;
          color: #666;
          font-size: 12px;
        }

        .btn-primary {
          background: #007bff;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: background 0.3s ease;
        }

        .btn-primary:hover:not(:disabled) {
          background: #0056b3;
        }

        .btn-primary:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .components-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 15px;
          margin: 20px 0;
        }

        .component-card {
          border: 1px solid #ddd;
          border-radius: 6px;
          padding: 15px;
          background: #f8f9fa;
        }

        .health-bar {
          width: 100%;
          height: 20px;
          background: #e9ecef;
          border-radius: 10px;
          overflow: hidden;
          margin: 10px 0;
        }

        .health-fill {
          height: 100%;
          background: #28a745;
          transition: width 0.3s ease;
        }

        .status-warning .health-fill {
          background: #ffc107;
        }

        .status-critical .health-fill {
          background: #dc3545;
        }

        .urgency {
          font-weight: bold;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 12px;
        }

        .urgency-low {
          background: #d4edda;
          color: #155724;
        }

        .urgency-medium {
          background: #fff3cd;
          color: #856404;
        }

        .urgency-high {
          background: #f8d7da;
          color: #721c24;
        }

        .crew-members {
          margin: 20px 0;
        }

        .crew-member-card {
          border: 1px solid #ddd;
          border-radius: 6px;
          padding: 15px;
          margin: 10px 0;
          background: #f8f9fa;
        }

        .resources-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin: 20px 0;
        }

        .resource-card {
          border: 1px solid #ddd;
          border-radius: 6px;
          padding: 15px;
          background: #f8f9fa;
        }

        .level-bar {
          width: 100%;
          height: 15px;
          background: #e9ecef;
          border-radius: 8px;
          overflow: hidden;
          margin: 10px 0;
        }

        .current-level {
          height: 100%;
          background: #007bff;
          transition: width 0.3s ease;
        }

        .status-good {
          color: #28a745;
        }

        .status-warning {
          color: #ffc107;
        }

        .status-critical {
          color: #dc3545;
        }

        .recommendations,
        .alerts {
          margin: 20px 0;
        }

        .recommendations ul,
        .alerts ul {
          list-style-type: disc;
          padding-left: 20px;
        }

        .alert-item {
          color: #856404;
          background: #fff3cd;
          padding: 5px;
          margin: 5px 0;
          border-radius: 3px;
        }

        .cost-savings {
          background: #d4edda;
          padding: 15px;
          border-radius: 6px;
          margin: 20px 0;
        }

        .efficiency-score {
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #e9ecef;
          padding: 15px;
          border-radius: 6px;
          margin: 15px 0;
        }

        .score-label {
          font-weight: bold;
          color: #333;
        }

        .score-value {
          font-size: 24px;
          font-weight: bold;
        }

        @media (max-width: 768px) {
          .tab-navigation {
            flex-direction: column;
          }
          
          .automation-grid {
            grid-template-columns: 1fr;
          }
          
          .components-grid,
          .resources-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default Automation;