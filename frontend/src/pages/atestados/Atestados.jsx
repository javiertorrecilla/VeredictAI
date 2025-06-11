import './Atestados.css';
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FiUpload, FiTrash2, FiDownload, FiLoader } from 'react-icons/fi';
import docs from '../../assets/docs.png';
import noArchivo from '../../assets/noArchivo.png';

export default function Atestados() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [popup, setPopup] = useState(false);
  const [error, setError] = useState(null);
  const overlayRef = useRef(null);

  useEffect(() => {
    if (!popup) return;

    const overlay = overlayRef.current;
    if (overlay) overlay.focus();

    const handleKey = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        setPopup(false);
      }
      if (e.key === 'Tab') {
        e.preventDefault();
      }
    };

    overlay?.addEventListener('keydown', handleKey);
    return () => overlay?.removeEventListener('keydown', handleKey);
  }, [popup]);

  const handleChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setResultado(null);
    setError(null);

    if (!selected) {
      setPreviewUrl(null);
      return;
    }

    if (selected.type === 'application/pdf') {
      setPreviewUrl(URL.createObjectURL(selected));
    } else {
      setPreviewUrl(null);
    }
  };

  const eliminarArchivo = () => {
    setFile(null);
    setPreviewUrl(null);
    setResultado(null);
    setError(null);
  };

  const procesar = async () => {
    setPopup(true);
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const res = await axios.post("https://veredictai.onrender.com/procesar/", formData);
      setResultado(res.data); 
      setError(null);
    } catch (err) {
      setError("Error al procesar el documento.");
    } finally {
      setLoading(false);
      setPopup(false);
    }
  };

  const descargarRDF = async () => {
    if (!resultado) {
      alert("Primero debes procesar un archivo.");
      return;
    }
  
    try {
      const res = await axios.post("https://veredictai.onrender.com/generar_rdf/", resultado, {
        responseType: 'blob'
      });
  
      const blob = new Blob([res.data], { type: 'application/xml' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'atestado.rdf';
      link.click();
    } catch {
      alert("No se pudo generar el archivo RDF.");
    }
  };

  return (
    <div className="atestados-wrapper">
      <h1 tabIndex="0">Procesamiento de Atestado</h1>
      <p className="subtitulo" tabIndex="0">Carga un atestado en formato PDF o DOCX y obtén su interpretación semántica.</p>

      <div className="pasos">
        <div className="paso" tabIndex="0"><span>1</span> Selecciona un archivo válido</div>
        <div className="paso" tabIndex="0"><span>2</span> Procesa el contenido con IA</div>
        <div className="paso" tabIndex="0"><span>3</span> Muestra los resultados y descarga el grafo</div>
      </div>

      <div className="procesamiento-grid">
        <div className="entrada">
          <div className="selector-box">
            <div className="preview" aria-label="Vista previa del archivo" role="region">
              {previewUrl ? (
                <embed src={previewUrl} type="application/pdf" title="Previsualización PDF" />
              ) : file && file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ? (
                <img src={docs} alt="Documento Word cargado" />
              ) : (
                <img src={noArchivo} alt="Ningún archivo seleccionado" />
              )}
            </div>
            <div className="archivo-info">
              <p tabIndex="0"><strong>{file ? file.name : 'No hay archivo seleccionado'}</strong></p>
              <p style={{ fontSize: '0.8rem', color: '#888' }} tabIndex="0">Recomendado: PDF para previsualización directa</p>

              <label className="btn archivo-btn" aria-label="Seleccionar archivo para procesar">
                <FiUpload aria-hidden="true" style={{ marginRight: '6px' }} />
                Seleccionar archivo
                <input type="file" accept=".pdf,.docx" onChange={handleChange} hidden />
              </label>

              {file && (
                <button className="eliminar-btn" onClick={eliminarArchivo} aria-label="Eliminar archivo seleccionado">
                  <FiTrash2 aria-hidden="true" style={{ marginRight: '4px' }} />
                  Eliminar
                </button>
              )}
            </div>
          </div>

          <button
            className="btn procesar-btn"
            onClick={procesar}
            disabled={!file}
            aria-label="Procesar el documento cargado"
          >
            <FiLoader aria-hidden="true" style={{ marginRight: '6px' }} />
            Procesar
          </button>
        </div>

        <div className="resultado" aria-live="polite" role="region">
          <h3 tabIndex="0">Resultado:</h3>
          {resultado ? (
            <>
              <p><strong>Descripción:</strong></p>
              <p tabIndex="0">
                {typeof resultado === "string"
                  ? resultado
                  : resultado.descripcion || "No se pudo generar descripción en lenguaje natural."}
              </p>

              <details style={{ marginTop: '1rem' }}>
                <summary tabIndex="0">Ver datos completos</summary>
                <pre style={{ marginTop: '0.5rem' }}>
                  {JSON.stringify(resultado, null, 2)}
                </pre>
              </details>
            </>
          ) : (
            <p tabIndex="0">No se ha procesado ningún documento aún.</p>
          )}

          <button className="btn descargar-btn" onClick={descargarRDF} aria-label="Descargar grafo RDF">
            <FiDownload aria-hidden="true" style={{ marginRight: '6px' }} />
            Descargar grafo
          </button>
          {error && <p className="error" tabIndex="0">{error}</p>}
        </div>
      </div>

      {popup && (
        <div
          className="popup-overlay"
          role="alertdialog"
          aria-modal="true"
          aria-live="polite"
          ref={overlayRef}
          tabIndex="-1"
        >
          <div className="popup-loader" aria-busy="true">
            <div className="spinner" />
            <p>Procesando documento...</p>
          </div>
        </div>
      )}
    </div>
  );
}
