import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ShipModifications.css';

const ShipModifications = ({ selectedShip, onShipUpdate, onClose }) => {
  const [activeTab, setActiveTab] = useState('modules');
  const [equipment, setEquipment] = useState({});
  const [modificationInfo, setModificationInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (selectedShip) {
      fetchEquipment();
      fetchModificationInfo();
    }
  }, [selectedShip]);

  const fetchEquipment = async () => {
    try {
      const response = await axios.get('/api/equipment');
      setEquipment(response.data.data);
    } catch (err) {
      setError('Failed to fetch equipment data');
    }
  };

  const fetchModificationInfo = async () => {
    try {
      const response = await axios.get(`/api/ships/${selectedShip.symbol}/modification-info`);
      setModificationInfo(response.data.data);
    } catch (err) {
      setError('Failed to fetch ship modification info');
    }
  };

  const handleInstallComponent = async (componentType, componentSymbol) => {
    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/install`, {
        shipSymbol: selectedShip.symbol,
        componentType,
        componentSymbol,
        action: 'install'
      });

      setSuccessMessage(`Successfully installed ${componentSymbol}!`);
      onShipUpdate(response.data.data.ship);
      fetchModificationInfo();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to install component');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveComponent = async (componentType, componentSymbol) => {
    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/remove`, {
        shipSymbol: selectedShip.symbol,
        componentType,
        componentSymbol,
        action: 'remove'
      });

      setSuccessMessage(`Successfully removed ${componentSymbol}! Refund: ${response.data.data.transaction.refund} credits`);
      onShipUpdate(response.data.data.ship);
      fetchModificationInfo();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to remove component');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomization = async (customizationData) => {
    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/customize`, {
        shipSymbol: selectedShip.symbol,
        ...customizationData
      });

      setSuccessMessage('Ship successfully customized!');
      onShipUpdate(response.data.data.ship);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to customize ship');
    } finally {
      setLoading(false);
    }
  };

  const renderEquipmentList = (componentType) => {
    const items = equipment[componentType] || [];
    const installedItems = selectedShip[componentType] || [];

    return (
      <div className="equipment-list">
        <h3>Available {componentType.charAt(0).toUpperCase() + componentType.slice(1)}</h3>
        <div className="equipment-grid">
          {items.map((item) => (
            <div key={item.symbol} className="equipment-item">
              <div className="equipment-header">
                <h4>{item.name}</h4>
                <span className="equipment-price">{item.price} credits</span>
              </div>
              <p className="equipment-description">{item.description}</p>
              
              <div className="equipment-stats">
                {item.capacity && <span>Capacity: {item.capacity}</span>}
                {item.range && <span>Range: {item.range}</span>}
                {item.strength && <span>Strength: {item.strength}</span>}
                {item.powerOutput && <span>Power Output: {item.powerOutput}</span>}
                {item.speed && <span>Speed: {item.speed}</span>}
              </div>

              <div className="equipment-requirements">
                <small>Requirements: Power: {item.requirements.power}, Crew: {item.requirements.crew}, Slots: {item.requirements.slots}</small>
              </div>

              <div className="equipment-actions">
                <button 
                  onClick={() => handleInstallComponent(componentType, item.symbol)}
                  disabled={loading}
                  className="install-btn"
                >
                  Install
                </button>
              </div>
            </div>
          ))}
        </div>

        {installedItems.length > 0 && (
          <div className="installed-components">
            <h3>Installed {componentType.charAt(0).toUpperCase() + componentType.slice(1)}</h3>
            <div className="installed-grid">
              {installedItems.map((item, index) => (
                <div key={index} className="installed-item">
                  <h4>{item.name}</h4>
                  <p>{item.description}</p>
                  <button 
                    onClick={() => handleRemoveComponent(componentType, item.symbol)}
                    disabled={loading}
                    className="remove-btn"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderCustomizationTab = () => {
    const [customName, setCustomName] = useState(selectedShip?.registration?.name || '');
    const [selectedColor, setSelectedColor] = useState(selectedShip?.customization?.color || '');
    const [selectedDecal, setSelectedDecal] = useState(selectedShip?.customization?.decal || '');

    const handleCustomizationSubmit = () => {
      const customizationData = {};
      if (customName !== selectedShip.registration?.name) customizationData.name = customName;
      if (selectedColor !== selectedShip.customization?.color) customizationData.color = selectedColor;
      if (selectedDecal !== selectedShip.customization?.decal) customizationData.decal = selectedDecal;

      if (Object.keys(customizationData).length > 0) {
        handleCustomization(customizationData);
      }
    };

    return (
      <div className="customization-panel">
        <h3>Ship Customization</h3>
        
        <div className="customization-section">
          <label>Ship Name:</label>
          <input
            type="text"
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
            placeholder="Enter ship name"
          />
        </div>

        <div className="customization-section">
          <label>Color:</label>
          <div className="color-options">
            {modificationInfo?.availableColors?.map((color) => (
              <div
                key={color}
                className={`color-option ${selectedColor === color ? 'selected' : ''}`}
                style={{ backgroundColor: color }}
                onClick={() => setSelectedColor(color)}
                title={color}
              />
            ))}
          </div>
        </div>

        <div className="customization-section">
          <label>Decal:</label>
          <select value={selectedDecal} onChange={(e) => setSelectedDecal(e.target.value)}>
            <option value="">No decal</option>
            {modificationInfo?.availableDecals?.map((decal) => (
              <option key={decal} value={decal}>
                {decal.charAt(0).toUpperCase() + decal.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <button 
          onClick={handleCustomizationSubmit}
          disabled={loading}
          className="customize-btn"
        >
          Apply Customization (1000 credits per change)
        </button>
      </div>
    );
  };

  const renderInfoPanel = () => {
    if (!modificationInfo) return null;

    return (
      <div className="info-panel">
        <h3>Ship Status</h3>
        <div className="status-grid">
          <div className="status-item">
            <label>Power Usage:</label>
            <span>{modificationInfo.powerInfo.currentUsage}/{modificationInfo.powerInfo.reactorPower}</span>
          </div>
          <div className="status-item">
            <label>Module Slots:</label>
            <span>{modificationInfo.slotInfo.usedModuleSlots}/{modificationInfo.slotInfo.moduleSlots}</span>
          </div>
          <div className="status-item">
            <label>Mounting Points:</label>
            <span>{modificationInfo.slotInfo.usedMountingPoints}/{modificationInfo.slotInfo.mountingPoints}</span>
          </div>
        </div>
      </div>
    );
  };

  if (!selectedShip) {
    return (
      <div className="ship-modifications">
        <p>Please select a ship to modify.</p>
      </div>
    );
  }

  return (
    <div className="ship-modifications">
      <div className="modifications-header">
        <h2>Ship Modifications - {selectedShip.symbol}</h2>
        <button onClick={onClose} className="close-btn">×</button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      {renderInfoPanel()}

      <div className="modifications-tabs">
        <button 
          className={`tab ${activeTab === 'modules' ? 'active' : ''}`}
          onClick={() => setActiveTab('modules')}
        >
          Modules
        </button>
        <button 
          className={`tab ${activeTab === 'mounts' ? 'active' : ''}`}
          onClick={() => setActiveTab('mounts')}
        >
          Mounts
        </button>
        <button 
          className={`tab ${activeTab === 'reactors' ? 'active' : ''}`}
          onClick={() => setActiveTab('reactors')}
        >
          Reactors
        </button>
        <button 
          className={`tab ${activeTab === 'engines' ? 'active' : ''}`}
          onClick={() => setActiveTab('engines')}
        >
          Engines
        </button>
        <button 
          className={`tab ${activeTab === 'customization' ? 'active' : ''}`}
          onClick={() => setActiveTab('customization')}
        >
          Customization
        </button>
      </div>

      <div className="modifications-content">
        {activeTab === 'customization' ? renderCustomizationTab() : renderEquipmentList(activeTab)}
      </div>
    </div>
  );
};

export default ShipModifications;