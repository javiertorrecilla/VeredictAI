import os
import fitz  
from docx import Document 

# Funcion para leer PDF
def leer_pdf(ruta_archivo):
    """Lee un archivo PDF y devuelve su texto."""
    try:
        with fitz.open(ruta_archivo) as documento:
            return "".join([pagina.get_text() for pagina in documento])
    except Exception as e:
        return f"Error al leer el archivo PDF: {e}"

# Funcion para leer DOCX
def leer_docx(ruta_archivo):
    """Lee un archivo DOCX y devuelve su texto."""
    try:
        documento = Document(ruta_archivo)
        return "\n".join([parrafo.text for parrafo in documento.paragraphs])
    except Exception as e:
        return f"Error al leer el archivo DOCX: {e}"

