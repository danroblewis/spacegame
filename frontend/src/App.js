import React, { createContext, useContext, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Fleet from './components/Fleet';
import Systems from './components/Systems';
import Factions from './components/Factions';
import ShipActionsSidebar from './components/ShipActionsSidebar';
import './App.css';

// Create ship context
const ShipContext = createContext();

export const useShip = () => {
  const context = useContext(ShipContext);
  if (!context) {
    throw new Error('useShip must be used within a ShipProvider');
  }
  return context;
};

function App() {
  const [selectedShip, setSelectedShip] = useState(null);

  const updateSelectedShip = (ship) => {
    setSelectedShip(ship);
  };

  return (
    <ShipContext.Provider value={{ selectedShip, updateSelectedShip }}>
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
                <li><Link to="/systems">Systems</Link></li>
                <li><Link to="/factions">Factions</Link></li>
              </ul>
            </div>
          </nav>

          <main className="main-content">
            <div className="container">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/fleet" element={<Fleet />} />
                <Route path="/systems" element={<Systems />} />
                <Route path="/factions" element={<Factions />} />
              </Routes>
            </div>
          </main>

          <ShipActionsSidebar />
        </div>
      </Router>
    </ShipContext.Provider>
  );
}

export default App;
