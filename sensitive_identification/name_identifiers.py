from __future__ import annotations
from typing import Iterable, List, Optional, Set
from meta import Span

from .sensitive_identifier import SensitiveIdentifier

from transformers import pipeline
import spacy


class RoBERTaNameIdentifier(SensitiveIdentifier):
    def __init__(self, model="BSC-TeMU/roberta-base-bne-capitel-ner-plus", label_list : Optional[List[str]] = None) -> None:
        super().__init__(label_list)
        self._pipe = pipeline("ner", model=model, tokenizer=model, use_auth_token=True)

    def _get_sensitive_spans(self, text : str) -> List[Span]:

        ner_result = self._pipe(text.strip())
        sensitive_entities = [e for e in ner_result if ('PER' in e['entity'] or 'LOC' in e['entity'])]
        # we define a sensitive entity as information that fully allows identification of an individual
        # i.e. any full name, or complete location (i.e. a full address)

        jsonl_format = BIOConllToJsonl(sensitive_entities, text)
        json_persons = [e for e in jsonl_format if e['tag'] == 'PER' and len(e['text'].split()) > 1]
        json_locations = [e for e in jsonl_format if e['tag'] == 'LOC']
        jsonl_format = json_persons + json_locations
        return [{"start": match["span"][0], "end":match["span"][1], "label":match["tag"], "rank":2} for match in jsonl_format]
    
    def get_labels(self) -> Iterable[str]:
        labels : Set[str] = set([label[2:] for label in self._pipe.model.config.label2id.keys() if label != "O"])
        return labels
        

def BIOConllToJsonl(bioEntities, original_text):
    entities = []
    index = 0
    punct = [' ', ',', '.', '!', '?', '\"', "'"]
    while index < len(bioEntities):
        tag = bioEntities[index]['entity']
        start = bioEntities[index]['start']
        end = bioEntities[index]['end']
        if tag[0] in ['B', 'S']:
            while(index + 1 < len(bioEntities) and (bioEntities[index + 1]['entity'] == tag) and bioEntities[index + 1]['start'] == (end)):
                end = bioEntities[index + 1]['end']
                index +=1

        while(index + 1 < len(bioEntities) and (bioEntities[index + 1]['entity'][0] in ['I', 'E'])):
            end = bioEntities[index + 1]['end']
            index +=1
        while end < len(original_text) and original_text[end] not in punct:
            end += 1
        text = original_text[start:end]
        entities.append({'tag': tag[2:], 'span':(start, end), 'text': text})
        index += 1
    
    return entities

class SpacyIdentifier(SensitiveIdentifier):
    def __init__(self, path_to_model : str, label_list : Optional[List[str]] = None) -> None:
        super().__init__(label_list)
        self._pipe = spacy.load(path_to_model)
    
    @property
    def label_map(self):
        return {
            "name" : "PER"
            , "surname" : "PER"
            , "surname2" : "PER"
            , "address" : "LOC"
            , "PER" : "PER"
            , "LOC" : "LOC"
            }

    def _get_sensitive_spans(self, text : str) -> List[Span]:
        
        doc = self._pipe(text)
        
        return [{"start": ent.start_char, "end": ent.end_char, "label": self.label_map[ent.label_] if ent.label_ in self.label_map else ent.label_, "rank": 0} for ent in doc.ents]

    def get_labels(self) -> Iterable[str]:
        return self._pipe.get_pipe("ner").labels
        
