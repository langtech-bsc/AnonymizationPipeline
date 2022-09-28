from __future__ import annotations

# This file will contain the formatters for the jsonl files. 

from abc import ABC, abstractmethod
import json
from typing import List, Optional
from anonymize import Anonymizer, anonymizeSpans
from meta import Span
from tqdm import tqdm



class Registry(ABC):

    def __init__(self, index : str, text : str, spans : List[Span], meta : dict) -> None:
        super().__init__()
        self._index = index
        self._text = text
        self._spans : List[Span] = []
        for span in spans:
            self.add_span(span)
        self._meta = meta

    @classmethod
    @abstractmethod
    def factory(cls, r : dict) -> Registry:
        pass
    
    @property
    def index(self) -> str:
        return self._index
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, value : str) -> None:
        self._text = value

    @property
    def spans(self) -> List[Span]:
        return self._spans

    @spans.setter
    def spans(self, spans : List[Span]) -> None:
        self._spans = spans

    @property
    def meta(self) -> dict:
        return self._meta

    @abstractmethod
    def toString(self) -> str:
        pass

    def update(self, r : Registry) -> None:
        self._index = r.index
        self._text = r.text
        self._spans = r.spans
        self._meta = r.meta
    
    def add_span(self, span : Span, label_list : Optional[List[str]] = None) -> None:
        if label_list and span["label"] not in label_list:
            return # No need to add the span because it is not in the list of labels we want to keep
        # Adding the span and keeping the list sorted
        index = 0
        while index < len(self.spans):
            if self.spans[index]["start"] > span["start"]:
                self.spans.insert(index,span)
                break
            else:
                index+=1
        
        if index == len(self.spans):
            self.spans.append(span)

        # Solving overlap between spans
        new_spans : List[Span] = []
        new_spans.append(self.spans.pop(0))
        while len(self.spans) > 0:
            current = new_spans[-1]
            top = self.spans[0]
            if top["start"] >= current["end"]:
                new_spans.append(top)
            elif top["end"] > current["end"]:
                current.update({"end":top["end"]})
                if current['rank'] < top["rank"]:
                    current.update({"rank":top["rank"], "label":top["label"]})
            self.spans.pop(0)

        self._spans = new_spans
        
class ProdigyRegistry(Registry):
    def __init__(self, index: str, text: str, spans: List[Span], meta: dict) -> None:
        super().__init__(index, text, spans, meta)
    
    def toString(self) -> str:
        return json.dumps({"text": self.text, "spans": self.spans, "meta": self.meta}, ensure_ascii=False) + "\n"
    
    @classmethod
    def factory(cls, r: dict) -> Registry:
        spans = list(map(lambda s: Span(start=s["start"],end=s["end"],label=s["label"], rank=s["rank"] if "rank" in s else 0), r["spans"]))
        return cls(r['meta']['ID'], r['text'], spans, r['meta'])

class SpacyRegistry(Registry):
    def __init__(self, index: str, text: str, spans: List[Span], meta: dict) -> None:
        super().__init__(index, text, spans, meta)

    def toString(self) -> str:
        return json.dumps({"text": self.text, "ents": self.spans, "meta": self.meta}, ensure_ascii=False) + "\n"

    @classmethod
    def factory(cls, r: dict) -> Registry:
        ents = list(map(lambda s: Span(start=s["start"],end=s["end"],label=s["label"], rank=s["rank"] if "rank" in s else 0), r["ents"]))
        return cls("0", r['text'], ents, {})
    

class PlainRegistry(Registry):
    def __init__(self, index: str, text: str, spans: List[Span], meta: dict) -> None:
        super().__init__(index, text, spans, meta)
    
    def toString(self) -> str:
        return json.dumps({"text": self.text, "spans": self.spans, "meta": self.meta}, ensure_ascii=False) + "\n"

    @classmethod
    def factory(cls, r: dict) -> Registry:
        text = r['text']
        index = r['index']
        return cls(index, text, [], {})
    

class DocannoRegistry(Registry):
    def __init__(self, index: str, text: str, spans: List[Span], meta: dict) -> None:
        super().__init__(index, text, spans, meta)
    
    def toString(self) -> str:
        spans = list(map(lambda x: (x['start'], x['end']), self.spans))
        return json.dumps({"text": self.text, "spans": spans}, ensure_ascii=False) + "\n"

    @classmethod
    def factory(cls, r: dict) -> DocannoRegistry:
        return cls(r['index'], r['text'], r['labels'], r['meta'])

class StreamIngester():
    def __init__(self, text : str) -> None:
        self.registry : Registry = SpacyRegistry.factory({"text": text, "ents": []})

    def ingest_text(self, new_text):
        self.registry = SpacyRegistry.factory({"text": new_text, "ents": []})

    def anonymize_registries(self, anonymizer : Anonymizer):
        new_spans, new_text = anonymizeSpans(anonymizer, self.registry.spans, self.registry.text)
        self.registry.text = new_text
        self.registry.spans = new_spans


class Formatter(ABC):

    def __init__(self, input_file : str) -> None:
        super().__init__()
        self.registries : List[Registry] = []
        self.read_file(input_file)

    @classmethod
    @abstractmethod
    def registryFactory(cls, line : str) -> Registry:
        pass

    def read_file(self, input_path) -> None:
        #TODO: Think if the formatter should read all lines or process them in batches (low memory resources)
        with open(input_path, "r") as f:
            for line in tqdm(f, "Ingesting registries", total=sum(1 for line in open(input_path, "r"))):
                reg = self.registryFactory(line)
                self.registries.append(reg)
    
    def anonymize_registries(self, anonymizer : Anonymizer):
        for registry in tqdm(self.registries, "Anonymizing Registries", total=len(self.registries)):
            new_spans, new_text = anonymizeSpans(anonymizer, registry.spans, registry.text)
            registry.text = new_text
            registry.spans = new_spans

    def save(self, output_path) -> None:
        with open(output_path, "w") as o:
            for reg in tqdm(self.registries, "Saving Registries", total=len(self.registries)):
                o.write(reg.toString())

class ProdigyFormatter(Formatter):
    def __init__(self, input_file) -> None:
        super().__init__(input_file)
    
    @classmethod
    def registryFactory(cls, line: str) -> Registry:
        return ProdigyRegistry.factory(json.loads(line))
    

class PlainTextFormatter(Formatter):
    index = 0
    def __init__(self, input_file: str) -> None:
        super().__init__(input_file)
        self.index = 0

    @classmethod
    def registryFactory(cls, line: str) -> Registry:
        cls.index = cls.index + 1
        return PlainRegistry.factory({"index":cls.index, "text":line})

    

class DocannoFormatter:
    #TODO: Program
    pass


