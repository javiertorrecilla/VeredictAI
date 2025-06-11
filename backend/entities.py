from decimal import Decimal, InvalidOperation
import re
from typing import List
from pydantic import BaseModel


class Bien(BaseModel):
    nombre: str
    caracteristicas_especiales: List[str] = []
    propietario: str = ""
    usuario: str = ""

class Acusado(BaseModel):
    id: str
    edad: int = 0
    organizacion_criminal: str = ""
    antecedentes: int = 0
    caracteristicas_acusado: List[str] = []

class Victima(BaseModel):
    id: str
    efectos_del_delito: List[str] = []

class Atestado(BaseModel):
    atestado_id: str
    victimas: List[Victima]
    autores: List[Acusado]
    complices: List[Acusado] = []
    testigos: List[str] = []
    empresas: List[str] = []
    bienes_robados: List[Bien]
    valor_total_robado: float = 0.0
    caracteristicas_del_delito: List[str] = []
    factores_agravantes: List[str] = []
    factores_mitigantes: List[str] = []

def initBienes(nombres: List[str]) -> List[Bien]:
    """Crea objetos ``Bien`` a partir de una lista de nombres."""
    return [Bien(nombre=nombre) for nombre in nombres]

def initAcusados(ids: List[str]) -> List[Acusado]:
    """Inicializa instancias de ``Acusado`` para los identificadores dados."""
    return [Acusado(id=id) for id in ids]

def initVictimas(ids: List[str]) -> List[Victima]:
    """Devuelve una lista de ``Victima`` basándose en sus identificadores."""
    return [Victima(id=id) for id in ids]

def initAtestado(atestado_id: str, bienes: List[Bien], victimas: List[Victima], autores: List[Acusado]) -> Atestado:
    """Construye un objeto ``Atestado`` con sus elementos principales."""
    return Atestado(
        atestado_id=atestado_id,
        bienes_robados=bienes,
        victimas=victimas,
        autores=autores
    )

def filtrar_bienes(lista):
    """Elimina nombres que hagan referencia a dinero de una lista de bienes."""
    patron = re.compile(r'\b(euro\w*|billete\w*|moneda\w*)\b', re.IGNORECASE)
    return [item for item in lista if not patron.search(item)]
