import google.generativeai as genai # type: ignore
import json
import re

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/javiertorrecilla/Desktop/UMA/TFG/herramientaJuridica/.env")

apiKey = os.getenv("api_key")
url = os.getenv("base_url")

genai.configure(api_key=apiKey)

# System Prompt Mejorado
system_prompt = """
Eres un asistente experto en el análisis de textos legales. Tu tarea es procesar documentos legales proporcionados, identificar entidades clave (como personas, artículos de ley, etc.), y asociarlas con sus atributos correspondientes según las definiciones proporcionadas.
Para llevar a cabo esta tarea, se te proporcionará una ontología que describe las entidades y sus significados, así como un listado de atributos que se pueden asociar con dichas entidades. Debes ser extremadamente preciso en tu análisis y debes seguir estrictamente las reglas que se te proporcionen para la extracción y asociación de datos.
Es importante que comprendas cómo se definen las entidades y qué atributos son relevantes para cada una de ellas. No debes agregar ninguna entidad o atributo que no esté presente en el texto. En caso de duda, asegúrate de seguir las reglas de asociación de atributos y de evitar duplicados.
Las respuestas deben ser presentadas de manera clara, estructurada y en formato JSON, como se describe a continuación:
"""

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
    
    # Crear el prompt para Gemini AI para buscar las entidades y atributos en el texto
    extract_entities_prompt = f"""
    {system_prompt}
    A continuación se presenta un listado de las entidades con sus definiciones. Tu tarea es identificar las entidades que aparecen en el siguiente texto, asociándolas con sus definiciones. Asegúrate de seguir estas reglas:

    1. Identificación única: Cada entidad que se mencione en el texto debe ser identificada solo una vez, aunque aparezca múltiples veces.
    2. Agrupación de sinónimos: Si una entidad se menciona de diferentes maneras (por ejemplo, "Juan" y "el acusado"), agrúpalas bajo la misma entidad.
    3. Entidades distintas: Si el texto menciona varias instancias de una entidad (por ejemplo, múltiples acusados), identifica cada instancia como una entidad separada con un identificador único.
    4. No agregar entidades no mencionadas: Solo incluye las entidades que realmente aparecen en el texto.
    5. Formato de salida: Las entidades deben ser devueltas en formato JSON con las claves "entity" y "id" (si es necesario) para cada entidad identificada.

    Listado de entidades y definiciones:
    {json.dumps(ontology_dict, ensure_ascii=False, indent=4)}

    Texto a analizar:
    {text}
    """
    
    # Generamos la respuesta con Gemini AI
    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(extract_entities_prompt)
    
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
    
    associate_attributes_prompt = f"""
    {system_prompt}

    A continuación se presenta un listado de las entidades detectadas en el texto, junto con sus posibles atributos asociados. Tu tarea es asociar cada entidad con los atributos válidos, siguiendo las siguientes reglas:

    1. Solo atributos válidos: Asegúrate de asociar solo los atributos que corresponden a cada entidad. Por ejemplo, si la entidad es "Victim", atributos como "Name" y "Age" pueden ser válidos, pero "num" no lo es.
    2. Evitar duplicados: Si un atributo ya ha sido asociado a una entidad, no lo repitas en la misma respuesta.
    3. Entidades sin atributos: Si una entidad está presente pero no tiene atributos asociados en el texto, inclúyela con un valor vacío para los atributos.
    4. Formato de salida: El formato de salida debe ser un JSON con la entidad y un objeto que contenga los atributos correspondientes, incluso si están vacíos.

    Listado de entidades detectadas y sus atributos válidos:
    {json.dumps(detected_entities, ensure_ascii=False, indent=4)}

    Listado de atributos:
    {json.dumps(attributes_dict, ensure_ascii=False, indent=4)}
    """
    
    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(associate_attributes_prompt)
    response_text = response.text.strip()
    cleaned_response = response_text.replace("```json", "").replace("```", "").strip()

    try:
        json_data = json.loads(cleaned_response)
        return json_data
    except json.JSONDecodeError:
        return {"error": "No se pudo procesar la respuesta correctamente."}
    
def extract_attributes(text, entity_attribute_mapping):
    """Extraer los atributos del texto, asegurándose de que coincidan con las entidades detectadas."""
    
    extract_attributes_prompt = f"""
    {system_prompt}
    
    A continuación se presenta un listado de las entidades con sus atributos válidos. Tu tarea es extraer los valores de los atributos mencionados en el texto, siguiendo estas reglas:

    1. Solo atributos mencionados: Extrae solo los atributos que están explícitamente mencionados en el texto.
    2. Formato consistente: Cada atributo extraído debe ser asociado con la entidad correspondiente.
    3. Entidades sin atributos: Si una entidad no tiene atributos mencionados, inclúyela en la salida con atributos vacíos.
    4. Evitar duplicados: Si un atributo ya ha sido asociado a una entidad, no lo repitas en la misma salida.
    5. Formato de salida: La salida debe ser un JSON estructurado con las entidades y los atributos extraídos de acuerdo con las reglas indicadas.

    Listado de entidades con sus atributos válidos:
    {json.dumps(entity_attribute_mapping, ensure_ascii=False, indent=4)}

    Texto a analizar:
    {text}
    """

    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(extract_attributes_prompt)
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

def main():

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

    entities_dict = parse_ontology(ontology_text)
    attributes_dict = parse_ontology(generic_attributes)
    entities = extract_entities(texto, entities_dict)
    entity_attribute_mapping = associate_attributes_with_detected_entities(entities, attributes_dict)
    attributes = extract_attributes(texto, entity_attribute_mapping)

    print(json.dumps(entities, indent=4, ensure_ascii=False))
    print(json.dumps(entity_attribute_mapping, indent=4, ensure_ascii=False))
    print(json.dumps(attributes, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
