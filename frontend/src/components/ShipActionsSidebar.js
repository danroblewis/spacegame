import React, { useState } from 'react';

const ShipActionsSidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className={`ship-actions-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <h3>🚀 Ship Actions</h3>
        <button 
          className="collapse-btn" 
          onClick={toggleSidebar}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? '►' : '◄'}
        </button>
      </div>
      
      {!isCollapsed && (
        <div className="sidebar-content">
          <div className="action-section">
            <h4>Navigation</h4>
            <div className="action-buttons-placeholder">
              <div className="placeholder-text">
                Navigation actions will appear here
              </div>
            </div>
          </div>

          <div className="action-section">
            <h4>Trading</h4>
            <div className="action-buttons-placeholder">
              <div className="placeholder-text">
                Trading actions will appear here
              </div>
            </div>
          </div>

          <div className="action-section">
            <h4>Mining</h4>
            <div className="action-buttons-placeholder">
              <div className="placeholder-text">
                Mining actions will appear here
              </div>
            </div>
          </div>

          <div className="action-section">
            <h4>Refuel & Repair</h4>
            <div className="action-buttons-placeholder">
              <div className="placeholder-text">
                Maintenance actions will appear here
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShipActionsSidebar;