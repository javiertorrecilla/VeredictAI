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

def extract_entities_and_definitions_from_text(text, ontology_dict, generic_attributes):
    """Busca las entidades y atributos genéricos en el texto y los empareja con sus definiciones."""
    
    # Primero se extraen las entidades de la ontología
    entities = list(ontology_dict.keys())
    
    # Crear el prompt para Gemini AI para buscar las entidades y atributos en el texto
    prompt = f"""
    Dado el siguiente listado de entidades y sus definiciones:

    Entidades:
    {json.dumps(ontology_dict, ensure_ascii=False, indent=4)}

    Atributos (genéricos, aplicables a diferentes entidades):
    {json.dumps(generic_attributes, ensure_ascii=False, indent=4)}

    Analiza el siguiente texto y extrae las entidades encontradas, asociándolas con sus definiciones.
    Si se encuentran atributos genéricos en el texto, también asócialos con las entidades correspondientes.

    Texto a analizar:
    {text}

    Devuelve un JSON con las entidades encontradas, sus definiciones, y los atributos genéricos correspondientes (si los tiene).
    Solo incluye las entidades con las propiedades 'entity' y 'entity_type'. Si la entidad tiene atributos genéricos, inclúyelos también con sus definiciones en formato natural.
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
La víctima también tiene el identificador de reporte 12345 y su nombre es María.
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

# Extraer entidades y definiciones del texto
resultado = extract_entities_and_definitions_from_text(texto, entities_dict, attributes_dict)

# Mostrar el resultado en formato JSON
print(json.dumps(resultado, indent=4, ensure_ascii=False))
