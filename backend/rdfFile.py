import rdflib
from rdflib import XSD, BNode, Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, OWL
from entities import Atestado, Bien, Acusado, Victima
import os
from platformdirs import user_downloads_path

# Definir el espacio de nombres para la ontología proporcionada
DELPATRIMONIO = Namespace("http://www.semanticweb.org/fjnavarrete/ontologies/2022/0/delito_contra_patrimonio#")

## ---- Función para iniciar un grafo RDF -----
def iniciar_grafo():
    """Crea un grafo RDF inicializado con los prefijos de la ontología."""
    g = rdflib.Graph()
    g.bind("delpatrimonio", DELPATRIMONIO)
    g.bind("owl", OWL)

    # Declarar relaciones como ObjectProperties
    object_properties = [
        DELPATRIMONIO.hasAccomplice,
        DELPATRIMONIO.stolenBy, 
        DELPATRIMONIO.belongsToCriminalOrganization, 
        DELPATRIMONIO.hasThingCharacteristic, 
        DELPATRIMONIO.hasEffectOffence, 
        DELPATRIMONIO.hasPunishment,
        DELPATRIMONIO.hasAggravatingFactor, 
        DELPATRIMONIO.hasMitigatingFactor,
        DELPATRIMONIO.hasOffenceCharacteristic, 
        DELPATRIMONIO.stolenthing, 
        DELPATRIMONIO.usedByOwner,
        DELPATRIMONIO.belongsTo,
        DELPATRIMONIO.hasPreviusSentence, 
        DELPATRIMONIO.stolenByOwner,
        DELPATRIMONIO.isThiefOf,
        DELPATRIMONIO.hasOffenceAggravatingFactor
    ]

    for prop in object_properties:
        g.add((prop, RDF.type, OWL.ObjectProperty))

    # Declarar propiedades de datos (DatatypeProperty)
    datatype_properties = [
        DELPATRIMONIO.Name,
        DELPATRIMONIO.ValueCost,
        DELPATRIMONIO.Age,
        DELPATRIMONIO.num
    ]

    for prop in datatype_properties:
        g.add((prop, RDF.type, OWL.DatatypeProperty))

    return g

def uriSegura(text: str) -> str:
    """Devuelve una representación segura para usar en URIs."""
    text = text.strip().replace("/", "_")
    return text.strip().replace(" ", "_")

## ---- Añadir un nuevo bien -----
def nuevoBien(g, bien: Bien, atestado: Atestado, atestado_uri: URIRef, primerBien: bool):
    """Añade un bien sustraído al grafo RDF."""
    bien_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(bien.nombre)}")
    g.add((bien_uri, RDF.type, DELPATRIMONIO.StolenGoods))
    g.add((atestado_uri, DELPATRIMONIO.stolenthing, bien_uri))

    # Añadir características del bien
    for caracteristica in bien.caracteristicas_especiales:
        g.add((URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(caracteristica)}"), RDF.type, DELPATRIMONIO.ThingCharacteristic))
        g.add((bien_uri, DELPATRIMONIO.hasThingCharacteristic, URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(caracteristica)}")))

    # Asociar el valor total robado con el bien
    if primerBien:
        g.add((bien_uri, DELPATRIMONIO.ValueCost, Literal(str(atestado.valor_total_robado), datatype=XSD.decimal)))

    # Relación "belongsTo" si hay propietario
    if bien.propietario != "":
        propietario_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(bien.propietario)}")
        g.add((bien_uri, DELPATRIMONIO.belongsTo, propietario_uri))

    if len(atestado.caracteristicas_del_delito) == 0:
        if bien.propietario == bien.usuario:
            propietario_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(bien.propietario)}")
            g.add((bien_uri, DELPATRIMONIO.usedByOwner, propietario_uri))


## ---- Añadir nueva víctima -----
def nuevaVictima(g, victima: Victima, atestado: Atestado):
    """Registra una víctima en el grafo."""
    # Crear la URI de la víctima
    victima_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(victima.id)}")
    
    # Añadir a la víctima al grafo
    g.add((victima_uri, RDF.type, DELPATRIMONIO.Victim))
    


