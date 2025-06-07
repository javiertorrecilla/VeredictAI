from decimal import Decimal
from itertools import combinations
from time import sleep
import time
from typing import List
from openai import OpenAI
import entities
import questions
from dotenv import load_dotenv
import os

# ---- Inicializar LLM ----
load_dotenv()

apiKey = os.getenv("OPENAI_API_KEY")
url = os.getenv("gpt-url")

client = OpenAI(
    api_key=apiKey,
    base_url=url
)

# ---- Clase para manejar el contexto del atestado y las preguntas al modelo LLM ----
class AtestadoLLM:

    cont = 0

    def __init__(self, contexto_atestado: str):
        self.contexto_atestado = contexto_atestado
        self.mensajes = [
            {"role": "system", "content":
             f"Eres un asistente jurídico. "
             f"Tienes que extraer información del siguiente atestado:\n\n{contexto_atestado}"}
        ]

    def preguntar(self, pregunta: str) -> str:
        AtestadoLLM.cont += 1
        sleep(4) 
        self.mensajes.append({"role": "user", "content": pregunta})
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=self.mensajes,
            temperature=0.2,
            top_p=1.0,
            max_tokens=1024,
        )
        respuesta = completion.choices[0].message.content.strip()
        self.mensajes.append({"role": "assistant", "content": respuesta})
        return respuesta

# ---- Función principal del árbol de decisión de delito contra la propiedad ----
def delitoPropiedad(atestado_llm: AtestadoLLM):
    delitoContraPropiedad = atestado_llm.preguntar(questions.DELITO_CONTRA_PROPIEDAD)
    if delitoContraPropiedad.lower().startswith("no"):
        return "No se estudia como delito contra la propiedad."
    
    print("Obteniendo número de atestado...")
    atestado_id = atestado_llm.preguntar(questions.NUM_ATESTADO)
    atestado_id = atestado_id.strip()
    atestado_id = atestado_id.replace("/","_")
    print("Obteniendo los bienes robados...")
    nombres_bienes = atestado_llm.preguntar(questions.NOMBRES_BIENES)
    nombres_bienes = [bien.strip() for bien in nombres_bienes.split(",") if bien.strip()]
    nombres_bienes = entities.filtrar_bienes(nombres_bienes)
    bienesRobados = entities.initBienes(nombres_bienes)

    victimas_res =[]
    print("Obteniendo víctimas...")
    victimaId = atestado_llm.preguntar(questions.VICTIMAS_BIENES)
    victimaId = [victima.strip() for victima in victimaId.split(",") if victima.strip()]
    victimas = entities.initVictimas(victimaId)

    for victima in victimas:
        victimas_res.append(victima)

    victimaId = atestado_llm.preguntar(questions.OTRAS_VICTIMAS)
    victimaId = [victima.strip() for victima in victimaId.split(",") if victima.strip()]
    if not victimaId[0].lower().startswith("no"):   
        victimas = entities.initVictimas(victimaId)

    for victima in victimas:
        if victima not in victimas_res:
            victimas_res.append(victima)

    victimas_def = victimas_res.copy()
    if len(victimas_res) > 1:
        for v1, v2 in combinations(victimas_res,2):
            iguales = atestado_llm.preguntar(questions.MISMA_PERSONA.format(p1=v1, p2=v2))
            if iguales.lower() == "sí":
                victimas_def.remove(v2)
    
    print("Obteniendo acusados...")
    acusadoId = atestado_llm.preguntar(questions.ACUSADOS_BIENES)
    acusadoId = [acusado.strip() for acusado in acusadoId.split(",") if acusado.strip()]
    acusados = entities.initAcusados(acusadoId)

    acusados_def = acusados.copy()
    if len(acusados_def) > 1:
        for v1, v2 in combinations(acusados,2):
            iguales = atestado_llm.preguntar(questions.MISMA_PERSONA.format(p1=v1, p2=v2))
            if iguales.lower() == "sí":
                acusados_def.remove(v2)

    atestado = entities.initAtestado(
        atestado_id=atestado_id,
        bienes=bienesRobados,
        victimas=victimas_def,
        autores=acusados_def
    )

    obtencionComplices(atestado_llm, atestado)

    roboOHurto = atestado_llm.preguntar(questions.ROBO_O_HURTO)
    print(roboOHurto)
    if roboOHurto.lower().startswith("no"):
        return procesar_hurto(atestado_llm, atestado)
    elif roboOHurto.lower().startswith("sí"):
        return procesar_robo(atestado_llm, atestado)
    else:
        return "Respuesta no válida para la naturaleza del delito."

