import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Fleet from './components/Fleet';
import Systems from './components/Systems';
import Factions from './components/Factions';
import Intelligence from './components/Intelligence';
import Crew from './components/Crew';
import Automation from './components/Automation';
import ResourceManagement from './components/ResourceManagement';
import ShipActionsSidebar from './components/ShipActionsSidebar';
import './App.css';

function App() {
  const [selectedShip, setSelectedShip] = useState(null);

  const handleShipSelect = (ship) => {
    setSelectedShip(ship);
  };

  const handleShipUpdate = (updatedShip) => {
    setSelectedShip(updatedShip);
  };

  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="container">
            <div className="nav-brand">
              <h1>🚀 SpaceTraders GUI</h1>
            </div>
            <ul className="nav-links">
              <li><Link to="/">Dashboard</Link></li>
              <li><Link to="/fleet">Fleet</Link></li>
              <li><Link to="/crew">Crew</Link></li>
              <li><Link to="/intelligence">Intelligence</Link></li>
              <li><Link to="/resources">Resources</Link></li>
              <li><Link to="/systems">Systems</Link></li>
              <li><Link to="/factions">Factions</Link></li>
              <li><Link to="/automation">🔄 Automation</Link></li>
            </ul>
          </div>
        </nav>

        <main className="main-content">
          <div className="container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route 
                path="/fleet" 
                element={
                  <Fleet 
                    selectedShip={selectedShip}
                    onShipSelect={handleShipSelect}
                    onShipUpdate={handleShipUpdate}
                  />
                } 
              />
              <Route path="/crew" element={<Crew />} />
              <Route path="/intelligence" element={<Intelligence />} />
              <Route path="/resources" element={<ResourceManagement />} />
              <Route path="/systems" element={<Systems />} />
              <Route path="/factions" element={<Factions />} />
              <Route path="/automation" element={<Automation />} />
            </Routes>
          </div>
        </main>

        <ShipActionsSidebar 
          selectedShip={selectedShip} 
          onShipUpdate={handleShipUpdate} 
        />
      </div>
    </Router>
  );
}

export default App;
