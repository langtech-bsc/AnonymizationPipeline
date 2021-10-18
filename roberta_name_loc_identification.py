# This file will perform the location and name identification using the ROBERTa model we've trained. 

# The idea is to perform NER over the conll of the previous part of the pipeline and then to add only the PER and the LOC tags to the resulting file. 

from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer




# text = "Hola Marta, me esta funcionando mal el telefono. Mi numero es 617761843 y me encuentro en Carrer del Cent 65, 08014, Barcelona, Espana. Deberia llamar o quieres que te pase mis datos bancarios? juanCa_selsen@outlook.org es mi corre y luego ES21 2100 2527 33 1234567890 es la cuenta. Buenos día a todos. Hoy vamos a estar trabajando en un proyecto de Integración entre todos. Nos reuniremos en el café Batac en Calle de Aragón 34, a las 17:35. Marc y Joan no se si van a estar leyendo esto o no, pero les dejo un mensaje y sus DNIs aquí por si las dudas. Y3364793V y A7484842Z."*4

# result = pipe(text)

# persons_and_locations = [e for e in result if ('PER' in e['entity'] or 'LOC' in e['entity'])]


# TODO: Things that I need to do
#   - Think about what to do if the text is longer than 512 tokens because it doesn't predict anything from there onwards. 


# for entity in persons_and_locations:
#     print(entity)

def identifyNames(text, model="BSC-TeMU/roberta-base-bne-capitel-ner-plus"):
    pipe = pipeline("ner", model="BSC-TeMU/roberta-base-bne-capitel-ner-plus", tokenizer="BSC-TeMU/roberta-base-bne-capitel-ner-plus")
    ner_result = pipe(text)

    sensitive_entities = [e for e in ner_result if ('PER' in e['entity'] or 'LOC' in e['entity'])]
    
    return BIOConllToJsonl(sensitive_entities, text)

def BIOConllToJsonl(bioEntities, original_text):
    entities = []
    index = 0
    while index < len(bioEntities):
        tag = bioEntities[index]['entity']
        start = bioEntities[index]['start']
        end = bioEntities[index]['end']
        # text = original_text[start:end]
        if tag[0] == 'B' :
            while(index + 1 < len(bioEntities) and (bioEntities[index + 1]['entity'][0] == 'B')):
                end = bioEntities[index + 1]['end']
                index +=1
        while(index + 1 < len(bioEntities) and (bioEntities[index + 1]['entity'][0] in ['I', 'E'])):
            end = bioEntities[index + 1]['end']
            index +=1
        text = original_text[start:end]
        entities.append({'tag': tag[2:], 'span':(start, end), 'text': text})
        index += 1
    
    return entities

# BIOConllToJsonl(persons_and_locations, text)