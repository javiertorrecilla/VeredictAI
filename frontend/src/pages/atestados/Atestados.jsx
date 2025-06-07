import './Atestados.css';
import { useState } from 'react';
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
      const res = await axios.post("http://localhost:8000/procesar/", formData);
      setResultado(res.data); 
      console.log("Resultado del procesamiento:", res.data);
      console.log(resultado);
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
      const res = await axios.post("http://localhost:8000/generar_rdf/", resultado, {
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
      <h1>Procesamiento de Atestado</h1>
      <p className="subtitulo">Carga un atestado en formato PDF o DOCX y obtén su interpretación semántica.</p>

      <div className="pasos">
        <div className="paso"><span>1</span> Selecciona un archivo válido</div>
        <div className="paso"><span>2</span> Procesa el contenido con IA</div>
        <div className="paso"><span>3</span> Muestra los resultados y descarga el grafo</div>
      </div>

      <div className="procesamiento-grid">
        <div className="entrada">
          <div className="selector-box">
            <div className="preview">
              {previewUrl ? (
                <embed src={previewUrl} type="application/pdf" />
              ) : file && file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ? (
                <img src={docs} alt="Vista DOCX" />
              ) : (
                <img src={noArchivo} alt="Sin archivo" />
              )}
            </div>
            <div className="archivo-info">
              <p><strong>{file ? file.name : 'No hay archivo seleccionado'}</strong></p>
              <p style={{ fontSize: '0.8rem', color: '#888' }}>Recomendado: PDF para previsualización directa</p>
              <label className="btn archivo-btn">
                <FiUpload style={{ marginRight: '6px' }} />
                Seleccionar archivo
                <input type="file" accept=".pdf,.docx" onChange={handleChange} hidden />
              </label>
              {file && (
                <button className="eliminar-btn" onClick={eliminarArchivo}>
                  <FiTrash2 style={{ marginRight: '4px' }} />
                  Eliminar
                </button>
              )}
            </div>
          </div>

          <button className="btn procesar-btn" onClick={procesar} disabled={!file}>
            <FiLoader style={{ marginRight: '6px' }} />
            Procesar
          </button>
        </div>

        <div className="resultado">
          <h3>Resultado:</h3>
          {resultado ? (
            <>
              <p><strong>Descripción:</strong></p>
              <p>
                {typeof resultado === "string"
                  ? resultado
                  : resultado.descripcion || "No se pudo generar descripción en lenguaje natural."}
              </p>

              <details style={{ marginTop: '1rem' }}>
                <summary>Ver datos completos</summary>
                <pre style={{ marginTop: '0.5rem' }}>
                  {JSON.stringify(resultado, null, 2)}
                </pre>
              </details>
            </>
          ) : (
            <p>No se ha procesado ningún documento aún.</p>
          )}

          <button className="btn descargar-btn" onClick={descargarRDF}>
            <FiDownload style={{ marginRight: '6px' }} />
            Descargar grafo
          </button>
          {error && <p className="error">{error}</p>}
        </div>
      </div>

      {popup && (
        <div className="popup-overlay">
          <div className="popup-loader">
            <div className="spinner" />
            <p>Procesando documento...</p>
          </div>
        </div>
      )}
    </div>
  );
}
