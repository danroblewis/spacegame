import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Crew = () => {
  const [ships, setShips] = useState([]);
  const [selectedShip, setSelectedShip] = useState(null);
  const [crewMembers, setCrewMembers] = useState([]);
  const [availableCrew, setAvailableCrew] = useState([]);
  const [quarters, setQuarters] = useState(null);
  const [medicalBay, setMedicalBay] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('roster');
  const [selectedCrewMember, setSelectedCrewMember] = useState(null);

  useEffect(() => {
    fetchShips();
  }, []);

  useEffect(() => {
    if (selectedShip) {
      fetchCrewData();
    }
  }, [selectedShip]);

  const fetchShips = async () => {
    try {
      const response = await axios.get('/api/ships');
      setShips(response.data);
      if (response.data.length > 0 && !selectedShip) {
        setSelectedShip(response.data[0]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch ships');
    }
  };

  const fetchCrewData = async () => {
    if (!selectedShip) return;
    
    try {
      setLoading(true);
      const [crewRes, availableRes, quartersRes, medicalRes] = await Promise.all([
        axios.get(`/api/ships/${selectedShip.symbol}/crew`),
        axios.get(`/api/ships/${selectedShip.symbol}/crew/available`),
        axios.get(`/api/ships/${selectedShip.symbol}/crew/quarters`),
        axios.get(`/api/ships/${selectedShip.symbol}/crew/medical`)
      ]);
      
      setCrewMembers(crewRes.data);
      setAvailableCrew(availableRes.data);
      setQuarters(quartersRes.data);
      setMedicalBay(medicalRes.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch crew data');
    } finally {
      setLoading(false);
    }
  };

  const hireCrew = async (role, maxSalary) => {
    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/crew/hire`, {
        role,
        max_salary: maxSalary
      });
      
      await fetchCrewData();
      await fetchShips(); // Update ship crew count
      alert(response.data.message);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to hire crew member');
    }
  };

  const fireCrew = async (crewId) => {
    if (!confirm('Are you sure you want to fire this crew member?')) return;
    
    try {
      const response = await axios.delete(`/api/ships/${selectedShip.symbol}/crew/${crewId}`);
      await fetchCrewData();
      await fetchShips(); // Update ship crew count
      alert(response.data.message);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to fire crew member');
    }
  };

  const trainCrew = async (crewId, skill, hours) => {
    try {
      const response = await axios.put(`/api/ships/${selectedShip.symbol}/crew/${crewId}/train`, {
        skill,
        duration_hours: hours
      });
      
      await fetchCrewData();
      alert(response.data.message);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to train crew member');
    }
  };

  const assignRole = async (crewId, newRole) => {
    try {
      const response = await axios.put(`/api/ships/${selectedShip.symbol}/crew/${crewId}/assign`, {
        new_role: newRole
      });
      
      await fetchCrewData();
      alert(response.data.message);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to assign role');
    }
  };

  const upgradeQuarters = async () => {
    try {
      const response = await axios.put(`/api/ships/${selectedShip.symbol}/crew/quarters`);
      await fetchCrewData();
      alert(response.data.message);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to upgrade quarters');
    }
  };

  const treatCrew = async (crewIds) => {
    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/crew/medical/treat`, {
        crew_ids: crewIds
      });
      
      await fetchCrewData();
      alert(`${response.data.message}. Cost: ${response.data.cost} credits`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to treat crew members');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'green';
      case 'INJURED': return 'red';
      case 'RESTING': return 'orange';
      case 'TRAINING': return 'blue';
      default: return 'gray';
    }
  };

  const getHealthColor = (health) => {
    if (health >= 80) return 'green';
    if (health >= 60) return 'orange';
    return 'red';
  };

  const getMoraleColor = (morale) => {
    if (morale >= 80) return 'green';
    if (morale >= 60) return 'orange';
    return 'red';
  };

  if (loading) {
    return <div className="loading">Loading crew data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="crew-management">
      <div className="card">
        <h1>👥 Crew Management</h1>
        
        {/* Ship Selection */}
        <div className="ship-selector">
          <label>Select Ship: </label>
          <select 
            value={selectedShip?.symbol || ''} 
            onChange={(e) => setSelectedShip(ships.find(s => s.symbol === e.target.value))}
          >
            {ships.map(ship => (
              <option key={ship.symbol} value={ship.symbol}>
                {ship.symbol} ({ship.crew?.current || 0}/{ship.crew?.capacity || 0} crew)
              </option>
            ))}
          </select>
        </div>

        {/* Tab Navigation */}
        <div className="tabs">
          <button 
            className={activeTab === 'roster' ? 'active' : ''} 
            onClick={() => setActiveTab('roster')}
          >
            Crew Roster
          </button>
          <button 
            className={activeTab === 'hire' ? 'active' : ''} 
            onClick={() => setActiveTab('hire')}
          >
            Hire Crew
          </button>
          <button 
            className={activeTab === 'quarters' ? 'active' : ''} 
            onClick={() => setActiveTab('quarters')}
          >
            Crew Quarters
          </button>
          <button 
            className={activeTab === 'medical' ? 'active' : ''} 
            onClick={() => setActiveTab('medical')}
          >
            Medical Bay
          </button>
        </div>
      </div>

      {/* Crew Roster Tab */}
      {activeTab === 'roster' && (
        <div className="card">
          <h2>Crew Roster ({crewMembers.length})</h2>
          
          {crewMembers.length === 0 ? (
            <p>No crew members aboard this ship.</p>
          ) : (
            <div className="crew-grid">
              {crewMembers.map(crew => (
                <div key={crew.id} className="crew-card">
                  <div className="crew-header">
                    <h3>{crew.name}</h3>
                    <span className={`crew-status ${getStatusColor(crew.status)}`}>
                      {crew.status}
                    </span>
                  </div>
                  
                  <div className="crew-details">
                    <div className="detail-row">
                      <span>Role:</span>
                      <span>{crew.role}</span>
                    </div>
                    <div className="detail-row">
                      <span>Level:</span>
                      <span>{crew.level}</span>
                    </div>
                    <div className="detail-row">
                      <span>Experience:</span>
                      <span>{crew.experience.toLocaleString()}</span>
                    </div>
                    <div className="detail-row">
                      <span>Health:</span>
                      <span style={{color: getHealthColor(crew.health)}}>{crew.health}%</span>
                    </div>
                    <div className="detail-row">
                      <span>Morale:</span>
                      <span style={{color: getMoraleColor(crew.morale)}}>{crew.morale}%</span>
                    </div>
                    <div className="detail-row">
                      <span>Salary:</span>
                      <span>{crew.salary} credits/day</span>
                    </div>
                  </div>

                  <div className="crew-skills">
                    <h4>Skills:</h4>
                    {Object.entries(crew.skills).map(([skill, level]) => (
                      <div key={skill} className="skill-bar">
                        <span>{skill}:</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{width: `${level}%`}}
                          ></div>
                          <span className="progress-text">{level}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="crew-actions">
                    <button 
                      onClick={() => setSelectedCrewMember(crew)}
                      className="btn-secondary"
                    >
                      Manage
                    </button>
                    <button 
                      onClick={() => fireCrew(crew.id)}
                      className="btn-danger"
                    >
                      Fire
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Hire Crew Tab */}
      {activeTab === 'hire' && (
        <div className="card">
          <h2>Available Crew for Hire</h2>
          
          <div className="crew-grid">
            {availableCrew.map(crew => (
              <div key={crew.id} className="crew-card available">
                <div className="crew-header">
                  <h3>{crew.name}</h3>
                  <span className="crew-role">{crew.role}</span>
                </div>
                
                <div className="crew-details">
                  <div className="detail-row">
                    <span>Level:</span>
                    <span>{crew.level}</span>
                  </div>
                  <div className="detail-row">
                    <span>Salary:</span>
                    <span>{crew.salary} credits/day</span>
                  </div>
                </div>

                <div className="crew-skills">
                  <h4>Skills:</h4>
                  {Object.entries(crew.skills).map(([skill, level]) => (
                    <div key={skill} className="skill-bar">
                      <span>{skill}:</span>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{width: `${level}%`}}
                        ></div>
                        <span className="progress-text">{level}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="crew-actions">
                  <button 
                    onClick={() => hireCrew(crew.role, crew.salary)}
                    className="btn-primary"
                    disabled={selectedShip?.crew?.current >= selectedShip?.crew?.capacity}
                  >
                    Hire ({crew.salary} credits/day)
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Crew Quarters Tab */}
      {activeTab === 'quarters' && quarters && (
        <div className="card">
          <h2>🏠 Crew Quarters</h2>
          
          <div className="quarters-info">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{quarters.capacity}</div>
                <div className="stat-label">Capacity</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{quarters.comfort_level}/5</div>
                <div className="stat-label">Comfort Level</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{quarters.maintenance_cost}</div>
                <div className="stat-label">Daily Maintenance</div>
              </div>
            </div>

            <div className="facilities">
              <h3>Facilities:</h3>
              <ul>
                {quarters.facilities.map(facility => (
                  <li key={facility}>{facility.replace('_', ' ').toUpperCase()}</li>
                ))}
              </ul>
            </div>

            <div className="quarters-actions">
              <button 
                onClick={upgradeQuarters}
                className="btn-primary"
                disabled={quarters.comfort_level >= 5}
              >
                {quarters.comfort_level >= 5 ? 'Max Level Reached' : 'Upgrade Quarters'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Medical Bay Tab */}
      {activeTab === 'medical' && medicalBay && (
        <div className="card">
          <h2>🏥 Medical Bay</h2>
          
          <div className="medical-info">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{medicalBay.level}/5</div>
                <div className="stat-label">Medical Level</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{medicalBay.capacity}</div>
                <div className="stat-label">Treatment Capacity</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{medicalBay.treatment_cost}</div>
                <div className="stat-label">Treatment Cost</div>
              </div>
            </div>

            <div className="equipment">
              <h3>Equipment:</h3>
              <ul>
                {medicalBay.equipment.map(item => (
                  <li key={item}>{item.replace('_', ' ').toUpperCase()}</li>
                ))}
              </ul>
            </div>

            <div className="injured-crew">
              <h3>Crew Needing Treatment:</h3>
              {crewMembers.filter(crew => crew.health < 100).length === 0 ? (
                <p>All crew members are healthy!</p>
              ) : (
                <div className="injured-list">
                  {crewMembers.filter(crew => crew.health < 100).map(crew => (
                    <div key={crew.id} className="injured-crew-item">
                      <span>{crew.name}</span>
                      <span style={{color: getHealthColor(crew.health)}}>
                        Health: {crew.health}%
                      </span>
                      <button 
                        onClick={() => treatCrew([crew.id])}
                        className="btn-primary small"
                      >
                        Treat ({medicalBay.treatment_cost} credits)
                      </button>
                    </div>
                  ))}
                  
                  {crewMembers.filter(crew => crew.health < 100).length > 1 && (
                    <button 
                      onClick={() => treatCrew(crewMembers.filter(crew => crew.health < 100).map(c => c.id))}
                      className="btn-primary"
                    >
                      Treat All ({crewMembers.filter(crew => crew.health < 100).length * medicalBay.treatment_cost} credits)
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Crew Management Modal */}
      {selectedCrewMember && (
        <div className="modal-overlay" onClick={() => setSelectedCrewMember(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Manage {selectedCrewMember.name}</h2>
              <button 
                onClick={() => setSelectedCrewMember(null)}
                className="close-btn"
              >
                ×
              </button>
            </div>
            
            <div className="modal-content">
              <div className="manage-section">
                <h3>Train Skills</h3>
                {Object.keys(selectedCrewMember.skills).map(skill => (
                  <div key={skill} className="train-option">
                    <span>{skill} (Current: {selectedCrewMember.skills[skill]})</span>
                    <button 
                      onClick={() => trainCrew(selectedCrewMember.id, skill, 4)}
                      className="btn-secondary small"
                      disabled={selectedCrewMember.status !== 'ACTIVE'}
                    >
                      Train 4h (200 credits)
                    </button>
                  </div>
                ))}
              </div>

              <div className="manage-section">
                <h3>Assign New Role</h3>
                <select 
                  onChange={(e) => e.target.value && assignRole(selectedCrewMember.id, e.target.value)}
                  defaultValue=""
                >
                  <option value="">Select new role...</option>
                  <option value="PILOT">Pilot</option>
                  <option value="ENGINEER">Engineer</option>
                  <option value="GUNNER">Gunner</option>
                  <option value="MEDIC">Medic</option>
                  <option value="SECURITY">Security</option>
                  <option value="MINER">Miner</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Crew;