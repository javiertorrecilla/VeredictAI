import './Analizador.css';
import { useRef, useState, useEffect } from 'react';
import axios from 'axios';
import { FiUpload, FiSearch, FiRotateCw } from 'react-icons/fi';

export default function Analizador() {
  const [file, setFile] = useState(null);
  const [grafoUrl, setGrafoUrl] = useState(null);
  const [articulos, setArticulos] = useState([]);
  const [error, setError] = useState(null);
  const [popupTexto, setPopupTexto] = useState(null);
  const [zoom, setZoom] = useState(1);

  const imageRef = useRef(null);
  const visualRef = useRef(null);
  const overlayRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!popupTexto) return;

    const overlay = overlayRef.current;
    if (overlay) overlay.focus();

    const handleKey = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        setPopupTexto(null);
      }
      if (e.key === 'Tab') {
        e.preventDefault();
      }
    };

    overlay?.addEventListener('keydown', handleKey);
    return () => overlay?.removeEventListener('keydown', handleKey);
  }, [popupTexto]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      fileInputRef.current?.click();
    }
  };

  const actualizarOverflow = (nuevoZoom) => {
    const zoomLimitado = Math.max(1, Math.min(1.3, nuevoZoom));
    setZoom(zoomLimitado);
    if (visualRef.current) {
      visualRef.current.style.overflow = nuevoZoom > 1 ? 'auto' : 'visible';
    }
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setArticulos([]);
    setError(null);
    setGrafoUrl(null);
    setZoom(1);

    if (selected) {
      const reader = new FileReader();
      reader.onload = async () => {
        const rdfText = reader.result;
        setPopupTexto("Cargando imagen del grafo...");

        try {
          const data = new URLSearchParams();
          data.append("rdf", rdfText);
          data.append("formato", "xml");

          const response = await axios.post("https://veredictai.onrender.com/ver_grafo/", data, {
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            responseType: "blob"
          });

          const blobUrl = URL.createObjectURL(new Blob([response.data], { type: 'image/png' }));
          setGrafoUrl(blobUrl);
        } catch (err) {
          console.error(err);
          setError("No se pudo generar la imagen del grafo.");
        } finally {
          setPopupTexto(null);
        }
      };

      reader.readAsText(selected);
    }
  };

  const onImageLoad = () => {
    if (imageRef.current && visualRef.current) {
      const img = imageRef.current;
      const contenedor = visualRef.current;
      const zoomCalculado = contenedor.clientWidth / img.naturalWidth;
      const zoomInicial = Math.min(1, parseFloat(zoomCalculado.toFixed(2)));
      setZoom(1);
      contenedor.style.overflow = 'visible';
    }
  };

  const analizar = async () => {
    if (!file){
      alert("Por favor, selecciona un archivo RDF para analizar.");
      return;
    }

    setPopupTexto("Infiriendo artículo...");

    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post("https://veredictai.onrender.com/inferencias/", formData);
      setArticulos(res.data.articulos || []);
      setError(null);
    } catch {
      setError("No se pudo realizar la inferencia del grafo RDF.");
    } finally {
      setPopupTexto(null);
    }
  };

  return (
    <div className="analizador-wrapper">
      <h1 tabIndex="0">Visualización de grafo RDF</h1>
      <p className="subtitulo" tabIndex="0">
        Sube un archivo RDF para visualizar su grafo asociado.
      </p>

      <div className="pasos">
        <div className="paso" tabIndex="0"><span>1</span> Selecciona un archivo RDF válido</div>
        <div className="paso" tabIndex="0"><span>2</span> Muestra el grafo asociado al archivo RDF</div>
      </div>

      <div className="analizador-formulario">
        <input
          type="file"
          accept=".rdf"
          id="rdfInput"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <label
          htmlFor="rdfInput"
          className="btn archivo-btn"
          aria-label="Seleccionar archivo RDF para analizar"
          tabIndex="0"
          onKeyDown={handleKeyDown}
          style={{ display: 'inline-flex', alignItems: 'center', cursor: 'pointer' }}
        >
          <FiUpload style={{ marginRight: '6px' }} />
          Seleccionar archivo RDF
        </label>

        <button
          className="btn reiniciar-btn"
          onClick={() => window.location.reload()}
          aria-label="Analizar otro archivo RDF"
        >
          <FiRotateCw aria-hidden="true" style={{ marginRight: '6px' }} />
          Analizar otro RDF
        </button>
      </div>

      <div className="visualizacion" ref={visualRef}>
        {grafoUrl ? (
          <img
            ref={imageRef}
            src={grafoUrl}
            alt="Visualización del grafo RDF"
            className="grafo-scroll-zoom"
            onLoad={onImageLoad}
            style={{ width: `${zoom * 100}%`, height: 'auto' }}
          />
        ) : (
          <p className="grafotip" tabIndex="0">Selecciona un RDF para visualizar su grafo.</p>
        )}
      </div>

      {grafoUrl && (
        <div className="zoom-control">
          <button onClick={() => actualizarOverflow(Math.max(0.1, zoom - 0.1))} aria-label="Reducir zoom">−</button>
          <span>{zoom.toFixed(1)}x</span>
          <button onClick={() => actualizarOverflow(zoom + 0.1)} aria-label="Aumentar zoom">+</button>
        </div>
      )}

      {popupTexto && (
        <div
          className="popup-overlay"
          role="alertdialog"
          aria-modal="true"
          aria-live='polite'
          ref={overlayRef}
          tabIndex="-1"
        >
          <div className="popup-loader" aria-busy="true">
            <div className="spinner" />
            <p>{popupTexto}</p>
          </div>
        </div>
      )}
    </div>
  );
}
