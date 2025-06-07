from typing import List, Literal, Optional
from openai import OpenAI
from pydantic import BaseModel, validator

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/javiertorrecilla/Desktop/UMA/TFG/herramientaJuridica/.env")

apiKey = os.getenv("api_key")
url = os.getenv("base_url")

client = OpenAI(
    api_key=apiKey,
    base_url=url
)

## Clase Bien que representa los bienes robados con nombre y caracteristica especia si tuviera
class Bien(BaseModel):
    nombre: str
    caracteristicas_especiales: List[Literal[
        'Bien relacionado con la agricultura o ganadería',
        'Bien artístico',
        'Bien con valor cultural',
        'Bien esencial cuyo robo causa perjuicios graves',
        'Bien con valor histórico',
        'Cableado de servicios',
        'Elemento de suministro eléctrico',
        'Infraestructura de interés general',
        'Componente relacionado con hidrocarburos',
        'Infraestructura de telecomunicaciones',
        'Tubería de servicios',
        'Bien con valor científico',
    ]] = []

    def as_key(self) -> str:
        if self.caracteristicas_especiales:
            return f"{self.nombre}|{'|'.join(sorted(self.caracteristicas_especiales))}"
        return self.nombre

## Clase Atestado que representa un atestado con sus campos y carcteristicas
class AtestadoModel(BaseModel):
    atestado_id: str
    victima_id: str
    acusado_id: str
    testigos_id: List[str] = [] ## todo: Revisar si poner o no los identificativos o un string autoexplicativo
    empresas_id: List[str] = [] ## todo: Revisar si poner o no los identificativos o un string autoexplicativo
    bienes_robados: List[Bien]
    valor_total_robado: float = 0.0
    caracteristicas_del_delito: List[Literal[
        'Allanamiento de morada',
        'Desactivación de alarmas durante el robo',
        'Entrada forzada a un inmueble',
        'Forzamiento de cerraduras',
        'Llaves copiadas ilegalmente',
        'Uso de llaves perdidas por el dueño',
        'Dispositivos electrónicos para abrir cerraduras',
        'Llaves robadas previamente',
        'Rotura o acceso ilegal a una vivienda o local',
        'Intimidacion',
        'Violencia',
        'Amenaza',
        'Robo con uso de intimidación o violencia explícita',
        'Acceso ilegal a un lugar sin autorización'
    ]] = []
    factores_agravantes: List[Literal[
        'Acusado vinculado a una organización criminal',
        'Acusado que involucra a menores de 16 años como cómplices',
        'Acusado con antecedentes penales graves (más de 3 condenas previas)'
    ]] = []
    factores_mitigantes: List[Literal[
        'Uso limitado de intimidación o violencia durante el delito'
    ]] = []    
    efectos_del_delito: List[Literal[
        'Impacto económico en la víctima',
        'Situación de vulnerabilidad de la víctima durante el delito',
        'Daño físico o psicológico infligido a la víctima'
    ]] = []
    antecedentes: Literal['sí', 'no'] = 'no'

def extraer_datos(texto):

    completion = client.beta.chat.completions.parse(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": "Extrae la información del atestado"},
            {"role": "user", "content": texto},
        ],
        response_format=AtestadoModel,
    )

    res = completion.choices[0].message.parsed
    return res
