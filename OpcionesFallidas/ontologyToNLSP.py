from rdflib import Graph, OWL, RDF, RDFS # type: ignore
import google.generativeai as genai # type: ignore

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/javiertorrecilla/Desktop/UMA/TFG/herramientaJuridica/.env")

apiKey = os.getenv("api_key")
url = os.getenv("base_url")

genai.configure(api_key=apiKey)

def get_label(g, entity):
    """Obtiene el rdfs:label de una entidad en la ontología."""
    for _, _, label in g.triples((entity, RDFS.label, None)):
        return str(label)
    return entity.split("#")[-1]  # Si no hay label, usa el último fragmento del URI

def load_ontology(ontology_path):
    """Carga una ontología OWL desde un archivo y organiza sus elementos."""
    g = Graph()
    try:
        g.parse(ontology_path, format='turtle')
    except Exception as e:
        return {"error": f"Error al cargar la ontología: {str(e)}"}

    ontology = {
        "Entidades": {},
        "Relaciones": {},
        "Atributos": {}
    }
    
    for c in g.subjects(RDF.type, OWL.Class):
        ontology["Entidades"][str(c)] = get_label(g, c)
    
    for p in g.subjects(RDF.type, OWL.ObjectProperty):
        ontology["Relaciones"][str(p)] = get_label(g, p)
    
    for p in g.subjects(RDF.type, OWL.DatatypeProperty):
        ontology["Atributos"][str(p)] = get_label(g, p)
    
    return ontology

def get_separated_ontology(ontology):
    """Devuelve la ontología separada en listas distintas."""
    entidades = list(ontology["Entidades"].values())
    relaciones = list(ontology["Relaciones"].values())
    atributos = list(ontology["Atributos"].values())
    
    return entidades, relaciones, atributos

# System prompt global que se mantiene constante para todas las consultas
system_prompt = """
Eres un experto en ontologías y lenguaje natural. Tu tarea es transformar definiciones técnicas de una ontología OWL en lenguaje claro, comprensible y conciso, sin perder la precisión. Además, deberás traducir las condiciones necesarias para las entidades, relaciones y atributos, usando un lenguaje accesible y directo, manteniendo la estructura de la ontología. 
Nunca añadas explicaciones adicionales ni información irrelevante.
"""

def definitions_with_gemini(text):
    """Usa Gemini para mejorar la redacción en lenguaje natural."""
    prompt = f"""
    {system_prompt}

    Convierte las definiciones de la ontología a un lenguaje natural claro y conciso.  

    Instrucciones:
    - Mantén la estructura sin agregar información extra.
    - Omite elementos sin definir o irrelevantes.
    - Usa frases naturales y fáciles de entender.
    - No incluyas explicaciones sobre lo que haces, solo devuelve la lista formateada.

    Ejemplo de formato esperado en la salida como líneas de texto:  
    "Accused": "Persona que ha sido acusada de cometer un delito.",
    "ArmedRobbery": "Robo cometido con el uso de un arma.",
    "Victim": "Persona que ha sufrido daños como resultado de un delito."

    Ontología a convertir:
    {text}
    """

    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
    return response.text.strip() if response.text else text

def conditions_to_natural_language(text):
    """Usa Gemini para traducir condiciones ontológicas a lenguaje natural."""
    prompt = f"""
    {system_prompt}

    Convierte las condiciones necesarias para cada elemento de la ontología en lenguaje natural claro y estructurado.  

    Instrucciones:
    - Explica qué se debe cumplir para que existan las entidades, relaciones y atributos.
    - Omite prefijos técnicos (como ne07) y otros términos irrelevantes.
    - Usa frases directas sin explicaciones adicionales.
    - Mantén la estructura y devuelve solo la lista con condiciones traducidas.

    Ejemplo de formato esperado en la salida como líneas de texto:  
    Accused: Debe existir si hay una persona señalada como responsable de un delito.
    CrimeScene: Solo se registra si hay un evento delictivo confirmado.
    Evidence: Es necesaria si se presenta en el juicio como prueba.

    Ontología a traducir:
    {text}
    """

    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
    return response.text.strip() if response.text else text

def ontology_processing():
    """Proceso completo desde lectura de ontología a procesamiento a lenguaje natural"""
    ontology_path = input("Ingrese la ruta de la ontología OWL: ")
    
    # Validación de existencia de archivo
    try:
        ontology = load_ontology(ontology_path)
        if "error" in ontology:
            raise ValueError(ontology["error"])
    except Exception as e:
        print(f"Error al cargar la ontología: {str(e)}")
        return
    
    entities, relations, attributes = get_separated_ontology(ontology)

    # Procesamiento de las entidades
    entities_clear = definitions_with_gemini(" ".join(entities))
    entities_conditions = conditions_to_natural_language(entities_clear)

    # Procesamiento de las relaciones
    relations_clear = definitions_with_gemini(" ".join(relations))
    relations_conditions = conditions_to_natural_language(relations_clear)

    # Procesamiento de los atributos
    attributes_clear = definitions_with_gemini(" ".join(attributes))
    attributes_conditions = conditions_to_natural_language(attributes_clear)

    return entities_conditions, relations_conditions, attributes_conditions

def main():
    ontology_path = input("Ingrese la ruta de la ontología OWL: ")
    
    # Validación de existencia de archivo
    try:
        ontology = load_ontology(ontology_path)
        if "error" in ontology:
            raise ValueError(ontology["error"])
    except Exception as e:
        print(f"Error al cargar la ontología: {str(e)}")
        return
    
    entities, relations, attributes = get_separated_ontology(ontology)
    entities_enhanced_text = definitions_with_gemini(entities)
    relations_enhanced_text = definitions_with_gemini(relations)
    attributes_enhanced_text = definitions_with_gemini(attributes)
    entities_conditions = conditions_to_natural_language(entities_enhanced_text)
    relations_conditions = conditions_to_natural_language(relations_enhanced_text)
    attributes_conditions = conditions_to_natural_language(attributes_enhanced_text)

    print(entities_conditions)
    print(relations_conditions)
    print(attributes_conditions)

if __name__ == "__main__":
    main()
