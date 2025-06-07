# ---- Preguntas para el modelo de clasificación de delitos ----

DELITO_CONTRA_PROPIEDAD = (
    "¿Se ha robado algo? Responde sí o no."
)

NUM_ATESTADO = (
    "¿Cuál es el identificador del atestado? "
    "Proporciónalo como texto (por ejemplo, 'AT20/20' o 'A2/21')."
)

NOMBRES_BIENES = (
    "¿Qué objeto o objetos han sido robado en total? Devuelve TODOS los objetos como una lista separada por comas "
    "(por ejemplo, 'libro, bici, reloj'). No incluyas información adicional, solo los nombres de los bienes. "
    "En caso de no saberse de manera individual pero sí en grupo, devolver el grupo como se especifique en el texto "
    "(por ejemplo: 'objetos variados', 'productos propios', ...)."
    "Si se roba una mochila, bolos o algo similar, devolver los bienes que contiene dentro. Si no se especifíca devolver el bien."
    "La lista no puede devolverse nunca vacía."
)

VICTIMAS_BIENES = (
    "¿A quién pertenecen los bienes robados? Proporciónalo como una lista separada por comas "
    "(por ejemplo, 'Juan Pérez, María López'). Ten en cuenta que puede haber más de un propietario del bien."
)

OTRAS_VICTIMAS = (
    "¿Hay alguna otra víctima aunque no le pertenezcan los bienes robados? Proporciónalo como una lista separada por comas "
    "(por ejemplo, 'Juan Pérez, María López'). Ten en cuenta que puede haber más de una."
)

ACUSADOS_BIENES = (
    "¿Quién es el acusado que ha robado los bienes sustraídos? Proporcióna sus identificadores como una lista separada por comas "
    "(por ejemplo, 'Juan Pérez, María López')."
)

ROBO_O_HURTO = (
    "¿Existe forzamiento para sustraer lo robado o el que sustrae realiza allanamiento de la casa o local o existe intimidación o violencia? "
    "Responde únicamente con sí o no."
)

HURTO_PROPIETARIO = (
    "¿El objeto o objetos sustraídos han sido robados o incitados a robar por su propio dueño aunque sean usados por otra persona? "
    "Responde con sí o no."
)

HURTO_NO_PROPIETARIO = (
    "¿El objeto sustraído se encontraba físicamente en posesión directa del propietario o almacenado en un lugar bajo su control, "
    "como su domicilio, local comercial o cualquier otro espacio de su propiedad hasta el momento del robo? "
    "Responde con 'sí' o 'no'."
)

DINERO_ROBADO = (
    "¿Cuál es la cantidad exacta de dinero en efectivo robada? "
    "Responde ÚNICAMENTE con un número decimal (por ejemplo: 500.0). No añadas texto, unidades ni explicaciones. "
    "Si no se ha robado dinero, responde con 0.0."
)

VALOR_ROBADO = (
    "¿Cuál es el valor económico estimado de los objetos robados (sin contar dinero en efectivo)? "
    "Responde ÚNICAMENTE con un número decimal (por ejemplo: 750.0). Si no hay objetos robados, responde con 0.0."
)

NEUTRALIZACION_ALARMAS = (
    "¿Se han neutralizado, eliminado o inutilizado los dispositivos de alarma o seguridad instalados para robar?"
    "Responde con sí o no."
)

CONDENAS_PREVIAS = (
    "¿{acusado} tiene más de 3 condenas previas? "
    "Responde con sí o no."
)

COMPLICE_MENOR = (
    "¿{acusado} tiene un cómplice menor de edad? "
    "Responde con sí o no."
)

EDAD_COMPLICES = (
    "¿Cuál es la edad del cómplice {complice}"
    "Responde con un número. Si no se especifica, responder 20"
)

ORGANIZACION_CRIMINAL = (
    "¿{acusado} pertenece a una organización criminal? "
    "Responde con sí o no."
)

NOMBRE_ORGANIZACION = (
    "¿Cuál es el nombre de la organización criminal a la que pertenece {acusado}? "
    "Proporciónalo como texto (por ejemplo, 'Los Zetas')."
)

