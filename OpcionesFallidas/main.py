def forma1():
    texto_atestado = documents.lectura()
    entities, relations, attributes = ontologyToNL.ontology_processing()
    ontologyExtractBySteps.ontologyData(entities,attributes, texto_atestado)

def forma2():
    texto_atestado = documents.lectura()
    entities, relations, attributes = ontologyToNL.ontology_processing()
    ontologyExtractByStepsSP.ontologyData(entities,attributes, texto_atestado)

def forma3():
    texto_atestado = documents.lectura()
    entities, relations, attributes = ontologyToNLSP.ontology_processing()
    ontologyExtractBySteps.ontologyData(entities,attributes, texto_atestado)

def forma4():
    texto_atestado = documents.lectura()
    entities, relations, attributes = ontologyToNLSP.ontology_processing()
    ontologyExtractByStepsSP.ontologyData(entities,attributes, texto_atestado)

def forma5():
    texto_atestado = documents.lectura()
    entities, relations, attributes = ontologyAnalizer.ontology_analysis_with_gemini()
    ontologyExtractBySteps.ontologyData(entities,attributes, texto_atestado)

def forma6():
    texto_atestado = documents.lectura()
    entities, relations, attributes = ontologyAnalizer.ontology_analysis_with_gemini()
    ontologyExtractByStepsSP.ontologyData(entities,attributes, texto_atestado)