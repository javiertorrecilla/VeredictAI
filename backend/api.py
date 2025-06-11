import tempfile
from fastapi import APIRouter, FastAPI, File, Form, Response, UploadFile
from platformdirs import user_downloads_path
import urllib
from rdfFile import crear_rdf, filtrar_grafo
from entities import Atestado
import decisionTree
from atestadoToText import generar_descripcion
from fastapi.responses import StreamingResponse
from documents import leer_pdf, leer_docx
import os
import requests
from reasonerFromFile import reasoner, construir_articulos_inferidos
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de api para procesar atestados
@app.post("/procesar/")
async def procesar_atestado(file: UploadFile):
    """Procesa un atestado subido por el usuario.

    Lee el archivo proporcionado (PDF o DOCX), lo envía al árbol de
    decisión basado en LLM y, si procede, genera una descripción
    resumida del atestado.

    Parameters
    ----------
    file: UploadFile
        Archivo que contiene el atestado en formato PDF o DOCX.

    Returns
    -------
    dict | str
        Diccionario con los datos del ``Atestado`` y su descripción o
        un mensaje de error/estado en caso de que no se determine un
        atestado válido.
    """
    try:
        extension = os.path.splitext(file.filename)[1].lower()
        contenido = await file.read()

        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contenido)

        if extension == ".pdf":
            texto = leer_pdf(temp_path)
        elif extension == ".docx":
            texto = leer_docx(temp_path)
        else:
            return {"error": "Formato de archivo no soportado. Usa PDF o DOCX."}

        resultado = decisionTree.delitoPropiedad(decisionTree.AtestadoLLM(texto))

        if isinstance(resultado, Atestado):
            descripcion = generar_descripcion(resultado)
        else:
            descripcion = resultado

        print(f"Descripción generada: {descripcion}")

        if isinstance(resultado, Atestado):
            resultado_dict = resultado.model_dump()
            resultado_dict["descripcion"] = descripcion
            print(f"Resultado del procesamiento: {resultado_dict}")
            return resultado_dict
        else:
            resultado_str = str(resultado)
            print(f"Resultado del procesamiento: {resultado_str}")
            return resultado_str

    except Exception as e:
        return {"error": str(e)}

# Ruta de api para generar RDF a partir de un atestado
@app.post("/generar_rdf/")
async def generar_rdf(atestado: Atestado):
    """Crear y devolver un fichero RDF para el ``Atestado`` recibido.

    Parameters
    ----------
    atestado: Atestado
        Datos estructurados del atestado a convertir en RDF.

    Returns
    -------
    StreamingResponse | dict
        Respuesta con el archivo RDF listo para descargar o un
        diccionario con información de error si algo falla.
    """
    try:
        nombre_archivo = crear_rdf(atestado)

        ruta_completa = os.path.join(user_downloads_path(), nombre_archivo)
        rdf_file = open(ruta_completa, "rb")

        return StreamingResponse(
            rdf_file,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
        )

    except Exception as e:
        return {"error": str(e)}

# Ruta de api para visualizar el grafo RDF
@app.post("/ver_grafo/")
async def ver_grafo(rdf: str = Form(...), formato: str = Form(default="xml")):
    """Devuelve una imagen PNG representando el grafo RDF recibido.

    Parameters
    ----------
    rdf: str
        Texto RDF en el formato indicado.
    formato: str
        Formato del RDF proporcionado. Por defecto ``"xml"``.

    Returns
    -------
    Response | dict
        Imagen PNG del grafo o diccionario con mensaje de error.
    """
    try:
        grafo_filtrado = filtrar_grafo(rdf, formato=formato)
        rdf_filtrado = grafo_filtrado.serialize(format=formato)

        encoded_rdf = urllib.parse.quote_plus(rdf_filtrado)

        body = f"rdf={encoded_rdf}&from={formato}&to=png"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        res = requests.post(
            "https://www.ldf.fi/service/rdf-grapher",
            data=body,
            headers=headers,
            timeout=10
        )

        if res.status_code != 200:
            return {"error": f"ldf.fi devolvió {res.status_code}"}

        return Response(content=res.content, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
    
# Ruta de api para inferencias RDF
@app.post("/inferencias/")
async def inferencias(file: UploadFile = File(...)):
    """Ejecuta inferencias OWL sobre el RDF subido y devuelve artículos.

    Parameters
    ----------
    file: UploadFile
        Archivo RDF que contiene el grafo a analizar.

    Returns
    -------
    dict
        Diccionario con la lista de artículos inferidos a partir de las
        clases OWL obtenidas.
    """
    contenido = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".rdf") as tmp:
        tmp.write(contenido)
        tmp_path = tmp.name

    clases_inferidas = reasoner(tmp_path)
    articulos = construir_articulos_inferidos(clases_inferidas)
    
    return {"articulos": articulos}