ANTECEDENTES = (
    "¿{acusado} tiene antecedentes penales por robo? "
    "Responde con sí o no."
)

CANTIDAD_ANTECEDENTES = (
    "¿Cuántos antecedentes tiene el acusado {acusado}"
    "Responde con un número. Si no se especifíca responder 1."
)

DANIOS_GRAVES = (
    "¿Existen daños graves provocados por el robo?"
    "Responde con sí o no."
)

ROBO_CON_ARMA = (
    "¿Existe factor agravante de robo con arma? "
    "Responde con sí o no."
)

VIOLENCIA_ESCASA = (
    "¿Tiene atenuantes de violencia escasa o mínima? "
    "Responde con sí o no."
)

INTIMIDACION_VIOLENCIA = (
    "¿Hubo violencia, intimidación, agresión o amenaza hacia la víctima antes, durante o después del robo?\n\n"
    "La violencia se refiere al uso de fuerza física contra la víctima. "
    "La intimidación implica amenazas o acciones que generen miedo o coacción.\n\n"
    "Responde únicamente con 'sí' o 'no'. No añadas explicación."
)

ALLANAMIENTO = (
    "¿El acusado entró o permaneció contra la voluntad del titular en un domicilio, local o establecimiento?\n\n"
    "El allanamiento de morada implica acceder o permanecer en un domicilio particular, local de persona jurídica, oficina o establecimiento "
    "fuera del horario permitido o sin consentimiento.\n\n"
    "Responde únicamente con:\n"
    "- 'domicilio' si es un domicilio personal o fiscal,\n"
    "- el nombre del establecimiento si fue un local o tienda,\n"
    "- 'no' si no hubo allanamiento.\n\n"
    "No añadas explicación, solo responde con una de esas tres opciones."
)

ALLANAMIENTO_ESTABLECIMIENTO = (
    "¿El establecimiento {est} estaba abierto al público en el momento del delito?"
    "Responde sí o no."
)

FORZAMIENTO = (
    "¿El acusado utilizó fuerza o manipuló dispositivos de seguridad para acceder al lugar donde estaban los bienes?\n\n"
    "El forzamiento incluye romper o manipular cerraduras, candados, ventanas o puertas para acceder al lugar del robo.\n\n"
    "Responde únicamente con 'sí' o 'no'. No añadas explicación."
)

IMPACTO_ECONOMICO = (
    "¿El robo ha tenido un impacto económico significativo en la víctima {victima}? "
    "El impacto económico significativo se refiere a una pérdida económica que afecta de manera considerable "
    "la estabilidad financiera de la víctima, como la pérdida de bienes esenciales, herramientas de trabajo, "
    "o una cantidad de dinero que represente una parte importante de sus ingresos o ahorros. "
    "Responde con sí o no."
)

VULNERABILIDAD = (
    "¿Ha habido una situación de vulnerabilidad para la víctima {victima}? "
    "La vulnerabilidad se refiere a una condición en la que la víctima se encuentra en desventaja o incapacidad "
    "para defenderse debido a factores como edad, discapacidad, enfermedad, o cualquier otra circunstancia que limite "
    "su capacidad de reacción o resistencia. "
    "Responde con sí o no."
)

DANIOS_FISICO_PSICOLOGICOS = (
    "¿Se han producido daños físicos o psicológicos a la víctima {victima}? "
    "Los daños físicos se refieren a lesiones corporales, heridas, o cualquier afectación a la integridad física de la víctima. "
    "Los daños psicológicos incluyen traumas emocionales, estrés postraumático, ansiedad, o cualquier afectación al bienestar mental "
    "de la víctima como resultado del incidente. "
    "Responde con sí o no."
)

BIEN_AGRICOLA = (
    "¿El bien robado {bien} es un bien agrícola? "
    "Un bien agrícola se refiere a productos obtenidos directamente de la agricultura, como frutas, verduras, cereales, "
    "semillas, plantas, o cualquier otro recurso cultivado en el campo. "
    "Responde con sí o no."
)

BIEN_ARTISTICO = (
    "¿El bien robado {bien} es un bien con valor artístico? "
    "Un bien con valor artístico se refiere a obras de arte como pinturas, esculturas, grabados, fotografías, "
    "o cualquier objeto creado con intención estética o expresiva. "
    "Responde con sí o no."
)

