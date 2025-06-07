from decimal import Decimal
from urllib.parse import urlparse
from rdflib import RDF, BNode, Graph, Literal
from owlready2 import get_ontology, sync_reasoner_pellet, ObjectPropertyClass, FunctionalProperty, World
from rdflib.namespace import RDF, OWL
from owlready2 import Not
from owlready2 import ThingClass, ObjectPropertyClass, FunctionalProperty

from articles import ARTICULOS_EXPLICACION

ONTOLOGY = "SCPO_Extended_Ontology_V01R08_AT08Q.owl"

def extract_local_name(iri):
    if '#' in iri:
        return iri.split('#')[-1]
    else:
        path = urlparse(iri).path
        return path.split('/')[-1]


def import_rdf_individuals(rdf_graph, onto):

    existing_individuals = {ind.name for ind in onto.individuals()}
    individual_map = {}  
    count_created = 0
    count_relations = 0

    # 1. CREAR INDIVIDUOS A PARTIR DE rdf:type
    for s, p, o in rdf_graph.triples((None, RDF.type, None)):
        subject_iri = str(s)
        class_iri = str(o)

        if any(ns in class_iri for ns in [
            "owl#", "rdf#", "rdfs#", "xsd#", "shacl#"
        ]):
            continue

        ind_name = extract_local_name(subject_iri)
        class_name = extract_local_name(class_iri)

        if ind_name in existing_individuals:
            continue

        cls = onto.search_one(iri=class_iri) or onto.search_one(iri="*#" + class_name)
        if cls is None:
            continue

        with onto:
            ind = cls(ind_name)
            individual_map[subject_iri] = ind
            existing_individuals.add(ind_name)
            count_created += 1
            print(f"  [+] Creado individuo: {ind_name} de tipo {cls.name}")

    print(f"✅ Total de individuos creados: {count_created}")

    for s, p, o in rdf_graph.triples((None, None, None)):
        if p == RDF.type:
            continue

        subject_iri = str(s)
        predicate_iri = str(p)
        object_iri = str(o)

        subj_ind = individual_map.get(subject_iri)
        if subj_ind is None:
            continue

        pred_name = extract_local_name(predicate_iri)
        prop = onto.search_one(iri=predicate_iri) or onto.search_one(iri="*#" + pred_name)

        if prop is None:
            continue

        if isinstance(o, Literal):

            value = o.toPython()

            if isinstance(value,Decimal):
                value=float(value)
                
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                value = float(value)
            elif hasattr(value, "value"):
                value = value.value

            current_value = getattr(subj_ind, prop.name)
                
            if isinstance(current_value, list):
                current_value.append(value)
            else:
                setattr(subj_ind, prop.name, value)

        else:

            obj_ind = individual_map.get(object_iri)
            if obj_ind is None:
                continue 

            if isinstance(prop, ObjectPropertyClass):
                if isinstance(prop, FunctionalProperty):
                    setattr(subj_ind, prop.name, obj_ind)
                else:
                    current = getattr(subj_ind, prop.name, [])
                    if isinstance(current, list):
                        current.append(obj_ind)
                    else:
                        setattr(subj_ind, prop.name, obj_ind)

                count_relations += 1
                print(f"  [+] Relación: {subj_ind.name} --{prop.name}--> {obj_ind.name}")

    print(f"✅ Total de relaciones/properties importadas: {count_relations}")



def aplicar_not_sobre_hasOffenceCharacteristic_si_es_nothing(rdf_graph, onto):

    for subj in rdf_graph.subjects(RDF.type, None):
        # Para cada tipo que sea un BNode (clase anónima)
        for _, _, class_bnode in rdf_graph.triples((subj, RDF.type, None)):
            if isinstance(class_bnode, BNode):
                # Buscar intersectionOf
                intersection = rdf_graph.value(class_bnode, OWL.intersectionOf)
                if intersection:
                    # Recorrer la lista RDF (puede usar rdflib.collection.Collection)
                    from rdflib.collection import Collection
                    items = list(Collection(rdf_graph, intersection))
                    for item in items:
                        # Buscar Restriction con owl:allValuesFrom owl:Nothing
                        if (item, RDF.type, OWL.Restriction) in rdf_graph:
                            prop = rdf_graph.value(item, OWL.onProperty)
                            all_val = rdf_graph.value(item, OWL.allValuesFrom)
                            if all_val == OWL.Nothing:
                                # Encontrado, buscar individuo y propiedad en la ontología
                                subject_iri = str(subj)
                                prop_iri = str(prop)
                                subj_ind = next((ind for ind in onto.individuals() if ind.iri == subject_iri), None)
                                owl_prop = onto.search_one(iri=prop_iri)
                                if subj_ind and owl_prop:
                                    from owlready2 import Not
                                    expr = Not(owl_prop.some(onto.RobberyCharacteristic))
                                    if expr not in subj_ind.is_a:
                                        subj_ind.is_a.append(expr)
                                        print(f"  🔁 Añadida inferencia negativa: {subj_ind.name} → NOT {owl_prop.name}.some(RobberyCharacteristic)")

    print("✅ Aplicación de NOT finalizada.\n")


def reasoner(ruta_grafo):
    print(f"📄 Cargando archivo RDF desde: {ruta_grafo}")

    onto = get_ontology(ONTOLOGY).load(reload=True)

    grafo = Graph()
    grafo.parse(ruta_grafo, format="xml")

    print("--- Importando individuos y relaciones desde RDF ---")
    import_rdf_individuals(grafo, onto)
    aplicar_not_sobre_hasOffenceCharacteristic_si_es_nothing(grafo, onto)

    print("--- Ejecutando razonador Pellet ---")
    with onto:
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

    # Buscar clase base Report
    report_class = onto.search_one(iri="*#Report")
    if not report_class:
        return []

    report_classes = set(report_class.subclasses()) | {report_class}

    clases_inferidas = set()

    for ind in onto.individuals():
        all_types = set(ind.INDIRECT_is_a)
        if report_classes & all_types:
            declared_classes = set(ind.is_a)
            for cls in declared_classes:
                if hasattr(cls, "name"):
                    clases_inferidas.add(cls.name)
                    print(f"  [+] Inferida clase: {cls.name} para individuo {ind.name}")

    return sorted(clases_inferidas)

def construir_articulos_inferidos(lista_clases: list[str]) -> list[str]:
    res = [ARTICULOS_EXPLICACION[c] for c in lista_clases if c in ARTICULOS_EXPLICACION]
    print(res)
    return res





