import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Fleet from './components/Fleet';
import Systems from './components/Systems';
import Factions from './components/Factions';
import Automation from './components/Automation';
import ShipActionsSidebar from './components/ShipActionsSidebar';
import './App.css';

function App() {
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
              <Route path="/fleet" element={<Fleet />} />
              <Route path="/systems" element={<Systems />} />
              <Route path="/factions" element={<Factions />} />
              <Route path="/automation" element={<Automation />} />
            </Routes>
          </div>
        </main>

        <ShipActionsSidebar />
      </div>
    </Router>
  );
}

export default App;
