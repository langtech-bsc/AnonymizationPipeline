from __future__ import annotations

from sensitive_identifier import SensitiveIdentifier
from formatters import Registry

from transformers import pipeline
import spacy


class RoBERTaNameIdentifier(SensitiveIdentifier):
    def __init__(self, model="BSC-TeMU/roberta-base-bne-capitel-ner-plus") -> None:
        super().__init__()
        self._pipe = pipeline("ner", model=model, tokenizer=model, use_auth_token=True)

    def identify_sensitive(self, registry: Registry) -> None:
        text = registry.text

        ner_result = self._pipe(text)

        sensitive_entities = [e for e in ner_result if ('PER' in e['entity'] or 'LOC' in e['entity'])]
        
        jsonl_format = BIOConllToJsonl(sensitive_entities, text)

        for match in jsonl_format:
            registry.add_span({"start": match["span"][0], "end":match["span"][1], "label":match["tag"], "rank":3})


def BIOConllToJsonl(bioEntities, original_text):
    #TODO: Review
    entities = []
    index = 0
    while index < len(bioEntities):
        tag = bioEntities[index]['entity']
        start = bioEntities[index]['start']
        end = bioEntities[index]['end']

        if tag[0] == 'B' :
            while(index + 1 < len(bioEntities) and (bioEntities[index + 1]['entity'] == tag) and bioEntities[index + 1]['start'] == (end)):
                end = bioEntities[index + 1]['end']
                index +=1
        while(index + 1 < len(bioEntities) and (bioEntities[index + 1]['entity'][0] in ['I', 'E'])):
            end = bioEntities[index + 1]['end']
            index +=1
        text = original_text[start:end]
        entities.append({'tag': tag[2:], 'span':(start, end), 'text': text})
        index += 1
    
    return entities

class SpacyIdentifier(SensitiveIdentifier):
    def __init__(self, path_to_model="xitxat_anonym/model_xit_xat_PER_LOC") -> None:
        super().__init__()
        self._pipe = spacy.load(path_to_model)
    
    @property
    def label_map(self):
        return {
            "name" : "PER"
            , "surname" : "PER"
            , "surname2" : "PER"
            , "address" : "LOC"
            }

    def identify_sensitive(self, registry: Registry) -> None:
        text = registry.text
        doc = self._pipe(text)
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
            registry.add_span({"start": ent.start_char, "end": ent.end_char, "label": self.label_map[ent.label_] if ent.label_ in self.label_map else "OTHER", "rank": 0})
