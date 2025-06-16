import os
import fitz  # PyMuPDF
from docx import Document

def leer_pdf(ruta_archivo):
    """Lee un archivo PDF y devuelve su texto."""
    if not os.path.exists(ruta_archivo):
        return "Archivo no encontrado."
    try:
        with fitz.open(ruta_archivo) as documento:
            texto = "".join([pagina.get_text() for pagina in documento])
        return texto.strip() or "El PDF no contiene texto."
    except Exception as e:
        return f"Error al leer el archivo PDF: {e}"

def leer_docx(ruta_archivo):
    """Lee un archivo DOCX y devuelve su texto."""
    if not os.path.exists(ruta_archivo):
        return "Archivo no encontrado."
    try:
        documento = Document(ruta_archivo)
        texto = "\n".join([parrafo.text for parrafo in documento.paragraphs])
        return texto.strip() or "El DOCX no contiene texto."
    except Exception as e:
        return f"Error al leer el archivo DOCX: {e}"
