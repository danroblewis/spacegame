import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
  const [agent, setAgent] = useState(null);
  const [ships, setShips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [agentRes, shipsRes] = await Promise.all([
          axios.get('/api/agent'),
          axios.get('/api/ships')
        ]);
        
        setAgent(agentRes.data);
        setShips(shipsRes.data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Loading agent data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  const activeShips = ships.filter(ship => ship.nav?.status === 'IN_TRANSIT' || ship.nav?.status === 'IN_ORBIT');
  const totalCargo = ships.reduce((total, ship) => total + (ship.cargo?.units || 0), 0);

  return (
    <div className="dashboard">
      <h1>Agent Dashboard</h1>
      
      {agent && (
        <div className="card">
          <h2>Agent Information</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{agent.symbol}</div>
              <div className="stat-label">Agent Symbol</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{agent.credits.toLocaleString()}</div>
              <div className="stat-label">Credits</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{agent.startingFaction}</div>
              <div className="stat-label">Faction</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{agent.headquarters}</div>
              <div className="stat-label">Headquarters</div>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h2>Fleet Overview</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{ships.length}</div>
            <div className="stat-label">Total Ships</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{activeShips.length}</div>
            <div className="stat-label">Active Ships</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalCargo}</div>
            <div className="stat-label">Total Cargo</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Recent Activity</h2>
        <div className="grid">
          {ships.slice(0, 3).map((ship) => (
            <div key={ship.symbol} className="ship-card">
              <div className="ship-header">
                <span className="ship-name">{ship.symbol}</span>
                <span className={`ship-status ${ship.nav?.status === 'IN_TRANSIT' || ship.nav?.status === 'IN_ORBIT' ? 'active' : 'inactive'}`}>
                  {ship.nav?.status || 'UNKNOWN'}
                </span>
              </div>
              <div className="ship-details">
                <div className="detail-item">
                  <div className="detail-value">{ship.nav?.waypointSymbol || 'N/A'}</div>
                  <div className="detail-label">Location</div>
                </div>
                <div className="detail-item">
                  <div className="detail-value">{ship.cargo?.units || 0}</div>
                  <div className="detail-label">Cargo</div>
                </div>
                <div className="detail-item">
                  <div className="detail-value">{ship.crew?.current || 0}</div>
                  <div className="detail-label">Crew</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
