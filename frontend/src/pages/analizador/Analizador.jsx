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
  // Ref to control focus on the popup overlay
  const overlayRef = useRef(null);

  // When the popup is visible, focus it and trap keyboard navigation.
  useEffect(() => {
    if (!popupTexto) return;

    const overlay = overlayRef.current;
    if (overlay) overlay.focus();

    const handleKey = (e) => {
      if (e.key === 'Escape') {
        // Allow the user to cancel the loading overlay with Esc
        e.preventDefault();
        setPopupTexto(null);
      }
      if (e.key === 'Tab') {
        // Keep focus within the overlay while it's visible
        e.preventDefault();
      }
    };

    overlay?.addEventListener('keydown', handleKey);
    return () => overlay?.removeEventListener('keydown', handleKey);
  }, [popupTexto]);

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
    if (!file) return;
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
      <h1>Análisis e Inferencia Jurídica</h1>
      <p className="subtitulo">Sube un archivo RDF para visualizar su grafo y obtener artículos inferidos automáticamente.</p>

      <div className="pasos">
        <div className="paso"><span>1</span> Selecciona un archivo RDF válido</div>
        <div className="paso"><span>2</span> Muestra el grafo asociado al archivo RDF</div>
        <div className="paso"><span>3</span> Analiza e infiere un artículo en base al grafo RDF</div>
      </div>

      <div className="analizador-formulario">
        <label className="btn archivo-btn">
          <FiUpload style={{ marginRight: '6px' }} />
          Seleccionar archivo RDF
          <input type="file" accept=".rdf" onChange={handleFileChange} hidden />
        </label>

        <button className="btn analizar-btn" onClick={analizar} disabled={!file}>
          <FiSearch style={{ marginRight: '6px' }} />
          Analizar RDF
        </button>

        <button className="btn reiniciar-btn" onClick={() => window.location.reload()}>
          <FiRotateCw style={{ marginRight: '6px' }} />
          Analizar otro RDF
        </button>
      </div>

      <div className="visualizacion" ref={visualRef}>
        {grafoUrl ? (
          <img
            ref={imageRef}
            src={grafoUrl}
            alt="Visualización del Grafo"
            className="grafo-scroll-zoom"
            onLoad={onImageLoad}
            style={{ width: `${zoom * 100}%`, height: 'auto' }}
          />
        ) : (
          <p className="grafotip">Selecciona un RDF para visualizar su grafo.</p>
        )}
      </div>

      {grafoUrl && (
        <div className="zoom-control">
          <button onClick={() => actualizarOverflow(Math.max(0.1, zoom - 0.1))}>−</button>
          <span>{zoom.toFixed(1)}x</span>
          <button onClick={() => actualizarOverflow(zoom + 0.1)}>+</button>
        </div>
      )}

      <div className="resultado">
        <h3>Artículos Inferidos:</h3>
        {articulos.length > 0 ? (
          <ul>
            {articulos.map((texto, i) => (
              <li key={i}>{texto}</li>
            ))}
          </ul>
        ) : (
          <p>No hay artículos inferidos.</p>
        )}
        {error && <p className="error">{error}</p>}
      </div>

      {popupTexto && (
        /* Loading overlay. Focus is trapped and Esc closes it. */
        <div
          className="popup-overlay"
          role="alertdialog"
          aria-modal="true"
          ref={overlayRef}
          tabIndex="-1"
        >
          <div className="popup-loader">
            <div className="spinner" />
            <p>{popupTexto}</p>
          </div>
        </div>
      )}
    </div>
  );
}
