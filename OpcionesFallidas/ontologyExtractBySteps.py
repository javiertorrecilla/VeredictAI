import google.generativeai as genai # type: ignore
import json
import re

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/javiertorrecilla/Desktop/UMA/TFG/herramientaJuridica/.env")

apiKey = os.getenv("api_key")
url = os.getenv("base_url")

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

    Reglas para la extracción de entidades:

    Evita duplicados:  
    - Si una entidad aparece varias veces en el texto pero se refiere a la misma, solo inclúyela una vez.  
    - Incorrecto:  
        ```json
        [
            {{"entity": "Accused"}},
            {{"entity": "Accused"}}
        ]
        ```
    - Correcto:  
        ```json
        [
            {{"entity": "Accused"}}
        ]
        ```

    Agrupa sinónimos bajo la misma entidad:  
    - Si una entidad es mencionada con distintos nombres (ej. "el acusado", "Juan"), agrúpala bajo la misma entidad.  

    Distingue entidades diferentes:  
    - Si hay múltiples entidades del mismo tipo pero son distintas, identifícalas como separadas.  
    - Ejemplo Correcto:  
        ```json
        [
            {{"entity": "Victim", "id": 1}},
            {{"entity": "Victim", "id": 2}}
        ]
        ```

    Entrada:
    {text}

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
    

def associate_attributes_with_detected_entities(detected_entities, attributes_dict):
    """Asociar los atributos a las entidades detectadas."""
    
    prompt = f"""
    Dado el siguiente listado de entidades detectadas:

    {json.dumps(detected_entities, ensure_ascii=False, indent=4)}

    Y el siguiente listado de atributos con sus definiciones:

    {json.dumps(attributes_dict, ensure_ascii=False, indent=4)}

    Asocia cada atributo solo con las entidades detectadas en el texto. 
    Por ejemplo, si "Victim" está en el texto, "Name" y "Age" pueden ser atributos válidos, pero "reportId" no.
    
    Devuelve un JSON con el siguiente formato:
    {{
        "Accused": ["Name", "Age", "PersonId"],
        "Victim": ["Name", "Age", "PersonId"]
    }}

    Debe contener todas las entidades que han sido pasadas por texto independientemente de que tengan o no atributos para asociar.
    """
    
    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
    response_text = response.text.strip()
    cleaned_response = response_text.replace("```json", "").replace("```", "").strip()

    try:
        json_data = json.loads(cleaned_response)
        return json_data
    except json.JSONDecodeError:
        return {"error": "No se pudo procesar la respuesta correctamente."}
    
def extract_attributes(text, entity_attribute_mapping):
    """Extraer los atributos del texto, asegurándose de que coincidan con las entidades detectadas."""
    
    prompt = f"""
    Dado el siguiente listado de entidades detectadas con sus atributos válidos:

    {json.dumps(entity_attribute_mapping, ensure_ascii=False, indent=4)}

    Reglas para la extracción:
    - Extrae solo los atributos que correspondan a cada entidad según el listado proporcionado.
    - No asignes atributos a entidades que no pueden poseerlos.
    - Si una entidad aparece en el texto pero no tiene atributos asociados en la lista, inclúyela en el JSON igualmente.
    - Evita duplicados: si un atributo ya fue registrado para una entidad, no lo repitas.
    - Para cada atributo detectado, extrae el valor correspondiente del texto.

    Formato de salida (ejemplo esperado):
    ```json
    [
        {{
            "entity": "Accused",
            "attributes": {{
                "Name": "Juan Pérez",
                "Age": 30
            }}
        }},
        {{
            "entity": "Victim",
            "attributes": {{
                "Name": "María González"
            }}
        }},
        {{
            "entity": "Article234_1",
            "attributes": {{}}
        }}
    ]
    ```
    
    Texto a analizar:
    {text}

    Devuelve el JSON con todas las entidades y sus atributos (vacíos si no se encontraron en el texto).
    """

    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
    response_text = response.text.strip()
    cleaned_response = response_text.replace("```json", "").replace("```", "").strip()

    try:
        json_data = json.loads(cleaned_response)
        return json_data
    except json.JSONDecodeError:
        return {"error": "No se pudo procesar la respuesta correctamente."}

def ontologyData(entities, attributes, text):
    """Obtener los datos de la ontologia que se presentan en el texto"""

    # Parsear la ontología y atributos
    entities_dict = parse_ontology(entities)
    attributes_dict = parse_ontology(attributes)

    # Extraer entidades del texto
    entities = extract_entities(text, entities_dict)

    # Asociar atributos con las entidades detectadas
    entity_attribute_mapping = associate_attributes_with_detected_entities(entities, attributes_dict)

    # Extraer atributos usando la información del paso anterior
    entitiesWithAttributes = extract_attributes(text, entity_attribute_mapping)

    # Mostrar los resultados
    print(json.dumps(entitiesWithAttributes, indent=4, ensure_ascii=False))

# Ejemplo de texto a analizar
texto = """
Juan es acusado de un robo a mano armada y se encuentra en el artículo 234 del código penal.
La víctima sufrió daños debido al delito. Además, el acusado tiene antecedentes previos.
La víctima fue registrada en el número de atestado 1234 y su nombre es María.
"""

# Ontología en formato texto (como la proporcionaste)
ontology_text = """
Accused: Persona que es acusada de un delito.
ArmedRobbery: Un robo a mano armada.
Article234_1: El artículo 234, párrafo 1.
Article234_2: El artículo 234, párrafo 2.
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
num: Un número asociado a algo o alguien.
reportId: El identificador de un reporte.
"""