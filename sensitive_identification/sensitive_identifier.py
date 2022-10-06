from __future__ import annotations
from abc import ABC, abstractmethod
from tokenize import String
from typing import Iterable, List, Optional

from ingestors import Registry
from meta import Span

class SensitiveIdentifier(ABC):
    
    def __init__(self, label_list : Optional[List[str]] = None) -> None:
        super().__init__()
        self._label_list = label_list

    def identify_sensitive(self, registry : Registry) -> None:
        text = registry.text
        spans = self._get_sensitive_spans(text)
        for span in spans:
            registry.add_span(span, self._label_list)

    @abstractmethod
    def get_labels(self) -> Iterable[str]:
        pass

    @abstractmethod
    def _get_sensitive_spans(self, text : str) -> List[Span]:
        #TODO: Think if this should be an Iterable to use yield instead of List
        pass
    