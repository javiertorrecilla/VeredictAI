// frontend/src/App.jsx
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/home/Home';
import Analizador from './pages/analizador/Analizador';
import Atestados from './pages/atestados/Atestados';
import { Routes, Route } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <div className="app-wrapper">
      <Navbar />
      <main className="main-hero">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/atestados" element={<Atestados />} />
          <Route path='/analizador' element={<Analizador />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
