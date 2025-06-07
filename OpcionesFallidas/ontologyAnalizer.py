import sys
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, OWL
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/javiertorrecilla/Desktop/UMA/TFG/herramientaJuridica/.env")

apiKey = os.getenv("api_key")
url = os.getenv("base_url")

genai.configure(api_key=apiKey) 
model = genai.GenerativeModel('gemini-2.0-flash')

def get_literal(graph, subject, property):
    for o in graph.objects(subject, property):
        if o.language is None or o.language.startswith("es"):
            return str(o)
    return None

def get_name(uri):
    return str(uri).split("#")[-1] if "#" in uri else str(uri).split("/")[-1]

def get_unique_name(graph, subject, property):
    for o in graph.objects(subject, property):
        return get_name(o)
    return None

def load_ontology(file_path):
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

def describe_object_properties(graph):
    properties = set(graph.subjects(RDF.type, OWL.ObjectProperty))
    descriptions = []
    for prop in properties:
        name = get_name(prop)
        label = get_literal(graph, prop, RDFS.label)
        comment = get_literal(graph, prop, RDFS.comment)
        domain = get_unique_name(graph, prop, RDFS.domain)
        range_ = get_unique_name(graph, prop, RDFS.range)

        characteristics = []
        if (prop, RDF.type, OWL.SymmetricProperty) in graph:
            characteristics.append("propiedad simétrica")
        if (prop, RDF.type, OWL.FunctionalProperty) in graph:
            characteristics.append("propiedad funcional")
        if (prop, RDF.type, OWL.InverseFunctionalProperty) in graph:
            characteristics.append("propiedad inversamente fuuncional")
        if (prop, RDF.type, OWL.TransitiveProperty) in graph:
            characteristics.append("propiedad transitiva")

        type_text = " and ".join(characteristics) if characteristics else "a relation"
        description = f"{name}: Tiene {type_text} entre {domain or 'una entidad'} y {range_ or 'otra entidad'}."
        if comment:
            description += f" {comment}"
        descriptions.append(description)
    return descriptions

def procesar_propiedades_objeto_con_gemini(propiedades) -> str:
    """
    Procesa las propiedades de objeto con Gemini para explicar relaciones
    """
    system_prompt = """Eres un experto en modelado de conocimiento. Explica estas relaciones entre entidades:
    - Usa el nombre de la relación exactamente como aparece (no lo traduzcas ni formatees)
    - Destaca el tipo de relación (jerárquica, asociativa, etc.)
    - Explica la dirección cuando sea relevante (ej: "A implica B")
    - Usa verbos activos (ej: "permite", "determina")
    - Mantén el formato original de entrada, sin caracteres especiales como * o **
    - Traduce al español solo las descripciones, no los nombres de las relaciones
    - Incluye ejemplos breves cuando ayuden
    - Devuelve solo las relaciones explicadas en lenguaje natural, una por línea, sin ningún carácter adicional
    """

    response = model.generate_content(
        system_prompt + "\n\nRelaciones a explicar:\n" + "\n".join(propiedades),
        generation_config=genai.types.GenerationConfig(temperature=0.4)
    )

    cleaned_lines = [
        line.replace("*", "").strip()
        for line in response.text.split("\n")
        if line.strip()
    ]
    
    return "\n".join(cleaned_lines)


def ontology_analysis_with_gemini():
    ontology_path = input("Ingrese la ruta de la ontología OWL: ")
    ontology = load_ontology(ontology_path)
    
    # Obtener descripciones técnicas
    obj_prop_tecnicas = describe_object_properties(ontology)
    
    # Procesar con Gemini
    obj_prop_naturales = procesar_propiedades_objeto_con_gemini(obj_prop_tecnicas)
    
    return obj_prop_naturales

def main():
    relations = ontology_analysis_with_gemini()
    print(relations)

if __name__ == "__main__":
    main()