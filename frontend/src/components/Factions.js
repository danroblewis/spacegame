import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Factions = () => {
  const [factions, setFactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFactions();
  }, []);

  const fetchFactions = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/factions');
      setFactions(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch factions');
    } finally {
      setLoading(false);
    }
  };

  const getFactionColor = (symbol) => {
    const colors = {
      'COSMIC': '#667eea',
      'VOID': '#764ba2',
      'GALACTIC': '#f093fb',
      'QUANTUM': '#4facfe',
      'DOMINION': '#43e97b',
      'ASTRO': '#38f9d7',
      'CORSAIRS': '#fa709a',
      'OBSIDIAN': '#a8edea',
      'AEGIS': '#fed6e3',
      'UNITED': '#a8caba',
      'SOLITARY': '#d299c2',
      'COBALT': '#667eea',
      'OMEGA': '#764ba2',
      'ECHO': '#f093fb',
      'LORDS': '#4facfe',
      'CULT': '#43e97b',
      'ANCIENTS': '#38f9d7',
      'SHADOW': '#fa709a',
      'ETHEREAL': '#a8edea'
    };
    return colors[symbol] || '#cccccc';
  };

  if (loading) {
    return <div className="loading">Loading factions data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="factions">
      <div className="card">
        <h1>Factions</h1>
        <p>Total Factions: {factions.length}</p>
      </div>

      {factions.length === 0 ? (
        <div className="card">
          <p>No factions found.</p>
        </div>
      ) : (
        <div className="grid">
          {factions.map((faction) => (
            <div key={faction.symbol} className="faction-card">
              <div className="faction-header">
                <h3 className="faction-name">{faction.name}</h3>
                <span 
                  className="faction-symbol"
                  style={{ backgroundColor: getFactionColor(faction.symbol) }}
                >
                  {faction.symbol}
                </span>
              </div>

              <div className="faction-description">
                <p>{faction.description}</p>
              </div>

              <div className="faction-details">
                <div className="detail-item">
                  <div className="detail-value">{faction.headquarters}</div>
                  <div className="detail-label">Headquarters</div>
                </div>
                <div className="detail-item">
                  <div className="detail-value">{faction.isRecruiting ? 'Yes' : 'No'}</div>
                  <div className="detail-label">Recruiting</div>
                </div>
                <div className="detail-item">
                  <div className="detail-value">{faction.traits?.length || 0}</div>
                  <div className="detail-label">Traits</div>
                </div>
              </div>

              {faction.traits && faction.traits.length > 0 && (
                <div className="traits-section">
                  <h4>Traits:</h4>
                  <div className="traits-grid">
                    {faction.traits.map((trait, index) => (
                      <div key={index} className="trait-item">
                        <span className="trait-name">{trait.name}</span>
                        <span className="trait-description">{trait.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Factions;
