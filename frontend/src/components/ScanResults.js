import React from 'react';

const ScanResults = ({ scanData, scanType, timestamp }) => {
  if (!scanData) return null;

  const formatThreatLevel = (level) => {
    const colors = {
      'LOW': '#4CAF50',
      'MEDIUM': '#FF9800', 
      'HIGH': '#F44336',
      'CRITICAL': '#9C27B0'
    };
    return (
      <span style={{ color: colors[level] || '#666', fontWeight: 'bold' }}>
        {level}
      </span>
    );
  };

  const formatDistance = (distance) => {
    return distance ? `${distance.toFixed(1)} units` : 'Unknown';
  };

  const renderSystemsData = () => (
    <div className="scan-results systems-scan">
      <h3>🌌 Long-Range Sensor Data</h3>
      <p className="scan-subtitle">Detected Systems and Celestial Objects</p>
      
      {scanData.systems && scanData.systems.length > 0 ? (
        <div className="systems-grid">
          {scanData.systems.map((system, index) => (
            <div key={index} className="system-card scan-card">
              <div className="system-header">
                <h4>{system.symbol}</h4>
                <span className="system-type">{system.type.replace(/_/g, ' ')}</span>
              </div>
              <div className="system-details">
                <div className="detail-row">
                  <span className="label">Sector:</span>
                  <span className="value">{system.sectorSymbol}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Coordinates:</span>
                  <span className="value">({system.x}, {system.y})</span>
                </div>
                <div className="detail-row">
                  <span className="label">Distance:</span>
                  <span className="value distance">{formatDistance(system.distance)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-data">No systems detected in scan range.</p>
      )}
    </div>
  );

  const renderWaypointsData = () => (
    <div className="scan-results waypoints-scan">
      <h3>🪐 Planetary Survey Data</h3>
      <p className="scan-subtitle">Waypoint Analysis and Resource Detection</p>
      
      {scanData.waypoints && scanData.waypoints.length > 0 ? (
        <div className="waypoints-grid">
          {scanData.waypoints.map((waypoint, index) => (
            <div key={index} className="waypoint-card scan-card">
              <div className="waypoint-header">
                <h4>{waypoint.symbol}</h4>
                <span className="waypoint-type">{waypoint.type.replace(/_/g, ' ')}</span>
              </div>
              <div className="waypoint-details">
                <div className="detail-row">
                  <span className="label">System:</span>
                  <span className="value">{waypoint.systemSymbol}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Coordinates:</span>
                  <span className="value">({waypoint.x}, {waypoint.y})</span>
                </div>
                {waypoint.traits && waypoint.traits.length > 0 && (
                  <div className="traits-section">
                    <h5>Detected Resources & Traits:</h5>
                    <div className="traits-grid">
                      {waypoint.traits.map((trait, idx) => (
                        <div key={idx} className="trait-item">
                          <span className="trait-name">{trait.name}</span>
                          <span className="trait-description">{trait.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-data">No new waypoints detected in scan range.</p>
      )}
    </div>
  );

  const renderShipsData = () => (
    <div className="scan-results ships-scan">
      <h3>📡 Ship Scanner & Threat Assessment</h3>
      <p className="scan-subtitle">Signal Interception and Proximity Analysis</p>
      
      {scanData.ships && scanData.ships.length > 0 ? (
        <div className="ships-grid">
          {scanData.ships.map((ship, index) => (
            <div key={index} className="ship-card scan-card">
              <div className="ship-header">
                <h4>{ship.symbol}</h4>
                <div className="ship-badges">
                  <span className="ship-role">{ship.registration?.role || 'Unknown'}</span>
                  {ship.threat_level && (
                    <span className="threat-level">
                      Threat: {formatThreatLevel(ship.threat_level)}
                    </span>
                  )}
                </div>
              </div>
              <div className="ship-details">
                <div className="detail-row">
                  <span className="label">Faction:</span>
                  <span className="value">{ship.registration?.factionSymbol || 'Unknown'}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Location:</span>
                  <span className="value">{ship.nav?.waypointSymbol || 'Unknown'}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Status:</span>
                  <span className="value">{ship.nav?.status || 'Unknown'}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Distance:</span>
                  <span className="value distance">{formatDistance(ship.distance)}</span>
                </div>
                {ship.frame && (
                  <div className="detail-row">
                    <span className="label">Frame:</span>
                    <span className="value">{ship.frame.symbol?.replace('FRAME_', '') || 'Unknown'}</span>
                  </div>
                )}
                {ship.cargo && (
                  <div className="detail-row">
                    <span className="label">Cargo:</span>
                    <span className="value">{ship.cargo.units || 0}/{ship.cargo.capacity || 0}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-data">No ships detected in scan range.</p>
      )}
    </div>
  );

  const renderSurveyData = () => (
    <div className="scan-results survey-scan">
      <h3>⛏️ Resource Survey Data</h3>
      <p className="scan-subtitle">Detailed Resource Mapping and Mining Prospects</p>
      
      {scanData.surveys && scanData.surveys.length > 0 ? (
        <div className="surveys-grid">
          {scanData.surveys.map((survey, index) => (
            <div key={index} className="survey-card scan-card">
              <div className="survey-header">
                <h4>Survey #{survey.signature}</h4>
                <div className="survey-badges">
                  <span className="survey-size">{survey.size} Deposit</span>
                </div>
              </div>
              <div className="survey-details">
                <div className="detail-row">
                  <span className="label">Location:</span>
                  <span className="value">{survey.symbol}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Expires:</span>
                  <span className="value">{new Date(survey.expiration).toLocaleString()}</span>
                </div>
                {survey.deposits && survey.deposits.length > 0 && (
                  <div className="deposits-section">
                    <h5>Detected Resources:</h5>
                    <div className="deposits-grid">
                      {survey.deposits.map((deposit, idx) => (
                        <div key={idx} className="deposit-item">
                          <span className="deposit-symbol">{deposit.symbol}</span>
                          <span className="deposit-name">{deposit.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-data">No surveys generated. Current location may not be suitable for resource extraction.</p>
      )}
    </div>
  );

  return (
    <div className="scan-results-container">
      <div className="scan-header">
        <div className="scan-timestamp">
          Scan completed: {timestamp ? new Date(timestamp).toLocaleString() : 'Unknown time'}
        </div>
        {scanData.cooldown && (
          <div className="cooldown-info">
            Cooldown: {scanData.cooldown.remainingSeconds}s remaining
          </div>
        )}
      </div>

      {scanType === 'systems' && renderSystemsData()}
      {scanType === 'waypoints' && renderWaypointsData()}
      {scanType === 'ships' && renderShipsData()}
      {scanType === 'survey' && renderSurveyData()}
    </div>
  );
};

export default ScanResults;