## ---- Añadir nuevo acusado (autor o cómplice) -----
def nuevoAcusado(g, acusado: Acusado, atestado: Atestado, atestado_uri: URIRef):
    """Añade al grafo la información de un acusado o cómplice."""
    acusado_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(acusado.id)}")
    g.add((acusado_uri, RDF.type, DELPATRIMONIO.Accused))

    if acusado.organizacion_criminal != "":
        criminal_org_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(acusado.organizacion_criminal)}")
        g.add((criminal_org_uri, RDF.type, DELPATRIMONIO.CriminalOrganization))
        g.add((criminal_org_uri, DELPATRIMONIO.Name, Literal(acusado.organizacion_criminal)))
        g.add((acusado_uri, DELPATRIMONIO.belongsToCriminalOrganization, criminal_org_uri))

    # Verificar antecedentes y características del acusado
    if acusado.antecedentes > 0:
        punishment_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Detencion_{uriSegura(acusado.id)}")
        g.add((punishment_uri, RDF.type, DELPATRIMONIO.PropertyCrimePunishments))
        g.add((acusado_uri, DELPATRIMONIO.hasPreviusSentence, punishment_uri))
        if acusado.antecedentes > 3:
            g.add((punishment_uri, DELPATRIMONIO.num, Literal(acusado.antecedentes, datatype=XSD.integer)))

    for caracteristica in acusado.caracteristicas_acusado:
        if caracteristica == "Más de 3 condenas previas":
            older_detention_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Más_3_condenas_previas")
            g.add((older_detention_uri, RDF.type, DELPATRIMONIO.OlderDetention))
        if caracteristica == "Menor de edad cómplice":
            minor_accomplice_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Cómplice_menor")
            g.add((minor_accomplice_uri, RDF.type, DELPATRIMONIO.MinnorAcomplice))
        if caracteristica == "Organización Criminal":
            collaboration_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_ColaboracionOrganizacionCriminal")
            g.add((collaboration_uri, RDF.type, DELPATRIMONIO.CollaborationWithCriminalOrganisation))

    for agravante in atestado.factores_agravantes:
        if agravante == "Robo con uso de armas":
            armed_robbery_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Robo_con_armas")
            g.add((armed_robbery_uri, RDF.type, DELPATRIMONIO.ArmedRobbery))
            g.add((acusado_uri, DELPATRIMONIO.hasAggravatingFactor, armed_robbery_uri))
        if agravante == "Daños Graves":
            damage_caused_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Daños_Graves")
            g.add((damage_caused_uri, RDF.type, DELPATRIMONIO.DamageCaused))
            g.add((atestado_uri, DELPATRIMONIO.hasOffenceAggravatingFactor, damage_caused_uri))

    # Factores mitigantes
    for mitigante in atestado.factores_mitigantes:
        if mitigante == "Violencia escasa o mínima":
            minimal_intimidation_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Violencia_minima")
            g.add((minimal_intimidation_uri, RDF.type, DELPATRIMONIO.MinimalIntimidationOrViolence))
            g.add((acusado_uri, DELPATRIMONIO.hasMitigatingFactor, minimal_intimidation_uri))

    for bien in atestado.bienes_robados:
        bien_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(bien.nombre)}")
        g.add((bien_uri, DELPATRIMONIO.stolenBy, acusado_uri))
        g.add((acusado_uri, DELPATRIMONIO.isThiefOf, bien_uri))

        if len(atestado.caracteristicas_del_delito) == 0:
            if bien.propietario == acusado.id: 
                g.add((bien_uri, DELPATRIMONIO.stolenByOwner, acusado_uri))

    for complice in atestado.complices:
        complice_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_{uriSegura(complice.id)}")
        g.add((complice_uri, RDF.type, DELPATRIMONIO.Accused))
        g.add((acusado_uri, DELPATRIMONIO.hasAccomplice, complice_uri))
        if complice.edad<18:
            g.add((complice_uri, DELPATRIMONIO.Age, Literal(complice.edad, datatype=XSD.int)))

