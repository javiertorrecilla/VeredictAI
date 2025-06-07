import google.generativeai as genai # type: ignore
import json
import re
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/javiertorrecilla/Desktop/UMA/TFG/herramientaJuridica/.env")

apiKey = os.getenv("api_key")
url = os.getenv("base_url")

# Configura la clave de API de Gemini AI
genai.configure(api_key=apiKey)

# Parsear la ontología de texto a un diccionario
def parse_ontology(ontology_text):
    ontology_dict = {}
    # Se separan las líneas de la ontología
    for line in ontology_text.split('\n'):
        if line.strip():  # Ignorar líneas vacías
            parts = line.split(":")
            if len(parts) == 2:
                entity = parts[0].strip()
                definition = parts[1].strip()
                ontology_dict[entity] = definition
    return ontology_dict

def extract_entities(text, ontology_dict):
    """Busca las entidades y atributos genéricos en el texto y los empareja con sus definiciones."""
    
    # Extraer entidades en forma de lista
    entities = list(ontology_dict.keys())
    print(entities)
    
    # Crear el prompt para Gemini AI para buscar las entidades y atributos en el texto
    prompt = f"""
    Dado el siguiente listado de entidades y sus definiciones:

    Entidades:
    {json.dumps(ontology_dict, ensure_ascii=False, indent=4)}

    Analiza el siguiente texto y extrae las entidades encontradas, asociándolas con sus definiciones.
    Ten en cuenta que puede haber varias entidades que sean la misma y se refieran a la misma,
    en ese caso solo devuelve una entidad. Si dos entidades de forma analítica son la misma, solo se guarda una.

    Texto a analizar:
    {text}

    Devuelve un JSON con las entidades encontradas y sus definiciones
    Solo incluye las entidades con las propiedades 'entity' y 'entity_type'.
    """
    
    # Generamos la respuesta con Gemini AI
    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
    
    # Extraer el contenido generado, que es un string con formato JSON
    response_text = response.text.strip()

    # Limpiar el formato extra (quitar ```json, saltos de línea, etc.)
    cleaned_response = response_text.replace("```json", "").replace("```", "").strip()

    # Convertir el texto limpio a un objeto JSON
    try:
        json_data = json.loads(cleaned_response)
        return json_data
    except json.JSONDecodeError:
        return {"error": "No se pudo procesar la respuesta correctamente."}
    
def extract_attributes(text, entities, attributes):
    """Busca las entidades y atributos genéricos en el texto y los empareja con sus definiciones."""
    
    # Crear el prompt para Gemini AI para buscar las entidades y atributos en el texto
    prompt = f"""
    Dado el siguiente listado de atributos y sus definiciones:

    Atributos:
    {json.dumps(attributes, ensure_ascii=False, indent=4)}

    Estos son atributos genéricos que pueden pertenecer a varias entidades, es decir, por ejemplo el atributo name puede estar relacionado
    con las entidades acusado y victima teniendo cada entidad su atributo nombre distinto y propio. 
    Ten en cuenta que puede haber varios atributos que sean el mismo y se refiera a la misma entidad,
    en ese caso solo devuelve un atributo, no duplicados. Además no puede haber entidades duplicadas si refieren a la misma cosa.

    Las entidades son las siguientes:
    {entities}

    Analiza el siguiente texto y extrae las los atributos encontrados, asociándolos con sus entidades correspondientes.

    Texto a analizar:
    {text}

    Devuelve un JSON con las entidades encontradas, sus definiciones y los atributos correspondientes encontrados y el valor de los mismos.
    """
    
    # Generamos la respuesta con Gemini AI
    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
    
    # Extraer el contenido generado, que es un string con formato JSON
    response_text = response.text.strip()

    # Limpiar el formato extra (quitar ```json, saltos de línea, etc.)
    cleaned_response = response_text.replace("```json", "").replace("```", "").strip()

    # Convertir el texto limpio a un objeto JSON
    try:
        json_data = json.loads(cleaned_response)
        return json_data
    except json.JSONDecodeError:
        return {"error": "No se pudo procesar la respuesta correctamente."}

# Ejemplo de texto a analizar
texto = """
Juan es acusado de un robo a mano armada y se encuentra en el artículo 234 del código penal.
La víctima sufrió daños debido al delito. Además, el acusado tiene antecedentes previos.
La víctima también tiene dejó contancia de los hechos en el atestado 3344 y su nombre es María.
"""

# Ontología en formato texto (como la proporcionaste)
ontology_text = """
Accused: Persona que es acusada de un delito.
ArmedRobbery: Un robo a mano armada.
Article234_1: El artículo 234, párrafo 1.
Victim: Víctima.
"""

# Atributos genéricos para las entidades (ejemplo con atributos comunes)
generic_attributes = """
Age: La edad de una persona.
Name: El nombre de una persona.
PersonId: El identificador de una persona.
ValueCost: El valor de un costo.
hasPunishmentValue: Tiene un valor de castigo.
isOpenOrOccupied: Indica si está abierto u ocupado.
num: Un número.
reportId: El identificador de un reporte.
"""

# Parsear la ontología y atributos
entities_dict = parse_ontology(ontology_text)
attributes_dict = parse_ontology(generic_attributes)

# Extraer entidades y atributos del texto
entities = extract_entities(texto, entities_dict)
#entities_list = [entity["entity"] for entity in entities.get("entities", [])]
attributes = extract_attributes(texto, entities, attributes_dict)

# Mostrar el resultado en formato JSON
print(json.dumps(entities, indent=4, ensure_ascii=False))
#Resultados en JSON de los atributos
print(json.dumps(attributes, indent=4, ensure_ascii=False))
