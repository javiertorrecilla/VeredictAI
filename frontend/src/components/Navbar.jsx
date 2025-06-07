import './Navbar.css';
import logo from '../assets/logo.png';
import { NavLink, Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-left" style={{ textDecoration: 'none', color: 'inherit' }}>
          <img src={logo} alt="Logo" className="navbar-logo" />
          <h2 className="navbar-title">VeredictAI</h2>
        </Link>
        <ul className="navbar-menu">
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