## ---- Añadir el atestado completo -----
def nuevoAtestadoRobo(atestado: Atestado):
    """Construye el RDF de un atestado clasificado como robo."""
    g = iniciar_grafo()

    # Crear URI único para el atestado
    nombre_archivo = uriSegura(atestado.atestado_id)
    atestado_uri = URIRef(f"{DELPATRIMONIO}{nombre_archivo}")
    g.add((atestado_uri, RDF.type, DELPATRIMONIO.Report))

    # Agregar características del delito
    for caracteristica in atestado.caracteristicas_del_delito:

        if caracteristica == "Neutralización, eliminación o inutilización de alarmas o dispositivos de seguridad":
            char_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_EntardaIlegal")
            g.add((char_uri, RDF.type, DELPATRIMONIO.UnlawfulEntry))
            g.add((atestado_uri, DELPATRIMONIO.hasOffenceCharacteristic, char_uri))

        elif caracteristica == "Forzamiento":
            char_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Forzamiento")
            g.add((char_uri, RDF.type, DELPATRIMONIO.BurglaryCrime))
            g.add((atestado_uri, DELPATRIMONIO.hasOffenceCharacteristic, char_uri))

        elif caracteristica == "Allanamiento de casa o local":
            char_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Allanamiento")
            g.add((char_uri, RDF.type, DELPATRIMONIO.HouseOrPremiseBreaking))
            g.add((atestado_uri, DELPATRIMONIO.hasOffenceCharacteristic, char_uri))

        elif caracteristica == "Intimidación o violencia":
            char_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_ViolenciaIntimidación")
            g.add((char_uri, RDF.type, DELPATRIMONIO.RobberyWithIntimidationOrViolence))
            g.add((atestado_uri, DELPATRIMONIO.hasOffenceCharacteristic, char_uri))

        else:
            continue  # Característica no reconocida

    # Agregar agravantes
    for agravante in atestado.factores_agravantes:
        if agravante.strip().lower() == "Daños causados a la víctima":
            aggravating_factor_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Daño_a_victima")
            g.add((aggravating_factor_uri, RDF.type, DELPATRIMONIO.AggravatingFactorAffectingInjuredParty))
            g.add((atestado_uri, DELPATRIMONIO.hasOffenceAggravatingFactor, aggravating_factor_uri))

    # Agregar víctimas, bienes y autores
    for victima in atestado.victimas:
        nuevaVictima(g, victima, atestado)

    primerBien = True
    for bien in atestado.bienes_robados:
        nuevoBien(g, bien, atestado, atestado_uri, primerBien)
        primerBien = False

    for autor in atestado.autores:
        nuevoAcusado(g, autor, atestado, atestado_uri)

    return g, nombre_archivo


