import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ShipActionsSidebar = ({ selectedShip, onShipUpdate }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [market, setMarket] = useState(null);
  const [cargo, setCargo] = useState(null);
  const [activeTab, setActiveTab] = useState('cargo');
  const [notification, setNotification] = useState(null);
  const [smugglingStatus, setSmugglingStatus] = useState(null);

  // Form states
  const [purchaseForm, setPurchaseForm] = useState({ symbol: '', units: 1 });
  const [sellForm, setSellForm] = useState({ symbol: '', units: 1 });
  const [jettisonForm, setJettisonForm] = useState({ symbol: '', units: 1 });
  const [transferForm, setTransferForm] = useState({ symbol: '', units: 1, destination: '' });

  useEffect(() => {
    if (selectedShip && !isCollapsed) {
      fetchCargo();
      fetchMarket();
      fetchSmugglingStatus();
    }
  }, [selectedShip, isCollapsed]);

  const fetchCargo = async () => {
    if (!selectedShip) return;
    
    try {
      const response = await axios.get(`/api/ships/${selectedShip.symbol}/cargo`);
      setCargo(response.data.data);
    } catch (error) {
      showNotification('Failed to fetch cargo', 'error');
    }
  };

  const fetchMarket = async () => {
    if (!selectedShip || !selectedShip.nav?.waypointSymbol) return;
    
    try {
      const systemSymbol = selectedShip.nav.systemSymbol;
      const waypointSymbol = selectedShip.nav.waypointSymbol;
      const response = await axios.get(`/api/systems/${systemSymbol}/waypoints/${waypointSymbol}/market`);
      setMarket(response.data.data);
    } catch (error) {
      console.log('No market available at this location');
      setMarket(null);
    }
  };

  const fetchSmugglingStatus = async () => {
    if (!selectedShip) return;
    
    try {
      const response = await axios.get(`/api/ships/${selectedShip.symbol}/smuggling/status`);
      setSmugglingStatus(response.data.data);
    } catch (error) {
      console.log('Smuggling status not available');
      setSmugglingStatus(null);
    }
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handlePurchase = async (e) => {
    e.preventDefault();
    if (!selectedShip || !purchaseForm.symbol || !purchaseForm.units) return;

    setLoading(true);
    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/purchase`, {
        symbol: purchaseForm.symbol,
        units: parseInt(purchaseForm.units)
      });
      
      await fetchCargo();
      if (onShipUpdate) onShipUpdate(selectedShip);
      showNotification(`Purchased ${purchaseForm.units} units of ${purchaseForm.symbol}`, 'success');
      setPurchaseForm({ symbol: '', units: 1 });
    } catch (error) {
      showNotification(error.response?.data?.detail || 'Purchase failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSell = async (e) => {
    e.preventDefault();
    if (!selectedShip || !sellForm.symbol || !sellForm.units) return;

    setLoading(true);
    try {
      await axios.post(`/api/ships/${selectedShip.symbol}/sell`, {
        symbol: sellForm.symbol,
        units: parseInt(sellForm.units)
      });
      
      await fetchCargo();
      if (onShipUpdate) onShipUpdate(selectedShip);
      showNotification(`Sold ${sellForm.units} units of ${sellForm.symbol}`, 'success');
      setSellForm({ symbol: '', units: 1 });
    } catch (error) {
      showNotification(error.response?.data?.detail || 'Sale failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleJettison = async (e) => {
    e.preventDefault();
    if (!selectedShip || !jettisonForm.symbol || !jettisonForm.units) return;

    setLoading(true);
    try {
      await axios.post(`/api/ships/${selectedShip.symbol}/jettison`, {
        symbol: jettisonForm.symbol,
        units: parseInt(jettisonForm.units)
      });
      
      await fetchCargo();
      if (onShipUpdate) onShipUpdate(selectedShip);
      showNotification(`Jettisoned ${jettisonForm.units} units of ${jettisonForm.symbol}`, 'success');
      setJettisonForm({ symbol: '', units: 1 });
    } catch (error) {
      showNotification(error.response?.data?.detail || 'Jettison failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleTransfer = async (e) => {
    e.preventDefault();
    if (!selectedShip || !transferForm.symbol || !transferForm.units || !transferForm.destination) return;

    setLoading(true);
    try {
      await axios.post(`/api/ships/${selectedShip.symbol}/transfer`, {
        symbol: transferForm.symbol,
        units: parseInt(transferForm.units),
        destination: transferForm.destination
      });
      
      await fetchCargo();
      if (onShipUpdate) onShipUpdate(selectedShip);
      showNotification(`Transferred ${transferForm.units} units of ${transferForm.symbol}`, 'success');
      setTransferForm({ symbol: '', units: 1, destination: '' });
    } catch (error) {
      showNotification(error.response?.data?.detail || 'Transfer failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const optimizeCargo = async () => {
    if (!cargo || !selectedShip) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/cargo/optimize`);
      const optimization = response.data.data.optimization;
      
      await fetchCargo();
      if (onShipUpdate) onShipUpdate(selectedShip);
      
      showNotification(
        `Cargo optimized! ${optimization.efficiency_improvement} efficiency improvement. ${optimization.space_saved} units of space saved.`,
        'success'
      );
    } catch (error) {
      showNotification('Cargo optimization failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const scanCargo = async () => {
    if (!cargo || !selectedShip) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`/api/ships/${selectedShip.symbol}/cargo/scan`);
      const scanResults = response.data.data.scan_results;
      
      const message = `Scan complete: ${scanResults.total_items} item types, ${scanResults.capacity_used}% capacity, ~${scanResults.estimated_value} credits value. Integrity: ${scanResults.cargo_integrity}`;
      showNotification(message, 'info');
    } catch (error) {
      showNotification('Cargo scan failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const configureSecretCompartment = async () => {
    if (!selectedShip) return;
    
    setLoading(true);
    try {
      await axios.post(`/api/ships/${selectedShip.symbol}/smuggling`, {
        action: 'configure_compartment'
      });
      
      await fetchSmugglingStatus();
      showNotification('Secret compartment configured successfully', 'success');
    } catch (error) {
      showNotification('Failed to configure secret compartment', 'error');
    } finally {
      setLoading(false);
    }
  };

  const hideCargoItem = async (symbol) => {
    if (!selectedShip || !symbol) return;
    
    setLoading(true);
    try {
      await axios.post(`/api/ships/${selectedShip.symbol}/smuggling`, {
        action: 'hide',
        cargo_symbol: symbol
      });
      
      await fetchCargo();
      await fetchSmugglingStatus();
      if (onShipUpdate) onShipUpdate(selectedShip);
      showNotification(`${symbol} hidden in secret compartment`, 'success');
    } catch (error) {
      showNotification('Failed to hide cargo', 'error');
    } finally {
      setLoading(false);
    }
  };

  const revealHiddenCargo = async () => {
    if (!selectedShip) return;
    
    setLoading(true);
    try {
      await axios.post(`/api/ships/${selectedShip.symbol}/smuggling`, {
        action: 'reveal'
      });
      
      await fetchCargo();
      await fetchSmugglingStatus();
      if (onShipUpdate) onShipUpdate(selectedShip);
      showNotification('Hidden cargo revealed', 'success');
    } catch (error) {
      showNotification('Failed to reveal hidden cargo', 'error');
    } finally {
      setLoading(false);
    }
  };

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const getCargoItem = (symbol) => {
    return cargo?.inventory?.find(item => item.symbol === symbol);
  };

  if (!selectedShip) {
    return (
      <div className="ship-actions-sidebar">
        <div className="sidebar-header">
          <h3>🚀 Ship Actions</h3>
        </div>
        <div className="sidebar-content">
          <p>Select a ship to view cargo operations</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`ship-actions-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <h3>🚀 {selectedShip.symbol}</h3>
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
          {notification && (
            <div className={`notification ${notification.type}`}>
              {notification.message}
            </div>
          )}

          {/* Tab Navigation */}
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'cargo' ? 'active' : ''}`}
              onClick={() => setActiveTab('cargo')}
            >
              📦 Cargo
            </button>
            <button 
              className={`tab ${activeTab === 'market' ? 'active' : ''}`}
              onClick={() => setActiveTab('market')}
            >
              🏪 Market
            </button>
            <button 
              className={`tab ${activeTab === 'advanced' ? 'active' : ''}`}
              onClick={() => setActiveTab('advanced')}
            >
              ⚡ Advanced
            </button>
          </div>

          {/* Cargo Tab */}
          {activeTab === 'cargo' && (
            <div className="tab-content">
              <div className="cargo-summary">
                <h4>Cargo Hold</h4>
                {cargo && (
                  <div className="cargo-stats">
                    <div>Capacity: {cargo.units}/{cargo.capacity}</div>
                    <div className="cargo-bar">
                      <div 
                        className="cargo-fill" 
                        style={{width: `${(cargo.units / cargo.capacity) * 100}%`}}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              {cargo?.inventory && cargo.inventory.length > 0 && (
                <div className="cargo-inventory">
                  <h5>Current Inventory</h5>
                  {cargo.inventory.map((item, index) => (
                    <div key={index} className="cargo-item-row">
                      <span className="item-symbol">{item.symbol}</span>
                      <span className="item-units">{item.units}</span>
                      <div className="item-actions">
                        <button onClick={() => setSellForm({...sellForm, symbol: item.symbol})}>Sell</button>
                        <button onClick={() => setJettisonForm({...jettisonForm, symbol: item.symbol})}>Jettison</button>
                        <button onClick={() => hideCargoItem(item.symbol)} disabled={loading}>Hide</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Sell Form */}
              <div className="action-section">
                <h5>💰 Sell Cargo</h5>
                <form onSubmit={handleSell}>
                  <select 
                    value={sellForm.symbol} 
                    onChange={(e) => setSellForm({...sellForm, symbol: e.target.value})}
                    required
                  >
                    <option value="">Select item to sell</option>
                    {cargo?.inventory?.map(item => (
                      <option key={item.symbol} value={item.symbol}>
                        {item.symbol} ({item.units} available)
                      </option>
                    ))}
                  </select>
                  <input 
                    type="number" 
                    min="1" 
                    max={getCargoItem(sellForm.symbol)?.units || 1}
                    value={sellForm.units}
                    onChange={(e) => setSellForm({...sellForm, units: e.target.value})}
                    placeholder="Units"
                    required
                  />
                  <button type="submit" disabled={loading || !market}>
                    {loading ? 'Selling...' : 'Sell'}
                  </button>
                </form>
                {!market && <small>⚠️ No market at current location</small>}
              </div>

              {/* Jettison Form */}
              <div className="action-section">
                <h5>🚨 Emergency Jettison</h5>
                <form onSubmit={handleJettison}>
                  <select 
                    value={jettisonForm.symbol} 
                    onChange={(e) => setJettisonForm({...jettisonForm, symbol: e.target.value})}
                    required
                  >
                    <option value="">Select item to jettison</option>
                    {cargo?.inventory?.map(item => (
                      <option key={item.symbol} value={item.symbol}>
                        {item.symbol} ({item.units} available)
                      </option>
                    ))}
                  </select>
                  <input 
                    type="number" 
                    min="1" 
                    max={getCargoItem(jettisonForm.symbol)?.units || 1}
                    value={jettisonForm.units}
                    onChange={(e) => setJettisonForm({...jettisonForm, units: e.target.value})}
                    placeholder="Units"
                    required
                  />
                  <button type="submit" disabled={loading} className="danger">
                    {loading ? 'Jettisoning...' : 'Jettison'}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Market Tab */}
          {activeTab === 'market' && (
            <div className="tab-content">
              {market ? (
                <>
                  <div className="action-section">
                    <h4>🏪 Local Market</h4>
                    <p>Location: {market.symbol}</p>
                  </div>

                  {/* Purchase Form */}
                  <div className="action-section">
                    <h5>🛒 Purchase Goods</h5>
                    <form onSubmit={handlePurchase}>
                      <select 
                        value={purchaseForm.symbol} 
                        onChange={(e) => setPurchaseForm({...purchaseForm, symbol: e.target.value})}
                        required
                      >
                        <option value="">Select item to purchase</option>
                        {market.tradeGoods?.map(good => (
                          <option key={good.symbol} value={good.symbol}>
                            {good.name} - {good.purchasePrice} credits
                          </option>
                        ))}
                      </select>
                      <input 
                        type="number" 
                        min="1" 
                        value={purchaseForm.units}
                        onChange={(e) => setPurchaseForm({...purchaseForm, units: e.target.value})}
                        placeholder="Units"
                        required
                      />
                      <button type="submit" disabled={loading}>
                        {loading ? 'Purchasing...' : 'Purchase'}
                      </button>
                    </form>
                  </div>

                  {/* Market Goods */}
                  {market.tradeGoods && (
                    <div className="market-goods">
                      <h5>Available Goods</h5>
                      {market.tradeGoods.map(good => (
                        <div key={good.symbol} className="market-item">
                          <div className="good-info">
                            <strong>{good.name}</strong>
                            <div className="good-prices">
                              Buy: {good.purchasePrice} | Sell: {good.sellPrice}
                            </div>
                            <div className="good-supply">Supply: {good.supply}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <div className="no-market">
                  <p>❌ No market available at current location</p>
                  <p>Navigate to a waypoint with a marketplace to trade goods</p>
                </div>
              )}
            </div>
          )}

          {/* Advanced Tab */}
          {activeTab === 'advanced' && (
            <div className="tab-content">
              <div className="action-section">
                <h4>⚡ Advanced Operations</h4>
                
                <div className="advanced-actions">
                  <button onClick={optimizeCargo} disabled={loading}>
                    🔧 Optimize Cargo
                  </button>
                  <button onClick={scanCargo} disabled={loading}>
                    🔍 Scan Cargo
                  </button>
                </div>
              </div>

              {/* Transfer Form */}
              <div className="action-section">
                <h5>🔄 Transfer Cargo</h5>
                <form onSubmit={handleTransfer}>
                  <select 
                    value={transferForm.symbol} 
                    onChange={(e) => setTransferForm({...transferForm, symbol: e.target.value})}
                    required
                  >
                    <option value="">Select item to transfer</option>
                    {cargo?.inventory?.map(item => (
                      <option key={item.symbol} value={item.symbol}>
                        {item.symbol} ({item.units} available)
                      </option>
                    ))}
                  </select>
                  <input 
                    type="number" 
                    min="1" 
                    max={getCargoItem(transferForm.symbol)?.units || 1}
                    value={transferForm.units}
                    onChange={(e) => setTransferForm({...transferForm, units: e.target.value})}
                    placeholder="Units"
                    required
                  />
                  <input 
                    type="text" 
                    value={transferForm.destination}
                    onChange={(e) => setTransferForm({...transferForm, destination: e.target.value})}
                    placeholder="Destination ship symbol"
                    required
                  />
                  <button type="submit" disabled={loading}>
                    {loading ? 'Transferring...' : 'Transfer'}
                  </button>
                </form>
              </div>

              {/* Smuggling Section */}
              <div className="action-section">
                <h5>🕵️ Smuggling Operations</h5>
                <div className="smuggling-info">
                  <p>🔒 Hidden compartments: {smugglingStatus?.hidden_compartments?.length || 0}/{smugglingStatus?.max_compartments || 2}</p>
                  <p>🎯 Stealth rating: {smugglingStatus?.stealth_rating || 0}%</p>
                  <p>⚠️ Detection risk: {smugglingStatus?.detection_risk || 'Unknown'}</p>
                  
                  {smugglingStatus?.hidden_compartments?.length > 0 && (
                    <div className="hidden-compartments">
                      <h6>Hidden Compartments:</h6>
                      {smugglingStatus.hidden_compartments.map((compartment, index) => (
                        <div key={index} className="compartment-info">
                          <p>Compartment {compartment.id}: {compartment.contents?.length || 0} items</p>
                          {compartment.contents?.map((item, itemIndex) => (
                            <span key={itemIndex} className="hidden-item">
                              {item.symbol}: {item.units}
                            </span>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="smuggling-actions">
                    <button 
                      onClick={configureSecretCompartment}
                      disabled={loading || (smugglingStatus?.hidden_compartments?.length >= smugglingStatus?.max_compartments)}
                    >
                      {loading ? 'Configuring...' : 'Configure Secret Compartment'}
                    </button>
                    
                    {smugglingStatus?.hidden_compartments?.some(c => c.contents?.length > 0) && (
                      <button 
                        onClick={revealHiddenCargo}
                        disabled={loading}
                        className="reveal-btn"
                      >
                        {loading ? 'Revealing...' : 'Reveal Hidden Cargo'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ShipActionsSidebar;