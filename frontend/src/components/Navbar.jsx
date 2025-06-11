import './Navbar.css';
import logo from '../assets/logo.png';
import { NavLink, Link } from 'react-router-dom';
import { useState } from 'react';
import { FiMenu, FiX } from 'react-icons/fi';

export default function Navbar() {
  const [open, setOpen] = useState(false);
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-left" style={{ textDecoration: 'none', color: 'inherit' }}>
          <img src={logo} alt="Logo" className="navbar-logo" />
          <h2 className="navbar-title">VeredictAI</h2>
        </Link>
        <button className="navbar-toggle" onClick={() => setOpen(!open)}>
          {open ? <FiX /> : <FiMenu />}
        </button>
        <ul className={`navbar-menu ${open ? 'open' : ''}`}>
          <li>
            <NavLink
              to="/atestados"
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              Procesamiento de Atestado
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/analizador"
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              Visualización e inferencia
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
}