## ---- Añadir el atestado completo -----
def nuevoAtestadoHurto(atestado: Atestado):

    """Construye el RDF de un atestado de hurto, creando restricciones
    cuando no hay características del delito."""

    g = iniciar_grafo()

    atestado_uri = URIRef(f"{DELPATRIMONIO}{uriSegura(atestado.atestado_id)}")
    g.add((atestado_uri, RDF.type, DELPATRIMONIO.Report))

    if len(atestado.caracteristicas_del_delito) > 0:
        caracteristica = atestado.caracteristicas_del_delito[0]
    else:
        caracteristica = []
        # Creamos una restricción: hasOffenceCharacteristic only owl:Nothing
        restriccion_bnode = BNode()
        g.add((restriccion_bnode, RDF.type, OWL.Restriction))
        g.add((restriccion_bnode, OWL.onProperty, DELPATRIMONIO.hasOffenceCharacteristic))
        g.add((restriccion_bnode, OWL.allValuesFrom, OWL.Nothing))

        # Crear clase anónima: intersectionOf(Report, restricción)
        from rdflib.collection import Collection
        intersection_node = BNode()
        list_node = BNode()

        g.add((intersection_node, RDF.type, OWL.Class))
        g.add((intersection_node, OWL.intersectionOf, list_node))
        Collection(g, list_node, [DELPATRIMONIO.Report, restriccion_bnode])

        # Declarar que el atestado es tipo de esa clase anónima
        g.add((atestado_uri, RDF.type, intersection_node))


    # Características del delito
    if caracteristica == "Neutralización, eliminación o inutilización de alarmas o dispositivos de seguridad":
            char_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_EntardaIlegal")
            g.add((char_uri, RDF.type, DELPATRIMONIO.UnlawfulEntry)) 
            g.add((atestado_uri, DELPATRIMONIO.hasOffenceCharacteristic, char_uri))

    # Agregar agravantes
    for agravante in atestado.factores_agravantes:
        if agravante == "Daños causados a la víctima":
            aggravating_factor_uri = URIRef(f"{DELPATRIMONIO}_{uriSegura(atestado.atestado_id)}_Daño_a_victima")
            g.add((aggravating_factor_uri, RDF.type, DELPATRIMONIO.AggravatingFactorAffectingInjuredParty))
            g.add((atestado_uri, DELPATRIMONIO.hasOffenceAggravatingFactor, aggravating_factor_uri))

    # Asociar elementos como víctimas, bienes y acusados
    for victima in atestado.victimas:
        nuevaVictima(g, victima, atestado)
    primerBien = True
    for bien in atestado.bienes_robados:
        nuevoBien(g, bien, atestado, atestado_uri, primerBien)
        primerBien = False
    for autor in atestado.autores:
        nuevoAcusado(g, autor, atestado, atestado_uri)

    nombre_archivo = f"{uriSegura(atestado.atestado_id)}"  

    return g, nombre_archivo

def crear_rdf(atestado: Atestado):
    """Crea el archivo RDF correspondiente a un ``Atestado``."""
    if len(atestado.caracteristicas_del_delito) == 0 or atestado.caracteristicas_del_delito[0] == "Neutralización, eliminación o inutilización de alarmas o dispositivos de seguridad": 
        grafo, nombre_archivo = nuevoAtestadoHurto(atestado)
    else:
        grafo, nombre_archivo = nuevoAtestadoRobo(atestado)

    ruta_descargas = user_downloads_path()
    os.makedirs(ruta_descargas, exist_ok=True)

    ruta_salida = os.path.join(ruta_descargas, f"{nombre_archivo}.rdf")
    grafo.serialize(destination=ruta_salida, format="xml")

    print(f"RDF creado para atestado guardado en {ruta_salida}")

    return f"{nombre_archivo}.rdf"

def filtrar_grafo(rdf_text: str, formato="xml", namespace_base="http://www.semanticweb.org/fjnavarrete/ontologies/2022/0/delito_contra_patrimonio#") -> Graph:
    """Elimina nodos externos al informe y los blank nodes, manteniendo solo información relevante."""
    g_original = Graph()
    g_original.parse(data=rdf_text, format=formato)

    g_filtrado = Graph()
    visitados = set()

    nodos_iniciales = set(g_original.subjects(RDF.type, URIRef(namespace_base + "Report")))

    def recorrer_nodo(nodo):
        if isinstance(nodo, BNode) or nodo in visitados:
            return
        visitados.add(nodo)

        for s, p, o in g_original.triples((nodo, None, None)):
            if isinstance(s, BNode) or isinstance(o, BNode):
                continue
            g_filtrado.add((s, p, o))
            if isinstance(o, URIRef):
                recorrer_nodo(o)

        for s, p, o in g_original.triples((None, None, nodo)):
            if isinstance(s, BNode) or isinstance(o, BNode):
                continue
            g_filtrado.add((s, p, o))
            recorrer_nodo(s)

    for nodo in nodos_iniciales:
        recorrer_nodo(nodo)

    return g_filtrado
