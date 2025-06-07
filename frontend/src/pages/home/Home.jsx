import fondo from '../../assets/fondo.jpg';
import './Home.css';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="home" style={{ backgroundImage: `url(${fondo})` }}>
      <div className="overlay">
        <div className="home-content">
          <h1>Herramienta Jurídica Inteligente</h1>
          <p>
            Herramienta fiscal de apoyo que procesa atestados y grafos RDF para extraer automáticamente artículos jurídicos aplicables.
          </p>
          <div className="home-buttons">
            <Link to="/atestados" className="home-btn">
              Procesamiento de atestado con IA
            </Link>
            <Link to="/analizador" className="home-btn">
              Visualización de grafo e inferencia de artículo
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
