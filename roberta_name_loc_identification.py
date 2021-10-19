from transformers import pipeline



# TODO: Things that I need to do
#   - Think about what to do if the text is longer than 512 tokens because it doesn't predict anything from there onwards. 

class ROBERTaNameIdentifier :

    def __init__(self, model="BSC-TeMU/roberta-base-bne-capitel-ner-plus") -> None:
        self.pipe = pipeline("ner", model=model, tokenizer=model)

    def identifyNames(self, text, ):
        
        ner_result = self.pipe(text)

        sensitive_entities = [e for e in ner_result if ('PER' in e['entity'] or 'LOC' in e['entity'])]
        
        return BIOConllToJsonl(sensitive_entities, text)


def BIOConllToJsonl(bioEntities, original_text):
    entities = []
    index = 0
    while index < len(bioEntities):
        tag = bioEntities[index]['entity']
        start = bioEntities[index]['start']
        end = bioEntities[index]['end']

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
