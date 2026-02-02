import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Cards from './pages/Cards';
import Categories from './pages/Categories';
import Merchants from './pages/Merchants';
import Settings from './pages/Settings';
import SimpleView from './pages/SimpleView';

function Navigation() {
  const location = useLocation();

  // Don't show navigation on simple view
  if (location.pathname === '/simple') {
    return null;
  }

  return (
    <nav className="nav">
      <div className="nav-content">
        <h1>Card Optimizer</h1>
        <div className="nav-links">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            Dashboard
          </Link>
          <Link to="/cards" className={location.pathname === '/cards' ? 'active' : ''}>
            Cards
          </Link>
          <Link to="/categories" className={location.pathname === '/categories' ? 'active' : ''}>
            Categories
          </Link>
          <Link to="/merchants" className={location.pathname === '/merchants' ? 'active' : ''}>
            Merchants
          </Link>
          <Link to="/settings" className={location.pathname === '/settings' ? 'active' : ''}>
            Settings
          </Link>
          <Link to="/simple" className={location.pathname === '/simple' ? 'active' : ''}>
            Simple View
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <Navigation />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/cards" element={<Cards />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/merchants" element={<Merchants />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/simple" element={<SimpleView />} />
      </Routes>
    </Router>
  );
}

export default App;