# ---- Función para procesar tipo de hurto ----
def procesar_hurto(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    hurtoPropietario = atestado_llm.preguntar(questions.HURTO_PROPIETARIO)

    obtencionUsuarios(atestado_llm, atestado)

    if hurtoPropietario.lower() == 'sí':
        for autor in atestado.autores:
            for bien in atestado.bienes_robados:
                if bien.propietario == "":
                    propietario = atestado_llm.preguntar(questions.PROPIETARIO_ESPECIFICO.format(persona=autor.id, bien=bien.nombre))
                    if propietario.lower() == "sí":
                        bien.propietario = autor
        return procesarHurtoPropietario(atestado_llm, atestado)

    elif hurtoPropietario.lower() == 'no':   
        for bien in atestado.bienes_robados:
            if bien.propietario == "":
                propietario = atestado_llm.preguntar(questions.PROPIETARIO_GENERAL.format(bien=bien.nombre))
                bien.propietario = propietario
        return procesarHurtoNoPropietario(atestado_llm, atestado)

    else:
        return "No se puede determinar el tipo de hurto. Respuestas contradictorias."

# ---- Función para comentar tipo de robo ----
def procesar_robo(atestado_llm: AtestadoLLM, atestado: entities.Atestado):

    for bien in atestado.bienes_robados:
        if bien.propietario == "":
            propietario = atestado_llm.preguntar(questions.PROPIETARIO_GENERAL.format(bien=bien.nombre))
            propietario = propietario.strip()
            bien.propietario = propietario

    intimidacionViolencia = atestado_llm.preguntar(questions.INTIMIDACION_VIOLENCIA)
    allanamiento = atestado_llm.preguntar(questions.ALLANAMIENTO)
    forzamiento = atestado_llm.preguntar(questions.FORZAMIENTO)

    print("Hay forzamiento:", forzamiento)
    print("Hay allanamiento:", allanamiento)
    print("Hay intimidación o violencia:", intimidacionViolencia)

    if forzamiento.lower().startswith("sí")  or allanamiento.lower().startswith("sí"):
        subarticulosAgravantes(atestado_llm, atestado)
        
    if forzamiento.lower().startswith("sí"):
        print("Clasificado como robo con forzamiento")
        atestado.caracteristicas_del_delito.append("Forzamiento")

    if allanamiento.lower().startswith("domicilio"):
        print("Clasificado como robo con allanamiento casa")
        atestado.caracteristicas_del_delito.append("Allanamiento de casa o local")

    if not allanamiento.lower().startswith("domicilio") and not allanamiento.lower().startswith("no"):
        abierto = atestado_llm.preguntar(questions.ALLANAMIENTO_ESTABLECIMIENTO.format(est=allanamiento))
        if abierto.lower().startswith("no"):
            print("Clasificado como robo con allanamiento local")
            atestado.caracteristicas_del_delito.append("Allanamiento de casa o local")
            allanamiento = "sí"

    if allanamiento.lower().startswith("sí"):
        daniosGraves = atestado_llm.preguntar(questions.DANIOS_GRAVES)
        if daniosGraves.lower() == "sí":
            atestado.factores_agravantes.append("Daños graves")

    if intimidacionViolencia.lower().startswith("sí"):
        procesarRoboConIntimidacion(atestado_llm, atestado)
        print("Clasificado como robo con initmidacion o violencia")
        atestado.caracteristicas_del_delito.append("Intimidación o violencia")

    
    print("Atestado creado")
    return atestado

# ---- Función para procesar hurto de propietario ----
def procesarHurtoPropietario(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    valorTotalRobado(atestado_llm, atestado)
    print("Clasificado como hurto de propietario")
    print("Atestado creado")
    return atestado

# ---- Función para procesar hurto que no es de propietario ----
def procesarHurtoNoPropietario(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    subarticulosAgravantes(atestado_llm, atestado)
    entradaIlegal = atestado_llm.preguntar(questions.NEUTRALIZACION_ALARMAS)
    if entradaIlegal.lower() == "sí":
        atestado.caracteristicas_del_delito.append("Neutralización, eliminación o inutilización de alarmas o dispositivos de seguridad")

    print("Clasificado como hurto de no propietario")
    print("Atestado creado")
    return atestado

# ---- Función para procesar robo con intimidación ----
def procesarRoboConIntimidacion(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    armas = atestado_llm.preguntar(questions.ROBO_CON_ARMA)
    violenciaMinima = atestado_llm.preguntar(questions.VIOLENCIA_ESCASA)
    if armas.lower() == "sí":
        atestado.factores_agravantes.append("Robo con uso de armas")
    if violenciaMinima.lower() == "sí":
        atestado.factores_mitigantes.append("Violencia escasa o mínima")

# ---- Función para calcular el valor total robado ----
def valorTotalRobado(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    print("Obteniendo valor robado...")
    dineroEfectivo = atestado_llm.preguntar(questions.DINERO_ROBADO)
    valorRobado = atestado_llm.preguntar(questions.VALOR_ROBADO)

    valorTotalRobado = Decimal(dineroEfectivo) + Decimal(valorRobado)
    atestado.valor_total_robado = valorTotalRobado

# ---- Función para procesar carcterísticas del acusado ----
def caracteristicasAcusado(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    print("Obteniendo características de acusados...")
    for acusado in atestado.autores:
        orgCriminal = atestado_llm.preguntar(questions.ORGANIZACION_CRIMINAL.format(acusado=acusado.id))
        if orgCriminal.lower() == 'sí':
            acusado.caracteristicas_acusado.append("Organización Criminal")
            nombreOrganizacion = atestado_llm.preguntar(questions.NOMBRE_ORGANIZACION.format(acusado=acusado.id))
            acusado.organicacion_criminal = nombreOrganizacion
        
        antecedentes = atestado_llm.preguntar(questions.ANTECEDENTES.format(acusado=acusado.id))
        if antecedentes.lower() == 'sí':
            condenasPrevias = atestado_llm.preguntar(questions.CONDENAS_PREVIAS.format(acusado=acusado.id))
            if condenasPrevias.lower() == 'sí':
                acusado.caracteristicas_acusado.append("Más de 3 condenas previas")
            cantidadDelitos = int(atestado_llm.preguntar(questions.CANTIDAD_ANTECEDENTES.format(acusado=acusado.id)))
            acusado.antecedentes = cantidadDelitos

        compliceMenor = atestado_llm.preguntar(questions.COMPLICE_MENOR.format(acusado=acusado.id))
        if compliceMenor.lower() == 'sí':
            acusado.caracteristicas_acusado.append("Menor de edad cómplice")

# ---- Función para procesar características de los bienes ----
def caracteristicasBienes(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    print("Obteniendo características de bienes...")

    for bien in atestado.bienes_robados:
        agricola = atestado_llm.preguntar(questions.BIEN_AGRICOLA.format(bien=bien.nombre))
        artistico = atestado_llm.preguntar(questions.BIEN_ARTISTICO.format(bien=bien.nombre))
        cientifico = atestado_llm.preguntar(questions.BIEN_CIENTIFICO.format(bien=bien.nombre))
        cultural = atestado_llm.preguntar(questions.BIEN_CULTURAL.format(bien=bien.nombre))
        esencial = atestado_llm.preguntar(questions.BIEN_ESENCIAL.format(bien=bien.nombre))
        historico = atestado_llm.preguntar(questions.BIEN_HISTORICO.format(bien=bien.nombre))
        servicios = atestado_llm.preguntar(questions.BIEN_SERVICIOS.format(bien=bien.nombre))

        if agricola.lower() == "sí":
            bien.caracteristicas_especiales.append("Bien agrícola")

        if artistico.lower() == "sí":
            bien.caracteristicas_especiales.append("Bien artístico")
    
        if cientifico.lower() == "sí":
            bien.caracteristicas_especiales.append("Bien científico")

        if cultural.lower() == "sí":
            bien.caracteristicas_especiales.append("Bien cultural")

        if esencial.lower() == "sí":
            bien.caracteristicas_especiales.append("Bien esencial")

        if historico.lower() == "sí":
            bien.caracteristicas_especiales.append("Bien histórico")

        if servicios.lower() == "sí":
            bien.caracteristicas_especiales.append("Bien de servicios de interés general")



# ---- Función para procesar efectos del delito ----
def efectosDelito(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    print("Obteniendo efectos del delito...")
    start = time.time()
    efectos = False

    for victima in atestado.victimas:
        vulnerabilidad = atestado_llm.preguntar(questions.VULNERABILIDAD.format(victima=victima.id))
        impactoEconomico = atestado_llm.preguntar(questions.IMPACTO_ECONOMICO.format(victima=victima.id))
        fisicoPsicologico = atestado_llm.preguntar(questions.DANIOS_FISICO_PSICOLOGICOS.format(victima=victima.id))

        if vulnerabilidad.lower() == "sí":
            victima.efectos_del_delito.append("Situación de vulnerabilidad")
            efectos = True
        
        if impactoEconomico.lower() == "sí":
            victima.efectos_del_delito.append("Impacto económico")
            efectos = True

        if fisicoPsicologico.lower() == "sí":
            victima.efectos_del_delito.append("Daño físico o psicológico")
            efectos = True

    if efectos:
        atestado.factores_agravantes.append("Daños causados a la víctima")

# ---- Función para procesar agravantes comunes a delitos contra la propiedad ----
def subarticulosAgravantes(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    caracteristicasBienes(atestado_llm, atestado)
    caracteristicasAcusado(atestado_llm, atestado)
    efectosDelito(atestado_llm, atestado)
    valorTotalRobado(atestado_llm, atestado)

# ---- Función para obtener cómplices, testigos y empresas ----
def obtencionComplices(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    
    print("Obteniendo cómplices...")
    complices = atestado_llm.preguntar(questions.COMPLICES)
    if complices.lower() == "no":
        complices = []
    else:
        complices = [complice.strip() for complice in complices.split(",") if complice.strip()]
        complices = entities.initAcusados(complices)
        for complice in complices:
            edad = int(atestado_llm.preguntar(questions.EDAD_COMPLICES.format(complice=complice.id)))
            complice.edad = edad

    complices_def = complices.copy()
    if len(complices_def) > 1:
        for v1, v2 in combinations(complices,2):
            iguales = atestado_llm.preguntar(questions.MISMA_PERSONA.format(p1=v1, p2=v2))
            if iguales.lower() == "sí":
                complices_def.remove(v2)

    atestado.complices = complices_def

# ---- Función para obtener usuarios ----
def obtencionUsuarios(atestado_llm: AtestadoLLM, atestado: entities.Atestado):
    print("Obteniendo usuarios de los bienes...")
    start = time.time()
    for bien in atestado.bienes_robados:
        usuario = atestado_llm.preguntar(questions.USUARIO.format(bien=bien.nombre))
        usuario = usuario.strip()
        if usuario.lower().startswith("no") or usuario.lower().startswith("ninguno"):
            bien.usuario = ""
        else:
            bien.usuario = usuario