BIEN_CULTURAL = (
    "¿El bien robado {bien} es un bien con valor cultural? "
    "Un bien con valor cultural se refiere a objetos que representan la identidad, historia, tradiciones o patrimonio "
    "de una comunidad o sociedad, como libros antiguos, manuscritos, o piezas arqueológicas. "
    "Responde con sí o no."
)

BIEN_ESENCIAL = (
    "¿El bien robado {bien} es un bien de primera necesidad que cause desabastecimiento a la víctima? "
    "Un bien de primera necesidad se refiere a productos esenciales para la vida diaria, como alimentos, medicamentos, "
    "ropa básica, o cualquier otro recurso indispensable para la subsistencia. "
    "Responde con sí o no."
)

BIEN_HISTORICO = (
    "¿El bien robado {bien} es un bien con valor histórico? "
    "Un bien con valor histórico se refiere a objetos que tienen importancia en la historia debido a su antigüedad, "
    "relevancia en eventos pasados, o conexión con figuras históricas, como documentos antiguos, reliquias, o monumentos. "
    "Responde con sí o no."
)

BIEN_CIENTIFICO = (
    "¿El bien robado {bien} es un bien con valor científico? "
    "Un bien con valor científico se refiere a objetos utilizados para la investigación, experimentación, o avance del conocimiento, "
    "como equipos de laboratorio, especímenes biológicos, o instrumentos tecnológicos. "
    "Responde con sí o no."
)

BIEN_SERVICIOS = (
    "¿El bien robado {bien} es un bien destinado a la prestación de servicios de interés general? "
    "Un bien destinado a la prestación de servicios de interés general se refiere a recursos utilizados para actividades "
    "que benefician a la comunidad, como vehículos de transporte público, equipos médicos, o infraestructura de servicios básicos. "
    "Responde con sí o no."
)

# ---- Preguntas extras que facilitaran datos ----

PROPIETARIO_ESPECIFICO = (
    "¿La persona identificada como {persona} es el propietario legítimo del bien identificado como {bien}? "
    "Responde únicamente con 'sí' o 'no'."
)

PROPIETARIO_GENERAL = (
    "¿Quién es el propietario legítimo del bien identificado como {bien}? "
    "Proporciónalo con el identificador único del propietario (por ejemplo, 'Juan Pérez' o 'Empresa XYZ'). "
    "Si no se conoce, responde con 'Desconocido'."
)

USUARIO = (
    "¿Quién es el usuario del bien '{bien}'? Responde con el identificador del usuario."
    "Si el bien o los bienes pertenecen a una empresa, el usuario es la empresa." \
    "Por ejemplo, si se ha robado una pizza en Mercadona, el usuario es mercadona, si se han robado objetos de Ikea, el usuario es Ikea."
    "Si no se especifica, responde 'Ninguno' o 'No hay'."
)

TESTIGOS = (
    "¿Hay testigos en el atestado?"
    "Si los hay responde con una lista de identificadores de testigos (por ejemplo 'Juan López, María Pérez')"
    "Si no hay devolver 'No'"
)

EMPRESAS = (
    "¿Hay empresas involucradas en el robo en relación a los bienes robados?"
    "Si los hay responde con una lista de identificadores de empresas (por ejemplo 'Mercadona, Concesionario Toyota')"
    "Si no hay devolver 'No'"
)

COMPLICES = (
    "¿Hay cómplices en el atestado?"
    "Si los hay responde con una lista de identificadores de cómplices (por ejemplo 'Juan López, María Pérez')"
    "Si no hay devolver 'No'"
)

ES_DINERO = (
    "¿El bien {bien} es dinero en efectivo o una cantidad numérica de dinero explícita?"
    "Responde con sí o no."
)

MISMA_PERSONA = (
    "¿La persona {p1} se refiere a la misma persona que {p2}?"
    "Responde sí o no"
)

MISMA_EMPRESA = (
    "¿La empresa {p1} se refiere a la misma empresa que {p2}?"
    "Responde sí o no."
)